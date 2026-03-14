from typing import List, Optional

from multiclick.models import (
    ClickPosition,
    CustomAction,
    CustomLoopConfig,
    KeyboardClickConfig,
    KeyboardTarget,
    MouseClickConfig,
)


class ValidationError(ValueError):
    """Raised when UI input cannot be converted into a valid configuration."""


def parse_positive_float(raw_value: str, field_label: str) -> float:
    try:
        value = float(raw_value)
    except ValueError as exc:
        raise ValidationError(f"{field_label}必须是数字。") from exc

    if value <= 0:
        raise ValidationError(f"{field_label}必须大于 0。")

    return value


def parse_positive_int(raw_value: str, field_label: str) -> int:
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ValidationError(f"{field_label}必须是整数。") from exc

    if value <= 0:
        raise ValidationError(f"{field_label}必须大于 0。")

    return value


def build_mouse_click_config(
    interval_raw: str,
    duration_raw: str,
    position: Optional[ClickPosition],
) -> MouseClickConfig:
    interval_seconds = parse_positive_float(interval_raw, "点击间隔时间")
    duration_seconds = parse_positive_float(duration_raw, "连点时间")

    if position is None:
        raise ValidationError("请先设置点击位置。")

    return MouseClickConfig(
        interval_seconds=interval_seconds,
        duration_seconds=duration_seconds,
        position=position,
    )


def build_keyboard_click_config(
    interval_raw: str,
    duration_raw: str,
    target: Optional[KeyboardTarget],
) -> KeyboardClickConfig:
    interval_seconds = parse_positive_float(interval_raw, "点击间隔时间")
    duration_seconds = parse_positive_float(duration_raw, "连点时间")

    if target is None:
        raise ValidationError("请先设置点击按键。")

    return KeyboardClickConfig(
        interval_seconds=interval_seconds,
        duration_seconds=duration_seconds,
        target=target,
    )


def build_custom_loop_config(
    loop_count_raw: str,
    actions: List[CustomAction],
) -> CustomLoopConfig:
    loop_count = parse_positive_int(loop_count_raw, "循环次数")

    if not actions:
        raise ValidationError("请先设定循环动作。")

    return CustomLoopConfig(loop_count=loop_count, actions=actions)
