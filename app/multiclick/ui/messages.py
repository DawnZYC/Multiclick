from multiclick.models import (
    ClickMode,
    ClickPosition,
    ClickProgress,
    ClickResult,
    KeyboardClickConfig,
    KeyboardTarget,
    MouseClickConfig,
)


WINDOW_TITLE = "Multiclick 连点器"
WINDOW_MIN_WIDTH = 520
WINDOW_MIN_HEIGHT = 460
DEFAULT_POSITION_TEXT = "未设置"


def default_status(mode: ClickMode) -> str:
    if mode is ClickMode.KEYBOARD:
        return "请选择键盘连点参数后开始。"
    return "请选择鼠标连点参数后开始。"


def subtitle_text() -> str:
    return "支持鼠标连点和键盘连点，运行中按 Esc 可中断。"


def parameter_frame_title(mode: ClickMode) -> str:
    if mode is ClickMode.KEYBOARD:
        return "键盘连点参数"
    return "鼠标连点参数"


def target_label_text(mode: ClickMode) -> str:
    if mode is ClickMode.KEYBOARD:
        return "点击按键"
    return "点击位置"


def capture_button_text(mode: ClickMode) -> str:
    if mode is ClickMode.KEYBOARD:
        return "设置按键"
    return "设置位置"


def capture_hint(mode: ClickMode) -> str:
    if mode is ClickMode.KEYBOARD:
        return "设置按键后按下目标键。运行中按 Esc 可中断，设置时按 Esc 可取消。"
    return "设置位置时点击一次目标位置。运行中按 Esc 可中断，设置时按 Esc 可取消。"


def capture_status(mode: ClickMode) -> str:
    if mode is ClickMode.KEYBOARD:
        return "按键捕获已开启：请按下目标按键，或按 Esc 取消。"
    return "位置捕获已开启：请在目标位置点击一次鼠标，或按 Esc 取消。"


def capture_cancelled_status(mode: ClickMode) -> str:
    if mode is ClickMode.KEYBOARD:
        return "已取消按键捕获。"
    return "已取消位置捕获。"


def mouse_target_selected_status(position: ClickPosition) -> str:
    return f"已设置点击位置：{position.display_text}"


def keyboard_target_selected_status(target: KeyboardTarget) -> str:
    return f"已设置点击按键：{target.display_text}"


def mouse_running_status(config: MouseClickConfig) -> str:
    return (
        "鼠标连点运行中："
        f"间隔 {config.interval_seconds}s，"
        f"持续 {config.duration_seconds}s，"
        f"位置 {config.position.display_text}。按 Esc 可中断。"
    )


def keyboard_running_status(config: KeyboardClickConfig) -> str:
    return (
        "键盘连点运行中："
        f"间隔 {config.interval_seconds}s，"
        f"持续 {config.duration_seconds}s，"
        f"按键 {config.target.display_text}。按 Esc 可中断。"
    )


def mouse_progress_status(progress: ClickProgress) -> str:
    return (
        "鼠标连点运行中："
        f"已点击 {progress.click_count} 次，"
        f"剩余约 {progress.remaining_seconds:.2f} 秒。按 Esc 可中断。"
    )


def keyboard_progress_status(progress: ClickProgress) -> str:
    return (
        "键盘连点运行中："
        f"已点击 {progress.click_count} 次，"
        f"剩余约 {progress.remaining_seconds:.2f} 秒。按 Esc 可中断。"
    )


def mouse_finished_status(result: ClickResult) -> str:
    if result.interrupted:
        return f"鼠标连点已中断，共点击 {result.click_count} 次。"
    return f"鼠标连点已完成，共点击 {result.click_count} 次。"


def keyboard_finished_status(result: ClickResult) -> str:
    if result.interrupted:
        return f"键盘连点已中断，共点击 {result.click_count} 次。"
    return f"键盘连点已完成，共点击 {result.click_count} 次。"
