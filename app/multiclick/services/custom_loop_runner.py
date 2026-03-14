import threading
import time
from collections.abc import Callable
from typing import Optional, Union

from pynput import keyboard, mouse

from multiclick.models import CustomAction, CustomLoopConfig, CustomLoopProgress, CustomLoopResult
from multiclick.services.keyboard_support import resolve_keyboard_target


class CustomLoopRunner:
    def __init__(
        self,
        config: CustomLoopConfig,
        on_progress: Callable[[CustomLoopProgress], None],
        on_finish: Callable[[CustomLoopResult], None],
    ) -> None:
        self._config = config
        self._on_progress = on_progress
        self._on_finish = on_finish
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._keyboard_listener: Optional[keyboard.Listener] = None

    def start(self) -> None:
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._keyboard_listener is not None:
            keyboard_listener = self._keyboard_listener
            keyboard_listener.stop()
            self._keyboard_listener = None
            if keyboard_listener.is_alive() and keyboard_listener is not threading.current_thread():
                keyboard_listener.join(timeout=1.0)

        if self._thread is not None and self._thread.is_alive() and self._thread is not threading.current_thread():
            self._thread.join(timeout=1.0)
        self._thread = None

    def _run(self) -> None:
        keyboard_controller = keyboard.Controller()
        mouse_controller = mouse.Controller()
        completed_loops = 0

        def handle_key_press(key: Union[keyboard.Key, keyboard.KeyCode]) -> bool:
            if key == keyboard.Key.esc:
                self._stop_event.set()
                return False
            return True

        self._keyboard_listener = keyboard.Listener(on_press=handle_key_press)
        self._keyboard_listener.start()

        for loop_index in range(self._config.loop_count):
            if self._stop_event.is_set():
                break

            loop_started_at = time.perf_counter()
            for action in self._config.actions:
                if self._wait_until(loop_started_at + action.timestamp_seconds):
                    break
                self._execute_action(action, mouse_controller, keyboard_controller)

            if self._stop_event.is_set():
                break

            completed_loops = loop_index + 1
            self._on_progress(
                CustomLoopProgress(
                    completed_loops=completed_loops,
                    total_loops=self._config.loop_count,
                )
            )

        result = CustomLoopResult(
            completed_loops=completed_loops,
            total_loops=self._config.loop_count,
            interrupted=self._stop_event.is_set(),
        )
        self.stop()
        self._on_finish(result)

    def _wait_until(self, target_time: float) -> bool:
        while not self._stop_event.is_set():
            remaining = target_time - time.perf_counter()
            if remaining <= 0:
                return False
            self._stop_event.wait(min(remaining, 0.01))
        return True

    def _execute_action(
        self,
        action: CustomAction,
        mouse_controller: mouse.Controller,
        keyboard_controller: keyboard.Controller,
    ) -> None:
        if action.action_type == "mouse_move" and action.position is not None:
            mouse_controller.position = (action.position.x, action.position.y)
            return

        if action.action_type in {"mouse_press", "mouse_release"} and action.position is not None and action.mouse_button:
            mouse_controller.position = (action.position.x, action.position.y)
            mouse_button = getattr(mouse.Button, action.mouse_button)
            if action.action_type == "mouse_press":
                mouse_controller.press(mouse_button)
            else:
                mouse_controller.release(mouse_button)
            return

        if action.action_type in {"keyboard_press", "keyboard_release"} and action.keyboard_target is not None:
            key_target = resolve_keyboard_target(action.keyboard_target)
            if action.action_type == "keyboard_press":
                keyboard_controller.press(key_target)
            else:
                keyboard_controller.release(key_target)
