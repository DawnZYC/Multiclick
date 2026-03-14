import ctypes
import sys
from tkinter import Tk

from multiclick.ui.main_window import MainWindow


def _enable_windows_dpi_awareness() -> None:
    if not sys.platform.startswith("win"):
        return

    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        return
    except Exception:
        pass

    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


def run() -> None:
    _enable_windows_dpi_awareness()
    root = Tk()
    window = MainWindow(root)
    root.protocol("WM_DELETE_WINDOW", window.close)
    root.mainloop()
