import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from multiclick.models import ClickMode, ClickProgress, ClickResult, ClickPosition, MouseClickConfig
from multiclick.ui import messages


class MessageTests(unittest.TestCase):
    def test_default_status_for_mouse_mode(self) -> None:
        self.assertEqual(messages.default_status(ClickMode.MOUSE), "请选择参数后开始。")

    def test_progress_status_formats_seconds(self) -> None:
        progress = ClickProgress(click_count=5, remaining_seconds=1.234)
        self.assertIn("已点击 5 次", messages.progress_status(progress))
        self.assertIn("1.23 秒", messages.progress_status(progress))

    def test_running_status_contains_position(self) -> None:
        config = MouseClickConfig(
            interval_seconds=0.1,
            duration_seconds=10,
            position=ClickPosition(x=100, y=200),
        )
        status = messages.running_status(config)
        self.assertIn("X=100, Y=200", status)
        self.assertIn("间隔 0.1s", status)

    def test_finished_status_reflects_interruption(self) -> None:
        result = ClickResult(click_count=12, interrupted=True)
        self.assertEqual(messages.finished_status(result), "鼠标连点已中断，共点击 12 次。")


if __name__ == "__main__":
    unittest.main()
