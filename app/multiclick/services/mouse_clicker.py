import threading
import time
from collections.abc import Callable
from typing import Optional, Union

from pynput import keyboard, mouse

from multiclick.models import ClickProgress, ClickResult, MouseClickConfig


class MouseClickRunner:
    def __init__(
        self,
        config: MouseClickConfig,
        on_progress: Callable[[ClickProgress], None],
        on_finish: Callable[[ClickResult], None],
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
        click_controller = mouse.Controller()
        end_time = time.time() + self._config.duration_seconds
        click_count = 0

        def handle_key_press(key: Union[keyboard.Key, keyboard.KeyCode]) -> bool:
            if key == keyboard.Key.esc:
                self._stop_event.set()
                return False
            return True

        self._keyboard_listener = keyboard.Listener(on_press=handle_key_press)
        self._keyboard_listener.start()

        while not self._stop_event.is_set():
            current_time = time.time()
            if current_time >= end_time:
                break

            click_controller.position = (self._config.position.x, self._config.position.y)
            click_controller.click(mouse.Button.left)
            click_count += 1

            self._on_progress(
                ClickProgress(
                    click_count=click_count,
                    remaining_seconds=max(0.0, end_time - current_time),
                )
            )

            if self._stop_event.wait(self._config.interval_seconds):
                break

        result = ClickResult(click_count=click_count, interrupted=self._stop_event.is_set())
        self.stop()
        self._on_finish(result)
