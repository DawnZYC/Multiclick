import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from pynput import keyboard

from multiclick.models import (
    ClickMode,
    ClickPosition,
    ClickProgress,
    ClickResult,
    CustomAction,
    CustomLoopConfig,
    CustomLoopProgress,
    CustomLoopResult,
    KeyboardClickConfig,
    KeyboardTarget,
    MouseClickConfig,
)
from multiclick.ui import messages
from multiclick.services.keyboard_support import build_keyboard_target


class MessageTests(unittest.TestCase):
    def test_default_status_for_mouse_mode(self) -> None:
        self.assertEqual(messages.default_status(ClickMode.MOUSE), "请选择鼠标连点参数后开始。")

    def test_default_status_for_keyboard_mode(self) -> None:
        self.assertEqual(messages.default_status(ClickMode.KEYBOARD), "请选择键盘连点参数后开始。")

    def test_default_status_for_custom_mode(self) -> None:
        self.assertEqual(messages.default_status(ClickMode.CUSTOM), "请选择自定义循环参数后开始。")

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

    def test_custom_running_status_contains_loop_count(self) -> None:
        config = CustomLoopConfig(
            loop_count=3,
            actions=[
                CustomAction(
                    action_type="keyboard_press",
                    timestamp_seconds=0.1,
                    keyboard_target=KeyboardTarget(kind="char", value="a", display_text="A"),
                )
            ],
        )
        status = messages.custom_running_status(config)
        self.assertIn("总循环 3 次", status)
        self.assertIn("每轮 1 个动作", status)

    def test_custom_action_summary_uses_last_timestamp(self) -> None:
        summary = messages.custom_action_summary(
            [
                CustomAction(action_type="mouse_press", timestamp_seconds=0.1),
                CustomAction(action_type="mouse_release", timestamp_seconds=1.5),
            ]
        )
        self.assertIn("2 个动作", summary)
        self.assertIn("1.50 秒", summary)

    def test_custom_progress_status_formats_loop_counts(self) -> None:
        progress = CustomLoopProgress(completed_loops=2, total_loops=5)
        self.assertIn("2/5", messages.custom_progress_status(progress))

    def test_keyboard_finished_status_reflects_completion(self) -> None:
        result = ClickResult(click_count=8, interrupted=False)
        self.assertEqual(messages.keyboard_finished_status(result), "键盘连点已完成，共点击 8 次。")

    def test_custom_finished_status_reflects_interruption(self) -> None:
        result = CustomLoopResult(completed_loops=1, total_loops=4, interrupted=True)
        self.assertEqual(messages.custom_finished_status(result), "自定义循环已中断，已完成 1/4 次循环。")

    def test_build_keyboard_target_keeps_vk_label(self) -> None:
        target = build_keyboard_target(keyboard.KeyCode.from_vk(67))
        self.assertEqual(target.kind, "vk")
        self.assertEqual(target.display_text, "C")


if __name__ == "__main__":
    unittest.main()
