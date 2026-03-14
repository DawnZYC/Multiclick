from multiclick.models import ClickMode, ClickPosition, ClickProgress, ClickResult, MouseClickConfig


WINDOW_TITLE = "Multiclick 连点器"
WINDOW_MIN_WIDTH = 520
WINDOW_MIN_HEIGHT = 460
DEFAULT_POSITION_TEXT = "未设置"


def default_status(mode: ClickMode) -> str:
    if mode is ClickMode.KEYBOARD:
        return "键盘连点界面已预留，当前版本仅支持鼠标连点。"
    return "请选择参数后开始。"


def capture_status() -> str:
    return "位置捕获已开启：请在目标位置点击一次鼠标，或按 Esc 取消。"


def capture_cancelled_status() -> str:
    return "已取消位置捕获。"


def position_selected_status(position: ClickPosition) -> str:
    return f"已设置点击位置：{position.display_text}"


def running_status(config: MouseClickConfig) -> str:
    return (
        "鼠标连点运行中："
        f"间隔 {config.interval_seconds}s，"
        f"持续 {config.duration_seconds}s，"
        f"位置 {config.position.display_text}。按 Esc 可中断。"
    )


def progress_status(progress: ClickProgress) -> str:
    return (
        "鼠标连点运行中："
        f"已点击 {progress.click_count} 次，"
        f"剩余约 {progress.remaining_seconds:.2f} 秒。按 Esc 可中断。"
    )


def finished_status(result: ClickResult) -> str:
    if result.interrupted:
        return f"鼠标连点已中断，共点击 {result.click_count} 次。"
    return f"鼠标连点已完成，共点击 {result.click_count} 次。"
