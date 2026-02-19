import builtins
import io
import os
import sys
import types
import importlib
import threading

from spec_runner.assertions import (
    assert_stdout_path_exists,
    first_nonempty_line,
)
from spec_runner.assertion_health import (
    format_assertion_health_error,
    format_assertion_health_warning,
    lint_assert_tree,
    resolve_assert_health_mode,
)
from spec_runner.compiler import compile_external_case
from spec_runner.components.assertion_engine import run_assertions_with_context
from spec_runner.components.execution_context import build_execution_context
from spec_runner.components.meta_subject import build_meta_subject
from spec_runner.components.subject_router import resolve_subject_for_target
from spec_runner.settings import SETTINGS


_GLOBAL_SIDE_EFFECT_LOCK = threading.RLock()


def _runtime_env(ctx) -> dict[str, str]:
    raw_env = getattr(ctx, "env", None)
    if raw_env is None:
        return dict(os.environ)
    return {str(k): str(v) for k, v in raw_env.items()}


def _is_safe_mode_enabled(runtime_env: dict[str, str]) -> bool:
    raw = str(runtime_env.get(SETTINGS.env.safe_mode, "")).strip().lower()
    return raw in {"1", "true", "yes", "on"}


def _load_entrypoint(ep: str):
    """
    Load a call target from an entrypoint-like string: "module.sub:func".
    """
    if ":" not in ep:
        raise ValueError(f"invalid entrypoint (expected module:attr): {ep}")
    mod_name, attr = ep.split(":", 1)
    mod_name = mod_name.strip()
    attr = attr.strip()
    if not mod_name or not attr:
        raise ValueError(f"invalid entrypoint (expected module:attr): {ep}")
    try:
        mod = importlib.import_module(mod_name)
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(f"entrypoint module not found: {mod_name}") from e
    except ImportError as e:
        raise ImportError(f"failed to import entrypoint module: {mod_name}") from e
    fn = getattr(mod, attr, None)
    if fn is None:
        raise AttributeError(f"entrypoint attribute not found: {ep}")
    if not callable(fn):
        raise TypeError(f"entrypoint is not callable: {ep}")
    return fn


def run(case, *, ctx) -> None:
    hook_case = case
    if hasattr(case, "test") and hasattr(case, "doc_path"):
        case = compile_external_case(case.test, doc_path=case.doc_path)
    t = case.raw_case
    case_id = case.id
    h = case.harness

    supported_harness_keys = {
        "entrypoint",
        "env",
        "stdin_isatty",
        "stdin_text",
        "block_imports",
        "stub_modules",
        "setup_files",
        "hook_before",
        "hook_after",
        "hook_kwargs",
        "spec_lang",
    }
    unknown = sorted(str(k) for k in h.keys() if k not in supported_harness_keys)
    if unknown:
        raise ValueError(f"unsupported harness key(s): {', '.join(unknown)}")

    forbidden_top_level_keys = {
        "stub_modules",
        "setup_files",
        "stdin_text",
        "stdin_isatty",
        "block_imports",
    }
    found_forbidden = sorted(k for k in forbidden_top_level_keys if k in t)
    if found_forbidden:
        raise ValueError(f"move harness-only keys under 'harness:': {', '.join(found_forbidden)}")

    argv = t.get("argv", [])
    if isinstance(argv, str):
        argv = [argv]
    argv = [str(a) for a in (argv or [])]

    # Optional hooks for complex setup/assertions.
    hook_kwargs = h.get("hook_kwargs") or {}
    if not isinstance(hook_kwargs, dict):
        raise TypeError("harness.hook_kwargs must be a mapping")

    hook_before_ep = h.get("hook_before")
    hook_after_ep = h.get("hook_after")

    if hook_before_ep is not None and not str(hook_before_ep).strip():
        hook_before_ep = None
    if hook_after_ep is not None and not str(hook_after_ep).strip():
        hook_after_ep = None

    runtime_env = _runtime_env(ctx)
    case_key = f"{case.doc_path.resolve().as_posix()}::{case_id}"
    chain_imports = dict(ctx.get_case_chain_imports(case_key=case_key))
    chain_payload = dict(ctx.get_case_chain_payload(case_key=case_key))
    execution = build_execution_context(
        case_id=case_id,
        case_type=case.type,
        harness={**h, "_chain_imports": chain_imports},
        doc_path=case.doc_path,
    )
    safe_mode = _is_safe_mode_enabled(runtime_env)

    with _GLOBAL_SIDE_EFFECT_LOCK:
        with ctx.patch_context() as mp:
            # Runner-provided setup features. These are deliberately small and generic
            # to avoid hook proliferation for common cases.
            stub_modules = h.get("stub_modules") or []
            if isinstance(stub_modules, str):
                stub_modules = [stub_modules]
            for name in [str(x).strip() for x in stub_modules if str(x).strip()]:
                if name in sys.modules:
                    continue
                if name == "openai":
                    mp.setitem(sys.modules, "openai", types.SimpleNamespace(OpenAI=object))
                else:
                    mp.setitem(sys.modules, name, types.SimpleNamespace())

            setup_files = h.get("setup_files") or []
            if isinstance(setup_files, dict):
                setup_files = [setup_files]
            if setup_files:
                if not isinstance(setup_files, list):
                    raise TypeError("setup_files must be a list (or mapping for a single file)")
                tmp_root = ctx.tmp_path.resolve()
                for item in setup_files:
                    if not isinstance(item, dict):
                        raise TypeError("setup_files item must be a mapping")
                    rel = item.get("path")
                    if not rel:
                        raise ValueError("setup_files item missing required key: path")
                    text = item.get("text", "")
                    from pathlib import Path

                    rel_p = Path(str(rel)).expanduser()
                    if rel_p.is_absolute():
                        raise ValueError("setup_files item path must be relative")
                    p = (tmp_root / rel_p).resolve()
                    try:
                        p.relative_to(tmp_root)
                    except ValueError as e:
                        raise ValueError("setup_files item path escapes tmp_path") from e
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_text(str(text), encoding="utf-8")

            harness_env_raw = h.get("env") or {}
            harness_env: dict[str, object] = {}
            if harness_env_raw:
                if not isinstance(harness_env_raw, dict):
                    raise TypeError("harness.env must be a mapping")
                harness_env = {str(k): v for k, v in harness_env_raw.items()}
                for k, v in harness_env.items():
                    if v is None:
                        mp.delenv(k, raising=False)
                    else:
                        sv = str(v)
                        # Convenience: if an env value looks like a relative path and a
                        # file exists under the runner temp dir, pass the absolute path.
                        try:
                            from pathlib import Path

                            pv = Path(sv).expanduser()
                            if not pv.is_absolute() and (ctx.tmp_path / pv).exists():
                                sv = str((ctx.tmp_path / pv).resolve())
                        except (OSError, ValueError):
                            pass
                        mp.setenv(k, sv)

            stdin_text = h.get("stdin_text")
            stdin_isatty = h.get("stdin_isatty")
            if stdin_text is not None or stdin_isatty is not None:
                class _FakeStdin(io.StringIO):
                    def __init__(self, text: str, isatty: bool):
                        super().__init__(text)
                        self._isatty = bool(isatty)

                    def isatty(self) -> bool:
                        return self._isatty

                fake = _FakeStdin("" if stdin_text is None else str(stdin_text), bool(stdin_isatty))
                mp.setattr(sys, "stdin", fake)

            # Test-only affordance: allow docs-embedded contract-specs to simulate missing
            # optional dependencies in a deterministic way.
            block_imports = h.get("block_imports") or []
            if isinstance(block_imports, str):
                block_imports = [block_imports]
            block_imports = {str(x) for x in block_imports if str(x).strip()}

            real_import = builtins.__import__

            def _blocked_import(name, globals=None, locals=None, fromlist=(), level=0):
                if name in block_imports or any(name.startswith(m + ".") for m in block_imports):
                    raise ModuleNotFoundError(name)
                return real_import(name, globals, locals, fromlist, level)

            if block_imports:
                mp.setattr(builtins, "__import__", _blocked_import)

            if safe_mode and (hook_before_ep or hook_after_ep):
                raise RuntimeError(
                    "cli.run safe mode forbids hook_before/hook_after; "
                    f"unset {SETTINGS.env.safe_mode} to use hooks"
                )

            if hook_before_ep:
                hook_before_fn = _load_entrypoint(str(hook_before_ep))
                hook_before_fn(case=hook_case, ctx=ctx, harness=h, **{str(k): v for k, v in hook_kwargs.items()})

            entrypoint = str(h.get("entrypoint") or "").strip()
            if not entrypoint:
                raise RuntimeError("cli.run requires explicit harness.entrypoint")
            cli_main = _load_entrypoint(entrypoint)

            try:
                code = cli_main(argv)
            except SystemExit as e:
                ec = getattr(e, "code", 1)
                code = 1 if ec is None else int(ec)

            captured = ctx.read_capture()
            got = int(code)
            want = int(t.get("exit_code", 0))
            assert got == want, f"[case_id={case_id}] exit_code expected={want} actual={got}"

            # Optional hook_after for complex assertions/setup that don't fit the declarative DSL.
            if hook_after_ep:
                # Best-effort derive stdout_path for convenience.
                stdout_path = None
                try:
                    stdout_path = assert_stdout_path_exists(captured.out)
                except AssertionError:
                    stdout_path = None
                hook_after_fn = _load_entrypoint(str(hook_after_ep))
                hook_after_fn(
                    case=hook_case,
                    ctx=ctx,
                    result={
                        "exit_code": int(code),
                        "stdout": captured.out,
                        "stderr": captured.err,
                        "stdout_path": stdout_path,
                    },
                    **{str(k): v for k, v in hook_kwargs.items()},
                )

    context_profile = {
        "profile_id": "cli.run/v1",
        "profile_version": 1,
        "value": {
            "exit_code": int(code),
            "stdout": captured.out,
            "stderr": captured.err,
        },
        "meta": {
            "target": "cli.run",
            "case_id": case_id,
            "argv": argv,
        },
        "context": {
            "entrypoint": entrypoint,
            "safe_mode": safe_mode,
        },
    }

    line = first_nonempty_line(captured.out)
    stdout_path_exists = False
    if line:
        try:
            from pathlib import Path

            stdout_path_exists = Path(line).exists()
        except (OSError, ValueError):
            stdout_path_exists = False
    mode = resolve_assert_health_mode(t, env=runtime_env)
    diags = lint_assert_tree(t.get("contract", []) or [])
    warning_lines: list[str] = []
    if diags and mode == "error":
        raise AssertionError(format_assertion_health_error(diags))
    if diags and mode == "warn":
        for d in diags:
            rendered = format_assertion_health_warning(d)
            warning_lines.append(rendered)
            print(rendered, file=sys.stderr)
    stderr_subject = captured.err
    if warning_lines:
        joiner = "\n" if stderr_subject and not stderr_subject.endswith("\n") else ""
        joined_warnings = "\n".join(warning_lines)
        stderr_subject = f"{stderr_subject}{joiner}{joined_warnings}"

    targets = {
        "stdout": captured.out,
        "stderr": stderr_subject,
        "stdout_path.exists": stdout_path_exists,
        "context_json": context_profile,
        "chain_json": chain_payload,
    }
    targets["meta_json"] = build_meta_subject(
        case=case,
        ctx=ctx,
        case_key=case_key,
        harness={**h, "_chain_imports": chain_imports},
        artifacts=targets,
    )
    ctx.set_case_targets(case_key=case_key, targets=targets)

    def _subject_for_key(subject_key: str):
        if subject_key == "stdout_path":
            line_local = first_nonempty_line(captured.out)
            if not line_local:
                raise AssertionError("expected stdout to contain a path")
            return line_local
        if subject_key == "stdout_path_text":
            p = assert_stdout_path_exists(captured.out)
            return p.read_text(encoding="utf-8")
        return resolve_subject_for_target(subject_key, targets, type_name="cli.run")

    run_assertions_with_context(
        assert_tree=case.assert_tree,
        raw_assert_spec=[],
        raw_case={},
        ctx=ctx,
        execution=execution,
        subject_for_key=_subject_for_key,
    )
