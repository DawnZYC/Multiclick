from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class ClickMode(str, Enum):
    MOUSE = "mouse"
    KEYBOARD = "keyboard"
    CUSTOM = "custom"


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
class KeyboardTarget:
    kind: str
    value: str
    display_text: str


@dataclass(frozen=True)
class KeyboardClickConfig:
    interval_seconds: float
    duration_seconds: float
    target: KeyboardTarget


@dataclass(frozen=True)
class CustomAction:
    action_type: str
    timestamp_seconds: float
    position: Optional[ClickPosition] = None
    mouse_button: Optional[str] = None
    keyboard_target: Optional[KeyboardTarget] = None


@dataclass(frozen=True)
class CustomLoopConfig:
    loop_count: int
    actions: List[CustomAction]


@dataclass(frozen=True)
class ClickProgress:
    click_count: int
    remaining_seconds: float


@dataclass(frozen=True)
class ClickResult:
    click_count: int
    interrupted: bool


@dataclass(frozen=True)
class CustomLoopProgress:
    completed_loops: int
    total_loops: int


@dataclass(frozen=True)
class CustomLoopResult:
    completed_loops: int
    total_loops: int
    interrupted: bool
