from typing import List

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


WINDOW_TITLE = "Multiclick 连点器"
WINDOW_MIN_WIDTH = 620
WINDOW_MIN_HEIGHT = 500
DEFAULT_POSITION_TEXT = "未设置"


def default_status(mode: ClickMode) -> str:
    if mode is ClickMode.KEYBOARD:
        return "请选择键盘连点参数后开始。"
    if mode is ClickMode.CUSTOM:
        return "请选择自定义循环参数后开始。"
    return "请选择鼠标连点参数后开始。"


def subtitle_text() -> str:
    return "支持鼠标连点、键盘连点和自定义循环，运行中按 Esc 可中断。"


def parameter_frame_title(mode: ClickMode) -> str:
    if mode is ClickMode.KEYBOARD:
        return "键盘连点参数"
    if mode is ClickMode.CUSTOM:
        return "自定义循环参数"
    return "鼠标连点参数"


def primary_label_text(mode: ClickMode) -> str:
    if mode is ClickMode.CUSTOM:
        return "循环次数"
    return "点击间隔时间（秒）"


def secondary_label_text(mode: ClickMode) -> str:
    if mode is ClickMode.CUSTOM:
        return ""
    return "连点时间（秒）"


def target_label_text(mode: ClickMode) -> str:
    if mode is ClickMode.KEYBOARD:
        return "点击按键"
    if mode is ClickMode.CUSTOM:
        return "循环动作"
    return "点击位置"


def capture_button_text(mode: ClickMode) -> str:
    if mode is ClickMode.KEYBOARD:
        return "设置按键"
    if mode is ClickMode.CUSTOM:
        return "设定动作"
    return "设置位置"


def start_button_text(mode: ClickMode) -> str:
    if mode is ClickMode.CUSTOM:
        return "开始循环"
    return "开始连点"


def capture_hint(mode: ClickMode) -> str:
    if mode is ClickMode.KEYBOARD:
        return "设置按键后按下目标键。运行中按 Esc 可中断，设置时按 Esc 可取消。"
    if mode is ClickMode.CUSTOM:
        return "点击设定动作后会弹出置顶窗口。点击开始自定义后开始录制，按 Esc 保存动作。"
    return "设置位置时点击一次目标位置。运行中按 Esc 可中断，设置时按 Esc 可取消。"


def capture_status(mode: ClickMode) -> str:
    if mode is ClickMode.KEYBOARD:
        return "按键捕获已开启：请按下目标按键，或按 Esc 取消。"
    if mode is ClickMode.CUSTOM:
        return "自定义动作录制中：请执行键盘鼠标动作，按 Esc 保存。"
    return "位置捕获已开启：请在目标位置点击一次鼠标，或按 Esc 取消。"


def capture_cancelled_status(mode: ClickMode) -> str:
    if mode is ClickMode.KEYBOARD:
        return "已取消按键捕获。"
    if mode is ClickMode.CUSTOM:
        return "已取消自定义动作设定。"
    return "已取消位置捕获。"


def mouse_target_selected_status(position: ClickPosition) -> str:
    return f"已设置点击位置：{position.display_text}"


def keyboard_target_selected_status(target: KeyboardTarget) -> str:
    return f"已设置点击按键：{target.display_text}"


def custom_actions_selected_status(actions: List[CustomAction]) -> str:
    if not actions:
        return "未录制到任何动作。"
    return f"已保存循环动作：{custom_action_summary(actions)}"


def custom_action_summary(actions: List[CustomAction]) -> str:
    if not actions:
        return DEFAULT_POSITION_TEXT
    duration_seconds = actions[-1].timestamp_seconds
    return f"{len(actions)} 个动作 / 单次约 {duration_seconds:.2f} 秒"


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


def custom_running_status(config: CustomLoopConfig) -> str:
    return (
        "自定义循环运行中："
        f"总循环 {config.loop_count} 次，"
        f"每轮 {len(config.actions)} 个动作。按 Esc 可中断。"
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


def custom_progress_status(progress: CustomLoopProgress) -> str:
    return (
        "自定义循环运行中："
        f"已完成 {progress.completed_loops}/{progress.total_loops} 次循环。按 Esc 可中断。"
    )


def mouse_finished_status(result: ClickResult) -> str:
    if result.interrupted:
        return f"鼠标连点已中断，共点击 {result.click_count} 次。"
    return f"鼠标连点已完成，共点击 {result.click_count} 次。"


def keyboard_finished_status(result: ClickResult) -> str:
    if result.interrupted:
        return f"键盘连点已中断，共点击 {result.click_count} 次。"
    return f"键盘连点已完成，共点击 {result.click_count} 次。"


def custom_finished_status(result: CustomLoopResult) -> str:
    if result.interrupted:
        return f"自定义循环已中断，已完成 {result.completed_loops}/{result.total_loops} 次循环。"
    return f"自定义循环已完成，共完成 {result.total_loops}/{result.total_loops} 次循环。"
