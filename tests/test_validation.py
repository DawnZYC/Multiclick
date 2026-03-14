import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from multiclick.models import ClickPosition, CustomAction, ClickMode, KeyboardTarget
from multiclick.validation import (
    ValidationError,
    build_custom_loop_config,
    build_keyboard_click_config,
    build_mouse_click_config,
    parse_positive_float,
    parse_positive_int,
)


class ValidationTests(unittest.TestCase):
    def test_parse_positive_float_accepts_valid_value(self) -> None:
        self.assertEqual(parse_positive_float("0.25", "点击间隔时间"), 0.25)

    def test_parse_positive_float_rejects_non_numeric_value(self) -> None:
        with self.assertRaises(ValidationError):
            parse_positive_float("abc", "点击间隔时间")

    def test_parse_positive_int_accepts_valid_value(self) -> None:
        self.assertEqual(parse_positive_int("3", "循环次数"), 3)

    def test_parse_positive_int_rejects_non_integer_value(self) -> None:
        with self.assertRaises(ValidationError):
            parse_positive_int("1.5", "循环次数")

    def test_build_mouse_click_config_requires_position(self) -> None:
        with self.assertRaises(ValidationError):
            build_mouse_click_config("0.1", "1.0", None)

    def test_build_mouse_click_config_returns_config(self) -> None:
        config = build_mouse_click_config("0.1", "1.5", ClickPosition(x=1, y=2))
        self.assertEqual(config.interval_seconds, 0.1)
        self.assertEqual(config.duration_seconds, 1.5)
        self.assertEqual(config.position.x, 1)

    def test_build_keyboard_click_config_requires_target(self) -> None:
        with self.assertRaises(ValidationError):
            build_keyboard_click_config("0.1", "1.0", None)

    def test_build_keyboard_click_config_returns_config(self) -> None:
        config = build_keyboard_click_config(
            "0.2",
            "2.5",
            KeyboardTarget(kind="char", value="a", display_text="A"),
        )
        self.assertEqual(config.interval_seconds, 0.2)
        self.assertEqual(config.duration_seconds, 2.5)
        self.assertEqual(config.target.display_text, "A")

    def test_build_custom_loop_config_requires_actions(self) -> None:
        with self.assertRaises(ValidationError):
            build_custom_loop_config("2", [])

    def test_build_custom_loop_config_returns_config(self) -> None:
        config = build_custom_loop_config(
            "2",
            [
                CustomAction(
                    action_type="keyboard_press",
                    timestamp_seconds=0.1,
                    keyboard_target=KeyboardTarget(kind="char", value="a", display_text="A"),
                )
            ],
        )
        self.assertEqual(config.loop_count, 2)
        self.assertEqual(len(config.actions), 1)


if __name__ == "__main__":
    unittest.main()
