"""
OpenMetro Installer
"""
import sys
import os
import shutil
import subprocess
import tempfile
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

INSTALL_DIR = Path(os.environ.get("LOCALAPPDATA", "C:/Users/Default/AppData/Local")) / "OpenMetro"
START_MENU = Path(os.environ.get("APPDATA", "")) / "Microsoft/Windows/Start Menu/Programs/OpenMetro"
EXE_NAME = "openmetro.exe"
APP_NAME = "OpenMetro"

if getattr(sys, "frozen", False):
    BASE = Path(sys._MEIPASS)
else:
    BASE = Path(__file__).parent

SOURCE_EXE = BASE / EXE_NAME

ACCENT = "#0078D4"
BG = "#1E1E1E"
FG = "#FFFFFF"
FG_DIM = "#AAAAAA"
FONT = "Segoe UI"


class Installer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OpenMetro Setup")
        self.geometry("480x320")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.overrideredirect(True)
        self._center()
        self._build_ui()
        self._check_source()

    def _center(self):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"480x320+{(sw-480)//2}+{(sh-320)//2}")

    def _build_ui(self):
        bar = tk.Frame(self, bg=ACCENT, height=36)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        tk.Label(bar, text="  OpenMetro Setup", bg=ACCENT, fg=FG,
                 font=(FONT, 10, "bold")).pack(side="left", padx=4)
        tk.Button(bar, text="✕", bg=ACCENT, fg=FG, font=(FONT, 10),
                  relief="flat", bd=0, padx=10, cursor="hand2",
                  command=self.destroy).pack(side="right")
        bar.bind("<ButtonPress-1>", self._start_drag)
        bar.bind("<B1-Motion>", self._drag)

        logo_frame = tk.Frame(self, bg=BG)
        logo_frame.pack(pady=(24, 0))
        canvas = tk.Canvas(logo_frame, width=48, height=48, bg=BG, highlightthickness=0)
        canvas.pack()
        canvas.create_rectangle(0, 0, 22, 22, fill="#0078D4", outline="")
        canvas.create_rectangle(26, 0, 48, 22, fill="#00B4D8", outline="")
        canvas.create_rectangle(0, 26, 22, 48, fill="#744DA9", outline="")
        canvas.create_rectangle(26, 26, 48, 48, fill="#FF8C00", outline="")

        tk.Label(self, text="OpenMetro", bg=BG, fg=FG,
                 font=(FONT, 18, "bold")).pack(pady=(8, 2))
        tk.Label(self, text="Metro apps, brought back.", bg=BG, fg=FG_DIM,
                 font=(FONT, 9)).pack()

        path_frame = tk.Frame(self, bg=BG)
        path_frame.pack(fill="x", padx=32, pady=(20, 0))
        tk.Label(path_frame, text="Install location:", bg=BG, fg=FG_DIM,
                 font=(FONT, 8)).pack(anchor="w")
        tk.Label(path_frame, text=str(INSTALL_DIR), bg=BG, fg=FG,
                 font=(FONT, 9)).pack(anchor="w")

        self.startup_var = tk.BooleanVar(value=False)
        tk.Checkbutton(self, text="Launch OpenMetro on startup", variable=self.startup_var,
                       bg=BG, fg=FG_DIM, selectcolor=BG, activebackground=BG,
                       activeforeground=FG, font=(FONT, 9)).pack(pady=(12, 0))

        self.progress = ttk.Progressbar(self, length=400, mode="determinate")

        self.status = tk.Label(self, text="", bg=BG, fg=FG_DIM, font=(FONT, 8))
        self.status.pack(pady=(4, 0))

        self.install_btn = tk.Button(
            self, text="Install", bg=ACCENT, fg=FG,
            font=(FONT, 10, "bold"), relief="flat", bd=0,
            padx=32, pady=8, cursor="hand2",
            command=self._install
        )
        self.install_btn.pack(pady=(12, 0))

    def _check_source(self):
        if not SOURCE_EXE.exists():
            messagebox.showerror("Error", f"Bundled {EXE_NAME} not found. Please rebuild the installer.")
            self.destroy()

    def _set_status(self, text):
        self.status.config(text=text)
        self.update_idletasks()

    def _step(self, value):
        self.progress["value"] = value
        self.update_idletasks()

    def _install(self):
        self.install_btn.config(state="disabled", text="Installing...")
        self.progress.pack(pady=(8, 0))
        self._step(0)

        try:
            self._set_status("Creating install directory...")
            INSTALL_DIR.mkdir(parents=True, exist_ok=True)
            self._step(20)

            self._set_status("Copying files...")
            dest = INSTALL_DIR / EXE_NAME
            shutil.copy2(SOURCE_EXE, dest)
            self._step(50)

            self._set_status("Creating Start Menu shortcut...")
            self._create_shortcut(
                name=APP_NAME,
                target=str(dest),
                folder=START_MENU,
                description="OpenMetro — Metro apps for Windows 10"
            )
            self._step(75)

            if self.startup_var.get():
                self._set_status("Adding to startup...")
                self._add_to_startup(dest)
            self._step(90)

            self._step(100)
            self._set_status("Installation complete!")
            self.install_btn.config(
                text="Launch OpenMetro", state="normal",
                bg="#107C10",
                command=lambda: (subprocess.Popen([str(dest)]), self.destroy())
            )

        except Exception as e:
            self._set_status(f"Error: {e}")
            self.install_btn.config(text="Retry", state="normal")

    def _create_shortcut(self, name, target, folder, description=""):
        folder = Path(folder)
        shortcut = folder / f"{name}.lnk"
        ps = f"""New-Item -ItemType Directory -Force -Path '{folder}' | Out-Null
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut('{shortcut}')
$s.TargetPath = '{target}'
$s.Arguments = ''
$s.WorkingDirectory = '{INSTALL_DIR}'
$s.Description = '{description}'
$s.Save()
"""
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".ps1", delete=False, encoding="utf-8")
        tmp.write(ps)
        tmp.close()
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", tmp.name],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        os.unlink(tmp.name)

    def _add_to_startup(self, exe_path):
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "OpenMetro", 0, winreg.REG_SZ, str(exe_path))
        winreg.CloseKey(key)

    def _start_drag(self, e):
        self._dx, self._dy = e.x, e.y

    def _drag(self, e):
        self.geometry(f"+{self.winfo_x()+e.x-self._dx}+{self.winfo_y()+e.y-self._dy}")


if __name__ == "__main__":
    app = Installer()
    app.mainloop()
