import threading
import time
from collections.abc import Callable
from typing import List, Optional, Set, Union

from pynput import keyboard, mouse

from multiclick.models import ClickPosition, CustomAction
from multiclick.services.keyboard_support import build_keyboard_target


class CustomActionRecorder:
    def __init__(self, on_finished: Callable[[List[CustomAction]], None]) -> None:
        self._on_finished = on_finished
        self._actions: List[CustomAction] = []
        self._started_at: Optional[float] = None
        self._pressed_mouse_buttons: Set[str] = set()
        self._mouse_listener: Optional[mouse.Listener] = None
        self._keyboard_listener: Optional[keyboard.Listener] = None

    def start(self) -> None:
        self._actions = []
        self._pressed_mouse_buttons = set()
        self._started_at = time.perf_counter()
        self._mouse_listener = mouse.Listener(
            on_move=self._handle_move,
            on_click=self._handle_click,
        )
        self._keyboard_listener = keyboard.Listener(
            on_press=self._handle_key_press,
            on_release=self._handle_key_release,
        )
        self._mouse_listener.start()
        self._keyboard_listener.start()

    def stop(self) -> None:
        if self._mouse_listener is not None:
            mouse_listener = self._mouse_listener
            mouse_listener.stop()
            self._mouse_listener = None
            if mouse_listener.is_alive() and mouse_listener is not threading.current_thread():
                mouse_listener.join(timeout=1.0)

        if self._keyboard_listener is not None:
            keyboard_listener = self._keyboard_listener
            keyboard_listener.stop()
            self._keyboard_listener = None
            if keyboard_listener.is_alive() and keyboard_listener is not threading.current_thread():
                keyboard_listener.join(timeout=1.0)

    def _handle_move(self, x: int, y: int) -> bool:
        if not self._pressed_mouse_buttons:
            return True

        self._actions.append(
            CustomAction(
                action_type="mouse_move",
                timestamp_seconds=self._elapsed_seconds(),
                position=ClickPosition(x=x, y=y),
            )
        )
        return True

    def _handle_click(self, x: int, y: int, button: mouse.Button, pressed: bool) -> bool:
        button_name = button.name
        if pressed:
            self._pressed_mouse_buttons.add(button_name)
            action_type = "mouse_press"
        else:
            self._pressed_mouse_buttons.discard(button_name)
            action_type = "mouse_release"

        self._actions.append(
            CustomAction(
                action_type=action_type,
                timestamp_seconds=self._elapsed_seconds(),
                position=ClickPosition(x=x, y=y),
                mouse_button=button_name,
            )
        )
        return True

    def _handle_key_press(self, key: Union[keyboard.Key, keyboard.KeyCode]) -> bool:
        if key == keyboard.Key.esc:
            self.stop()
            self._on_finished(list(self._actions))
            return False

        self._actions.append(
            CustomAction(
                action_type="keyboard_press",
                timestamp_seconds=self._elapsed_seconds(),
                keyboard_target=build_keyboard_target(key),
            )
        )
        return True

    def _handle_key_release(self, key: Union[keyboard.Key, keyboard.KeyCode]) -> bool:
        if key == keyboard.Key.esc:
            return False

        self._actions.append(
            CustomAction(
                action_type="keyboard_release",
                timestamp_seconds=self._elapsed_seconds(),
                keyboard_target=build_keyboard_target(key),
            )
        )
        return True

    def _elapsed_seconds(self) -> float:
        if self._started_at is None:
            return 0.0
        return max(0.0, time.perf_counter() - self._started_at)
