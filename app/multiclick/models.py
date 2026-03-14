from dataclasses import dataclass
from enum import Enum


class ClickMode(str, Enum):
    MOUSE = "mouse"
    KEYBOARD = "keyboard"


@dataclass(frozen=True)
class ClickPosition:
    x: int
    y: int

    @property
    def display_text(self) -> str:
        return f"X={self.x}, Y={self.y}"


@dataclass(frozen=True)
class MouseClickConfig:
    interval_seconds: float
    duration_seconds: float
    position: ClickPosition


@dataclass(frozen=True)
class ClickProgress:
    click_count: int
    remaining_seconds: float


@dataclass(frozen=True)
class ClickResult:
    click_count: int
    interrupted: bool
