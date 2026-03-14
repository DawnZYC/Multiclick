import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from multiclick.models import ClickMode, ClickPosition, ClickProgress, ClickResult
from multiclick.services.mouse_clicker import MouseClickRunner
from multiclick.services.position_capture import PositionCaptureService
from multiclick.ui import messages
from multiclick.validation import ValidationError, build_mouse_click_config


class MainWindow:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(messages.WINDOW_TITLE)
        self.root.resizable(False, False)

        self.mode_var = tk.StringVar(value=ClickMode.MOUSE.value)
        self.interval_var = tk.StringVar(value="0.1")
        self.duration_var = tk.StringVar(value="10")
        self.position_var = tk.StringVar(value=messages.DEFAULT_POSITION_TEXT)
        self.status_var = tk.StringVar(value=messages.default_status(ClickMode.MOUSE))

        self._selected_position: Optional[ClickPosition] = None
        self._capture_service: Optional[PositionCaptureService] = None
        self._click_runner: Optional[MouseClickRunner] = None

        self._build_layout()
        self._apply_window_size()
        self._refresh_mode_state()

    def close(self) -> None:
        if self._capture_service is not None:
            self._capture_service.stop()
            self._capture_service = None

        if self._click_runner is not None:
            self._click_runner.stop()
            self._click_runner = None

        self.root.quit()
        self.root.destroy()

    def _apply_window_size(self) -> None:
        self.root.update_idletasks()
        required_width = max(self.root.winfo_reqwidth() + 24, messages.WINDOW_MIN_WIDTH)
        required_height = max(self.root.winfo_reqheight() + 24, messages.WINDOW_MIN_HEIGHT)
        self.root.geometry(f"{required_width}x{required_height}")
        self.root.minsize(required_width, required_height)

    def _build_layout(self) -> None:
        container = ttk.Frame(self.root, padding=18)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Multiclick", font=("Microsoft YaHei UI", 18, "bold")).pack(anchor="w")
        ttk.Label(
            container,
            text="当前版本先实现鼠标连点，键盘连点入口已预留。",
            font=("Microsoft YaHei UI", 10),
            foreground="#4f4f4f",
        ).pack(anchor="w", pady=(4, 14))

        mode_frame = ttk.LabelFrame(container, text="模式选择", padding=12)
        mode_frame.pack(fill="x")
        ttk.Radiobutton(
            mode_frame,
            text="鼠标连点",
            value=ClickMode.MOUSE.value,
            variable=self.mode_var,
            command=self._refresh_mode_state,
        ).grid(row=0, column=0, sticky="w", padx=(0, 24))
        ttk.Radiobutton(
            mode_frame,
            text="键盘连点",
            value=ClickMode.KEYBOARD.value,
            variable=self.mode_var,
            command=self._refresh_mode_state,
        ).grid(row=0, column=1, sticky="w")

        form_frame = ttk.LabelFrame(container, text="鼠标连点参数", padding=12)
        form_frame.pack(fill="x", pady=14)
        form_frame.columnconfigure(1, weight=1)

        ttk.Label(form_frame, text="点击间隔时间（秒）").grid(row=0, column=0, sticky="w", pady=6)
        self.interval_entry = ttk.Entry(form_frame, textvariable=self.interval_var)
        self.interval_entry.grid(row=0, column=1, sticky="ew", pady=6)

        ttk.Label(form_frame, text="点击位置").grid(row=1, column=0, sticky="w", pady=6)
        position_frame = ttk.Frame(form_frame)
        position_frame.grid(row=1, column=1, sticky="ew", pady=6)
        position_frame.columnconfigure(0, weight=1)

        self.position_label = ttk.Label(
            position_frame,
            textvariable=self.position_var,
            anchor="w",
            relief="sunken",
            padding=(8, 4),
        )
        self.position_label.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.capture_button = ttk.Button(position_frame, text="设置位置", command=self.start_position_capture)
        self.capture_button.grid(row=0, column=1)

        ttk.Label(form_frame, text="连点时间（秒）").grid(row=2, column=0, sticky="w", pady=6)
        self.duration_entry = ttk.Entry(form_frame, textvariable=self.duration_var)
        self.duration_entry.grid(row=2, column=1, sticky="ew", pady=6)

        ttk.Label(
            form_frame,
            text="运行中按 Esc 可中断。设置位置时也可按 Esc 取消捕获。",
            font=("Microsoft YaHei UI", 9),
            foreground="#5c5c5c",
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(8, 0))

        action_frame = ttk.Frame(container)
        action_frame.pack(fill="x")

        self.start_button = ttk.Button(action_frame, text="开始连点", command=self.start_clicking)
        self.start_button.pack(side="left")

        self.stop_button = ttk.Button(action_frame, text="停止", command=self.stop_clicking)
        self.stop_button.pack(side="left", padx=10)

        status_frame = ttk.LabelFrame(container, text="状态", padding=12)
        status_frame.pack(fill="both", expand=True, pady=(14, 0))
        ttk.Label(
            status_frame,
            textvariable=self.status_var,
            justify="left",
            anchor="nw",
            font=("Microsoft YaHei UI", 10),
        ).pack(fill="both", expand=True)

    def _selected_mode(self) -> ClickMode:
        return ClickMode(self.mode_var.get())

    def _refresh_mode_state(self, reset_status: bool = True) -> None:
        state = "normal" if self._selected_mode() is ClickMode.MOUSE else "disabled"
        start_state = state if self._click_runner is None else "disabled"
        stop_state = "normal" if self._click_runner is not None else "disabled"

        self.interval_entry.configure(state=state)
        self.duration_entry.configure(state=state)
        capture_state = state if self._capture_service is None and self._click_runner is None else "disabled"
        self.capture_button.configure(state=capture_state)
        self.start_button.configure(state=start_state)
        self.stop_button.configure(state=stop_state)

        if reset_status and self._click_runner is None and self._capture_service is None:
            self.status_var.set(messages.default_status(self._selected_mode()))

    def start_position_capture(self) -> None:
        if self._capture_service is not None:
            return

        self.status_var.set(messages.capture_status())
        self.capture_button.configure(state="disabled")
        self.root.iconify()

        self._capture_service = PositionCaptureService(
            on_captured=lambda position: self.root.after(0, self._handle_position_captured, position),
            on_cancelled=lambda: self.root.after(0, self._handle_capture_cancelled),
        )
        self._capture_service.start()

    def _handle_position_captured(self, position: ClickPosition) -> None:
        self._capture_service = None
        self._selected_position = position
        self.position_var.set(position.display_text)

        self.status_var.set(messages.position_selected_status(position))
        self._restore_window()
        self._refresh_mode_state(reset_status=False)

    def _handle_capture_cancelled(self) -> None:
        self._capture_service = None
        self.status_var.set(messages.capture_cancelled_status())
        self._restore_window()
        self._refresh_mode_state(reset_status=False)

    def _restore_window(self) -> None:
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def start_clicking(self) -> None:
        if self._click_runner is not None:
            return

        if self._selected_mode() is ClickMode.KEYBOARD:
            messagebox.showinfo("暂未开放", "当前版本只支持鼠标连点。")
            return

        try:
            config = build_mouse_click_config(
                interval_raw=self.interval_var.get(),
                duration_raw=self.duration_var.get(),
                position=self._selected_position,
            )
        except ValidationError as exc:
            messagebox.showerror("参数错误", str(exc))
            return

        self._click_runner = MouseClickRunner(
            config=config,
            on_progress=lambda progress: self.root.after(0, self._handle_progress, progress),
            on_finish=lambda result: self.root.after(0, self._handle_finish, result),
        )
        self.status_var.set(messages.running_status(config))
        self._refresh_mode_state(reset_status=False)
        self._click_runner.start()

    def stop_clicking(self) -> None:
        if self._click_runner is not None:
            self._click_runner.stop()

    def _handle_progress(self, progress: ClickProgress) -> None:
        self.status_var.set(messages.progress_status(progress))

    def _handle_finish(self, result: ClickResult) -> None:
        self._click_runner = None
        self.status_var.set(messages.finished_status(result))
        self._refresh_mode_state(reset_status=False)

        if result.interrupted:
            messagebox.showinfo("连点已中断", f"鼠标连点已中断，共点击 {result.click_count} 次。")
        else:
            messagebox.showinfo("连点已完成", f"鼠标连点已完成，共点击 {result.click_count} 次。")
