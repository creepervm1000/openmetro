import tkinter as tk
from tkinter import ttk, messagebox
import threading
from config import *
import store as store_api
import downloader
import launcher

class StoreTab(tk.Frame):
    def __init__(self, parent, on_library_refresh=None):
        super().__init__(parent, bg=BG)
        self.on_library_refresh = on_library_refresh
        self.registry = []
        self.download_threads = {}

        self._build_ui()
        self._load_store()

    def _build_ui(self):
        # Search bar
        search_frame = tk.Frame(self, bg=BG)
        search_frame.pack(fill="x", padx=16, pady=(16, 8))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search)
        search_entry = tk.Entry(
            search_frame, textvariable=self.search_var,
            bg=BG_CARD, fg=FG, insertbackground=FG,
            font=(FONT, 11), relief="flat", bd=8
        )
        search_entry.pack(fill="x")
        search_entry.insert(0, "Search apps...")
        search_entry.bind("<FocusIn>", lambda e: search_entry.delete(0, "end") if search_entry.get() == "Search apps..." else None)

        # Status label
        self.status_label = tk.Label(self, text="Loading store...", bg=BG, fg=FG_DIM, font=(FONT, 9))
        self.status_label.pack(anchor="w", padx=16)

        # Scrollable app list
        container = tk.Frame(self, bg=BG)
        container.pack(fill="both", expand=True, padx=16, pady=8)

        self.canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.app_list = tk.Frame(self.canvas, bg=BG)

        self.app_list.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.app_list, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(-1*(e.delta//120), "units"))

    def _load_store(self):
        def fetch():
            try:
                self.registry = store_api.fetch_registry()
                self.after(0, lambda: self._render_apps(self.registry))
                self.after(0, lambda: self.status_label.config(text=f"{len(self.registry)} apps available"))
            except Exception as e:
                self.after(0, lambda: self.status_label.config(text=f"Failed to load store: {e}"))
        threading.Thread(target=fetch, daemon=True).start()

    def _on_search(self, *_):
        if not hasattr(self, 'app_list'):
            return
        q = self.search_var.get().strip()
        if q and q != "Search apps...":
            results = store_api.search_apps(q, self.registry)
        else:
            results = self.registry
        self._render_apps(results)

    def _render_apps(self, apps):
        for w in self.app_list.winfo_children():
            w.destroy()

        for app in apps:
            self._make_app_card(app)

    def _make_app_card(self, app):
        card = tk.Frame(self.app_list, bg=BG_CARD, pady=12, padx=14, cursor="hand2")
        card.pack(fill="x", pady=4)

        # Left: info
        info = tk.Frame(card, bg=BG_CARD)
        info.pack(side="left", fill="both", expand=True)

        tk.Label(info, text=app["name"], bg=BG_CARD, fg=FG, font=(FONT, 12, "bold")).pack(anchor="w")
        tk.Label(info, text=app.get("description", ""), bg=BG_CARD, fg=FG_DIM, font=(FONT, 9), wraplength=380, justify="left").pack(anchor="w")
        tk.Label(info, text=f"v{app['version']}  •  {app.get('author','')}", bg=BG_CARD, fg=FG_DIM, font=(FONT, 8)).pack(anchor="w", pady=(4,0))

        # Right: button + progress
        right = tk.Frame(card, bg=BG_CARD)
        right.pack(side="right", padx=(8,0))

        installed = downloader.is_installed(app["id"])
        has_update = downloader.is_update_available(app) if installed else False

        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(right, variable=progress_var, maximum=100, length=100)
        btn_text = "Update" if has_update else ("Launch" if installed else "Install")
        btn_color = "#FF8C00" if has_update else (ACCENT if not installed else "#333")

        btn = tk.Button(
            right, text=btn_text, bg=btn_color, fg=FG,
            font=(FONT, 9, "bold"), relief="flat", bd=0,
            padx=12, pady=6, cursor="hand2"
        )
        btn.config(command=lambda a=app, b=btn, pv=progress_var, pb=progress_bar: self._handle_btn(a, b, pv, pb))
        btn.pack()

        card.bind("<Enter>", lambda e, c=card: c.config(bg=BG_HOVER))
        card.bind("<Leave>", lambda e, c=card: c.config(bg=BG_CARD))

    def _handle_btn(self, app, btn, progress_var, progress_bar):
        if downloader.is_installed(app["id"]) and not downloader.is_update_available(app):
            # Launch
            try:
                launcher.launch_app(app["id"])
            except Exception as e:
                messagebox.showerror("Launch Error", str(e))
            return

        # Install or update
        btn.config(text="...", state="disabled")
        progress_bar.pack(pady=(4,0))

        def do_download():
            try:
                def on_progress(dl, total):
                    if total:
                        pct = (dl / total) * 100
                        self.after(0, lambda: progress_var.set(pct))

                downloader.download_app(app, progress_callback=on_progress)
                self.after(0, lambda: btn.config(text="Launch", bg="#333", state="normal"))
                self.after(0, lambda: progress_bar.pack_forget())
                if self.on_library_refresh:
                    self.after(0, self.on_library_refresh)
            except Exception as e:
                self.after(0, lambda: btn.config(text="Retry", state="normal"))
                self.after(0, lambda: progress_bar.pack_forget())
                self.after(0, lambda err=e: messagebox.showerror("Download Error", str(err)))

        threading.Thread(target=do_download, daemon=True).start()
