from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

CommandHandler = Callable[[list[str]], int]


@dataclass(frozen=True)
class CommandSpec:
    name: str
    handler: CommandHandler
