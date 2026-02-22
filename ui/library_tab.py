import tkinter as tk
from tkinter import messagebox
from config import *
import downloader
import launcher

class LibraryTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=16, pady=(16, 4))
        tk.Label(header, text="Installed Apps", bg=BG, fg=FG, font=(FONT, 13, "bold")).pack(side="left")
        tk.Button(header, text="↻ Refresh", bg=BG_CARD, fg=FG, font=(FONT, 9),
                  relief="flat", bd=0, padx=8, pady=4, cursor="hand2",
                  command=self.refresh).pack(side="right")

        container = tk.Frame(self, bg=BG)
        container.pack(fill="both", expand=True, padx=16, pady=8)

        self.canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        from tkinter import ttk
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.app_list = tk.Frame(self.canvas, bg=BG)
        self.app_list.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.app_list, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.empty_label = tk.Label(self, text="No apps installed yet.\nHead to the Store tab to find some!",
                                    bg=BG, fg=FG_DIM, font=(FONT, 11), justify="center")

    def refresh(self):
        for w in self.app_list.winfo_children():
            w.destroy()
        self.empty_label.pack_forget()

        apps = downloader.get_installed_apps()
        if not apps:
            self.empty_label.pack(expand=True)
            return

        for app in apps:
            self._make_app_card(app)

    def _make_app_card(self, app):
        card = tk.Frame(self.app_list, bg=BG_CARD, pady=12, padx=14)
        card.pack(fill="x", pady=4)

        info = tk.Frame(card, bg=BG_CARD)
        info.pack(side="left", fill="both", expand=True)

        tk.Label(info, text=app["name"], bg=BG_CARD, fg=FG, font=(FONT, 12, "bold")).pack(anchor="w")
        tk.Label(info, text=app.get("description", ""), bg=BG_CARD, fg=FG_DIM, font=(FONT, 9)).pack(anchor="w")
        tk.Label(info, text=f"v{app['version']}  •  by {app.get('author','unknown')}", bg=BG_CARD, fg=FG_DIM, font=(FONT, 8)).pack(anchor="w", pady=(4,0))

        btn_frame = tk.Frame(card, bg=BG_CARD)
        btn_frame.pack(side="right")

        tk.Button(btn_frame, text="Launch", bg=ACCENT, fg=FG, font=(FONT, 9, "bold"),
                  relief="flat", bd=0, padx=10, pady=6, cursor="hand2",
                  command=lambda a=app: self._launch(a)).pack(side="left", padx=4)

        tk.Button(btn_frame, text="Uninstall", bg="#AA3333", fg=FG, font=(FONT, 9),
                  relief="flat", bd=0, padx=10, pady=6, cursor="hand2",
                  command=lambda a=app, c=card: self._uninstall(a, c)).pack(side="left", padx=4)

    def _launch(self, app):
        try:
            launcher.launch_app(app["id"])
        except Exception as e:
            messagebox.showerror("Launch Error", str(e))

    def _uninstall(self, app, card):
        if messagebox.askyesno("Uninstall", f"Uninstall {app['name']}?"):
            downloader.uninstall_app(app["id"])
            card.destroy()
            if not downloader.get_installed_apps():
                self.empty_label.pack(expand=True)
