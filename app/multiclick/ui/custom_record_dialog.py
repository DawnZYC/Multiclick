import tkinter as tk
from tkinter import ttk
from typing import Callable


class CustomRecordDialog:
    def __init__(
        self,
        parent: tk.Tk,
        on_start: Callable[[], None],
        on_close: Callable[[], None],
    ) -> None:
        self._on_start = on_start
        self._on_close = on_close
        self.window = tk.Toplevel(parent)
        self.window.title("自定义循环录制")
        self.window.resizable(False, False)
        self.window.attributes("-topmost", True)
        self.window.transient(parent)
        self.window.protocol("WM_DELETE_WINDOW", self.close)

        frame = ttk.Frame(self.window, padding=18)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="点击“开始自定义”后开始录制键盘鼠标动作，按 Esc 保存。",
            justify="left",
            font=("Microsoft YaHei UI", 10),
        ).pack(anchor="w", pady=(0, 14))

        self.start_button = ttk.Button(frame, text="开始自定义", command=self._handle_start)
        self.start_button.pack(anchor="center")

        self.window.grab_set()
        self.window.focus_force()

    def _handle_start(self) -> None:
        self.start_button.configure(state="disabled")
        self._on_start()

    def close(self) -> None:
        try:
            self.window.grab_release()
        except tk.TclError:
            pass
        if self.window.winfo_exists():
            self.window.destroy()
        self._on_close()
