import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional, Union

from multiclick.models import ClickMode, ClickPosition, ClickProgress, ClickResult, KeyboardTarget
from multiclick.services.keyboard_capture import KeyboardCaptureService
from multiclick.services.keyboard_clicker import KeyboardClickRunner
from multiclick.services.mouse_clicker import MouseClickRunner
from multiclick.services.position_capture import PositionCaptureService
from multiclick.ui import messages
from multiclick.validation import ValidationError, build_keyboard_click_config, build_mouse_click_config


class MainWindow:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(messages.WINDOW_TITLE)
        self.root.resizable(False, False)

        self.mode_var = tk.StringVar(value=ClickMode.MOUSE.value)
        self.interval_var = tk.StringVar(value="0.1")
        self.duration_var = tk.StringVar(value="10")
        self.target_var = tk.StringVar(value=messages.DEFAULT_POSITION_TEXT)
        self.status_var = tk.StringVar(value=messages.default_status(ClickMode.MOUSE))

        self._selected_position: Optional[ClickPosition] = None
        self._selected_key: Optional[KeyboardTarget] = None
        self._capture_service: Optional[Union[PositionCaptureService, KeyboardCaptureService]] = None
        self._click_runner: Optional[Union[MouseClickRunner, KeyboardClickRunner]] = None
        self._active_run_mode: Optional[ClickMode] = None

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
        self.subtitle_label = ttk.Label(
            container,
            text=messages.subtitle_text(),
            font=("Microsoft YaHei UI", 10),
            foreground="#4f4f4f",
        )
        self.subtitle_label.pack(anchor="w", pady=(4, 14))

        mode_frame = ttk.LabelFrame(container, text="模式选择", padding=12)
        mode_frame.pack(fill="x")
        self.mouse_mode_button = ttk.Radiobutton(
            mode_frame,
            text="鼠标连点",
            value=ClickMode.MOUSE.value,
            variable=self.mode_var,
            command=self._refresh_mode_state,
        )
        self.mouse_mode_button.grid(row=0, column=0, sticky="w", padx=(0, 24))
        self.keyboard_mode_button = ttk.Radiobutton(
            mode_frame,
            text="键盘连点",
            value=ClickMode.KEYBOARD.value,
            variable=self.mode_var,
            command=self._refresh_mode_state,
        )
        self.keyboard_mode_button.grid(row=0, column=1, sticky="w")

        self.form_frame = ttk.LabelFrame(container, text="", padding=12)
        self.form_frame.pack(fill="x", pady=14)
        self.form_frame.columnconfigure(1, weight=1)

        ttk.Label(self.form_frame, text="点击间隔时间（秒）").grid(row=0, column=0, sticky="w", pady=6)
        self.interval_entry = ttk.Entry(self.form_frame, textvariable=self.interval_var)
        self.interval_entry.grid(row=0, column=1, sticky="ew", pady=6)

        self.target_name_label = ttk.Label(self.form_frame, text="")
        self.target_name_label.grid(row=1, column=0, sticky="w", pady=6)
        target_frame = ttk.Frame(self.form_frame)
        target_frame.grid(row=1, column=1, sticky="ew", pady=6)
        target_frame.columnconfigure(0, weight=1)

        self.target_display_label = ttk.Label(
            target_frame,
            textvariable=self.target_var,
            anchor="w",
            relief="sunken",
            padding=(8, 4),
        )
        self.target_display_label.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.capture_button = ttk.Button(target_frame, text="", command=self.start_target_capture)
        self.capture_button.grid(row=0, column=1)

        ttk.Label(self.form_frame, text="连点时间（秒）").grid(row=2, column=0, sticky="w", pady=6)
        self.duration_entry = ttk.Entry(self.form_frame, textvariable=self.duration_var)
        self.duration_entry.grid(row=2, column=1, sticky="ew", pady=6)

        self.hint_label = ttk.Label(
            self.form_frame,
            text="",
            font=("Microsoft YaHei UI", 9),
            foreground="#5c5c5c",
        )
        self.hint_label.grid(row=3, column=0, columnspan=2, sticky="w", pady=(8, 0))

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
        mode = self._selected_mode()
        inputs_enabled = self._capture_service is None and self._click_runner is None
        common_state = "normal" if inputs_enabled else "disabled"
        stop_state = "normal" if self._click_runner is not None else "disabled"

        self.mouse_mode_button.configure(state=common_state)
        self.keyboard_mode_button.configure(state=common_state)
        self.interval_entry.configure(state=common_state)
        self.duration_entry.configure(state=common_state)
        self.capture_button.configure(state=common_state)
        self.start_button.configure(state=common_state)
        self.stop_button.configure(state=stop_state)
        self._apply_mode_visuals(mode)

        if reset_status and self._click_runner is None and self._capture_service is None:
            self.status_var.set(messages.default_status(mode))

    def _apply_mode_visuals(self, mode: ClickMode) -> None:
        self.form_frame.configure(text=messages.parameter_frame_title(mode))
        self.target_name_label.configure(text=messages.target_label_text(mode))
        self.capture_button.configure(text=messages.capture_button_text(mode))
        self.hint_label.configure(text=messages.capture_hint(mode))
        self.target_var.set(self._selected_target_text(mode))

    def _selected_target_text(self, mode: ClickMode) -> str:
        if mode is ClickMode.KEYBOARD and self._selected_key is not None:
            return self._selected_key.display_text
        if mode is ClickMode.MOUSE and self._selected_position is not None:
            return self._selected_position.display_text
        return messages.DEFAULT_POSITION_TEXT

    def start_target_capture(self) -> None:
        if self._capture_service is not None:
            return

        mode = self._selected_mode()
        self.status_var.set(messages.capture_status(mode))
        self.capture_button.configure(state="disabled")
        self.root.iconify()

        if mode is ClickMode.MOUSE:
            self._capture_service = PositionCaptureService(
                on_captured=lambda position: self.root.after(0, self._handle_position_captured, position),
                on_cancelled=lambda: self.root.after(0, self._handle_capture_cancelled, ClickMode.MOUSE),
            )
        else:
            self._capture_service = KeyboardCaptureService(
                on_captured=lambda target: self.root.after(0, self._handle_key_captured, target),
                on_cancelled=lambda: self.root.after(0, self._handle_capture_cancelled, ClickMode.KEYBOARD),
            )
        self._capture_service.start()

    def _handle_position_captured(self, position: ClickPosition) -> None:
        self._capture_service = None
        self._selected_position = position
        self.target_var.set(position.display_text)
        self.status_var.set(messages.mouse_target_selected_status(position))
        self._restore_window()
        self._refresh_mode_state(reset_status=False)

    def _handle_key_captured(self, target: KeyboardTarget) -> None:
        self._capture_service = None
        self._selected_key = target
        self.target_var.set(target.display_text)
        self.status_var.set(messages.keyboard_target_selected_status(target))
        self._restore_window()
        self._refresh_mode_state(reset_status=False)

    def _handle_capture_cancelled(self, mode: ClickMode) -> None:
        self._capture_service = None
        self.status_var.set(messages.capture_cancelled_status(mode))
        self._restore_window()
        self._refresh_mode_state(reset_status=False)

    def _restore_window(self) -> None:
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def start_clicking(self) -> None:
        if self._click_runner is not None:
            return

        mode = self._selected_mode()

        try:
            if mode is ClickMode.MOUSE:
                config = build_mouse_click_config(
                    interval_raw=self.interval_var.get(),
                    duration_raw=self.duration_var.get(),
                    position=self._selected_position,
                )
                self._click_runner = MouseClickRunner(
                    config=config,
                    on_progress=lambda progress: self.root.after(0, self._handle_progress, progress),
                    on_finish=lambda result: self.root.after(0, self._handle_finish, result),
                )
                self.status_var.set(messages.mouse_running_status(config))
            else:
                config = build_keyboard_click_config(
                    interval_raw=self.interval_var.get(),
                    duration_raw=self.duration_var.get(),
                    target=self._selected_key,
                )
                self._click_runner = KeyboardClickRunner(
                    config=config,
                    on_progress=lambda progress: self.root.after(0, self._handle_progress, progress),
                    on_finish=lambda result: self.root.after(0, self._handle_finish, result),
                )
                self.status_var.set(messages.keyboard_running_status(config))
        except ValidationError as exc:
            messagebox.showerror("参数错误", str(exc))
            return

        self._active_run_mode = mode
        self._refresh_mode_state(reset_status=False)
        self._click_runner.start()

    def stop_clicking(self) -> None:
        if self._click_runner is not None:
            self._click_runner.stop()

    def _handle_progress(self, progress: ClickProgress) -> None:
        if self._active_run_mode is ClickMode.KEYBOARD:
            self.status_var.set(messages.keyboard_progress_status(progress))
        else:
            self.status_var.set(messages.mouse_progress_status(progress))

    def _handle_finish(self, result: ClickResult) -> None:
        completed_mode = self._active_run_mode or ClickMode.MOUSE
        self._click_runner = None
        self._active_run_mode = None

        if completed_mode is ClickMode.KEYBOARD:
            finished_text = messages.keyboard_finished_status(result)
        else:
            finished_text = messages.mouse_finished_status(result)

        self.status_var.set(finished_text)
        self._refresh_mode_state(reset_status=False)

        if result.interrupted:
            messagebox.showinfo("连点已中断", finished_text)
        else:
            messagebox.showinfo("连点已完成", finished_text)
