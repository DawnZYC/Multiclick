import threading
from collections.abc import Callable
from typing import Optional, Union

from pynput import keyboard

from multiclick.models import KeyboardTarget
from multiclick.services.keyboard_support import build_keyboard_target


class KeyboardCaptureService:
    def __init__(
        self,
        on_captured: Callable[[KeyboardTarget], None],
        on_cancelled: Callable[[], None],
    ) -> None:
        self._on_captured = on_captured
        self._on_cancelled = on_cancelled
        self._keyboard_listener: Optional[keyboard.Listener] = None

    def start(self) -> None:
        self._keyboard_listener = keyboard.Listener(on_press=self._handle_key_press)
        self._keyboard_listener.start()

    def stop(self) -> None:
        if self._keyboard_listener is not None:
            keyboard_listener = self._keyboard_listener
            keyboard_listener.stop()
            self._keyboard_listener = None
            if keyboard_listener.is_alive() and keyboard_listener is not threading.current_thread():
                keyboard_listener.join(timeout=1.0)

    def _handle_key_press(self, key: Union[keyboard.Key, keyboard.KeyCode]) -> bool:
        if key == keyboard.Key.esc:
            self.stop()
            self._on_cancelled()
            return False

        try:
            target = build_keyboard_target(key)
        except ValueError:
            return True

        self.stop()
        self._on_captured(target)
        return False
