from __future__ import annotations

import io
import os
import threading
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from types import SimpleNamespace
from typing import Any, Iterator

_MISSING = object()
_GLOBAL_PATCH_LOCK = threading.RLock()


class MiniMonkeyPatch:
    def __init__(self) -> None:
        self._undo: list[tuple[str, Any, Any, Any]] = []

    @contextmanager
    def context(self) -> Iterator[MiniMonkeyPatch]:
        with _GLOBAL_PATCH_LOCK:
            mark = len(self._undo)
            try:
                yield self
            finally:
                while len(self._undo) > mark:
                    mode, obj, key, old = self._undo.pop()
                    if mode == "attr":
                        if old is _MISSING:
                            delattr(obj, key)
                        else:
                            setattr(obj, key, old)
                    elif mode == "item":
                        if old is _MISSING:
                            del obj[key]
                        else:
                            obj[key] = old
                    elif mode == "env":
                        if old is _MISSING:
                            os.environ.pop(key, None)
                        else:
                            os.environ[key] = old

    def setattr(self, obj: Any, name: str, value: Any) -> None:
        old = getattr(obj, name, _MISSING)
        self._undo.append(("attr", obj, name, old))
        setattr(obj, name, value)

    def setitem(self, mapping: Any, key: Any, value: Any) -> None:
        old = mapping[key] if key in mapping else _MISSING
        self._undo.append(("item", mapping, key, old))
        mapping[key] = value

    def setenv(self, name: str, value: str) -> None:
        old = os.environ[name] if name in os.environ else _MISSING
        self._undo.append(("env", None, name, old))
        os.environ[name] = value

    def delenv(self, name: str, raising: bool = True) -> None:
        if name not in os.environ:
            if raising:
                raise KeyError(name)
            return
        old = os.environ[name]
        self._undo.append(("env", None, name, old))
        del os.environ[name]


class MiniCapsys:
    def __init__(self) -> None:
        self._stdout = io.StringIO()
        self._stderr = io.StringIO()

    @contextmanager
    def capture(self) -> Iterator[None]:
        self._stdout = io.StringIO()
        self._stderr = io.StringIO()
        with redirect_stdout(self._stdout), redirect_stderr(self._stderr):
            yield

    def readouterr(self) -> SimpleNamespace:
        out = self._stdout.getvalue()
        err = self._stderr.getvalue()
        self._stdout.seek(0)
        self._stdout.truncate(0)
        self._stderr.seek(0)
        self._stderr.truncate(0)
        return SimpleNamespace(out=out, err=err)
