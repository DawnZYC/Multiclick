import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from multiclick.models import (
    ClickMode,
    ClickPosition,
    ClickProgress,
    ClickResult,
    KeyboardClickConfig,
    KeyboardTarget,
    MouseClickConfig,
)
from multiclick.ui import messages


class MessageTests(unittest.TestCase):
    def test_default_status_for_mouse_mode(self) -> None:
        self.assertEqual(messages.default_status(ClickMode.MOUSE), "请选择鼠标连点参数后开始。")

    def test_default_status_for_keyboard_mode(self) -> None:
        self.assertEqual(messages.default_status(ClickMode.KEYBOARD), "请选择键盘连点参数后开始。")

    def test_mouse_progress_status_formats_seconds(self) -> None:
        progress = ClickProgress(click_count=5, remaining_seconds=1.234)
        self.assertIn("已点击 5 次", messages.mouse_progress_status(progress))
        self.assertIn("1.23 秒", messages.mouse_progress_status(progress))

    def test_mouse_running_status_contains_position(self) -> None:
        config = MouseClickConfig(
            interval_seconds=0.1,
            duration_seconds=10,
            position=ClickPosition(x=100, y=200),
        )
        status = messages.mouse_running_status(config)
        self.assertIn("X=100, Y=200", status)
        self.assertIn("间隔 0.1s", status)

    def test_keyboard_running_status_contains_target(self) -> None:
        config = KeyboardClickConfig(
            interval_seconds=0.2,
            duration_seconds=3,
            target=KeyboardTarget(kind="char", value="a", display_text="A"),
        )
        status = messages.keyboard_running_status(config)
        self.assertIn("按键 A", status)
        self.assertIn("间隔 0.2s", status)

    def test_mouse_finished_status_reflects_interruption(self) -> None:
        result = ClickResult(click_count=12, interrupted=True)
        self.assertEqual(messages.mouse_finished_status(result), "鼠标连点已中断，共点击 12 次。")

    def test_keyboard_finished_status_reflects_completion(self) -> None:
        result = ClickResult(click_count=8, interrupted=False)
        self.assertEqual(messages.keyboard_finished_status(result), "键盘连点已完成，共点击 8 次。")


if __name__ == "__main__":
    unittest.main()
