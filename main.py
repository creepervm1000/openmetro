import sys
import os

# --- Runner mode (launched as subprocess to open an app fullscreen) ---
if "--run" in sys.argv:
    idx = sys.argv.index("--run")
    if len(sys.argv) >= idx + 3:
        # Inject runner logic directly
        entry = sys.argv[idx + 1]
        name = sys.argv[idx + 2]
        # Rewrite argv so runner.py logic works
        sys.argv = [sys.argv[0], entry, name]
        import runpy
        from pathlib import Path
        runner_path = Path(__file__).parent / "runner.py"
        if runner_path.exists():
            runpy.run_path(str(runner_path), run_name="__main__")
        else:
            # Frozen - runner code is embedded
            from runner import main as runner_main
            runner_main()
    sys.exit(0)

# --- Normal client GUI mode ---
import tkinter as tk
from tkinter import ttk
from config import *
from ui.store_tab import StoreTab
from ui.library_tab import LibraryTab
from pathlib import Path
ico = Path(__file__).parent / "openmetro.ico"

class OpenMetroClient(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("OpenMetro")
        self.geometry("700x560")
        self.minsize(560, 400)
        self.configure(bg=BG)
        if ico.exists():
            self.iconbitmap(str(ico))
        self._apply_style()
        self._build_ui()

    def _apply_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=BG_CARD, foreground=FG_DIM,
                         font=(FONT, 10), padding=(16, 8), borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", FG)])
        style.configure("Vertical.TScrollbar", background=BG_CARD, troughcolor=BG,
                         borderwidth=0, arrowcolor=FG_DIM)
        style.configure("TProgressbar", troughcolor=BG_CARD, background=ACCENT, borderwidth=0)

    def _build_ui(self):
        titlebar = tk.Frame(self, bg=ACCENT, height=40)
        titlebar.pack(fill="x")
        titlebar.pack_propagate(False)

        tk.Label(titlebar, text="  OpenMetro", bg=ACCENT, fg=FG,
                 font=(FONT, 12, "bold")).pack(side="left", padx=4)

        close_btn = tk.Button(titlebar, text="✕", bg=ACCENT, fg=FG,
                              font=(FONT, 11), relief="flat", bd=0,
                              padx=12, cursor="hand2", command=self.destroy)
        close_btn.pack(side="right")
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg="#C42B1C"))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg=ACCENT))

        titlebar.bind("<ButtonPress-1>", self._start_drag)
        titlebar.bind("<B1-Motion>", self._drag)

        self.overrideredirect(True)
        self._center_window()
        self._fix_taskbar()

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        self.library_tab = LibraryTab(notebook)
        self.store_tab = StoreTab(notebook, on_library_refresh=self.library_tab.refresh)

        notebook.add(self.store_tab, text="  Store  ")
        notebook.add(self.library_tab, text="  Library  ")

    def _center_window(self):
        self.update_idletasks()
        w, h = 700, 560
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _fix_taskbar(self):
        if sys.platform != "win32":
            return
        import ctypes
        self.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
        GWL_EXSTYLE = -20
        WS_EX_APPWINDOW = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style = (style & ~WS_EX_TOOLWINDOW) | WS_EX_APPWINDOW
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        self.withdraw()
        self.after(10, self.deiconify)

    def _start_drag(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _drag(self, event):
        x = self.winfo_x() + (event.x - self._drag_x)
        y = self.winfo_y() + (event.y - self._drag_y)
        self.geometry(f"+{x}+{y}")


def main():
    app = OpenMetroClient()
    app.mainloop()

if __name__ == "__main__":
    main()
