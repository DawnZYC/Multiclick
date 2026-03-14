from typing import Union

from pynput import keyboard

from multiclick.models import KeyboardTarget


def build_keyboard_target(key: Union[keyboard.Key, keyboard.KeyCode]) -> KeyboardTarget:
    if isinstance(key, keyboard.Key):
        name = key.name or str(key).split(".")[-1]
        return KeyboardTarget(kind="key", value=name, display_text=_format_special_key_name(name))

    if key.char:
        return KeyboardTarget(kind="char", value=key.char, display_text=key.char.upper())

    if key.vk is not None:
        return KeyboardTarget(kind="vk", value=str(key.vk), display_text=f"VK_{key.vk}")

    raise ValueError("无法识别按键。")


def resolve_keyboard_target(target: KeyboardTarget) -> Union[keyboard.Key, keyboard.KeyCode, str]:
    if target.kind == "key":
        return getattr(keyboard.Key, target.value)

    if target.kind == "char":
        return target.value

    if target.kind == "vk":
        return keyboard.KeyCode.from_vk(int(target.value))

    raise ValueError(f"不支持的按键类型: {target.kind}")


def _format_special_key_name(name: str) -> str:
    label_map = {
        "alt": "Alt",
        "alt_l": "Left Alt",
        "alt_r": "Right Alt",
        "backspace": "Backspace",
        "caps_lock": "Caps Lock",
        "cmd": "Cmd",
        "cmd_l": "Left Cmd",
        "cmd_r": "Right Cmd",
        "ctrl": "Ctrl",
        "ctrl_l": "Left Ctrl",
        "ctrl_r": "Right Ctrl",
        "delete": "Delete",
        "down": "Down",
        "end": "End",
        "enter": "Enter",
        "esc": "Esc",
        "f1": "F1",
        "f2": "F2",
        "f3": "F3",
        "f4": "F4",
        "f5": "F5",
        "f6": "F6",
        "f7": "F7",
        "f8": "F8",
        "f9": "F9",
        "f10": "F10",
        "f11": "F11",
        "f12": "F12",
        "home": "Home",
        "insert": "Insert",
        "left": "Left",
        "menu": "Menu",
        "page_down": "Page Down",
        "page_up": "Page Up",
        "right": "Right",
        "shift": "Shift",
        "shift_l": "Left Shift",
        "shift_r": "Right Shift",
        "space": "Space",
        "tab": "Tab",
        "up": "Up",
    }
    return label_map.get(name, name.replace("_", " ").title())
