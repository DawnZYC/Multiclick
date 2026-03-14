import threading
from collections.abc import Callable
from typing import Optional, Union

from pynput import keyboard, mouse

from multiclick.models import ClickPosition


class PositionCaptureService:
    def __init__(
        self,
        on_captured: Callable[[ClickPosition], None],
        on_cancelled: Callable[[], None],
    ) -> None:
        self._on_captured = on_captured
        self._on_cancelled = on_cancelled
        self._mouse_listener: Optional[mouse.Listener] = None
        self._keyboard_listener: Optional[keyboard.Listener] = None
        self._mouse_controller = mouse.Controller()

    def start(self) -> None:
        self._mouse_listener = mouse.Listener(on_click=self._handle_click)
        self._keyboard_listener = keyboard.Listener(on_press=self._handle_key_press)
        self._mouse_listener.start()
        self._keyboard_listener.start()

    def stop(self) -> None:
        if self._mouse_listener is not None:
            mouse_listener = self._mouse_listener
            self._mouse_listener.stop()
            self._mouse_listener = None
            if mouse_listener.is_alive() and mouse_listener is not threading.current_thread():
                mouse_listener.join(timeout=1.0)

        if self._keyboard_listener is not None:
            keyboard_listener = self._keyboard_listener
            self._keyboard_listener.stop()
            self._keyboard_listener = None
            if keyboard_listener.is_alive() and keyboard_listener is not threading.current_thread():
                keyboard_listener.join(timeout=1.0)

    def _handle_click(self, x: int, y: int, _button: mouse.Button, pressed: bool) -> bool:
        if not pressed:
            return True

        current_x, current_y = self._mouse_controller.position
        self.stop()
        self._on_captured(ClickPosition(x=int(current_x), y=int(current_y)))
        return False

    def _handle_key_press(self, key: Union[keyboard.Key, keyboard.KeyCode]) -> bool:
        if key != keyboard.Key.esc:
            return True

        self.stop()
        self._on_cancelled()
        return False
