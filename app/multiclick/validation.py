from typing import Optional

from multiclick.models import ClickPosition, MouseClickConfig


class ValidationError(ValueError):
    """Raised when UI input cannot be converted into a valid click configuration."""


def parse_positive_float(raw_value: str, field_label: str) -> float:
    try:
        value = float(raw_value)
    except ValueError as exc:
        raise ValidationError(f"{field_label}必须是数字。") from exc

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
