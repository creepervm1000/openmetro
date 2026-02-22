# OpenMetro

**Bring back full-screen Metro apps on Windows 10.**

OpenMetro is an open platform for building and distributing Metro-style fullscreen apps on Windows, built on web technologies. Apps are written in HTML/CSS/JS, distributed through a static store hosted on Cloudflare Pages, and managed by a lightweight Python desktop client.

---

## What is this?

Windows 8/8.1 had a unique fullscreen app paradigm called Metro. Windows 10 killed it. OpenMetro brings it back — with a modern twist. Instead of a proprietary runtime, apps are just web pages. Anyone who knows HTML can build an OpenMetro app.

---

## Repos

| Repo | Purpose |
|------|---------|
| [openmetro](https://github.com/creepervm1000/openmetro) | Client source code (this repo) |
| [openmetro-server](https://github.com/creepervm1000/openmetro-server) | Store server — app registry and packages |

---

## Client

The client is a Metro-styled Python/tkinter desktop app with two tabs:

- **Store** — browse, search, and install apps from the OpenMetro store
- **Library** — manage and launch installed apps

Apps open fullscreen via pywebview with a Win8.1-style hover titlebar (move your cursor to the top of the screen to reveal it). A home button returns you to the client. Installed apps are registered in the Windows Start Menu automatically.

### Requirements

- Python 3.12 or 3.13
- `pip install requests pywebview`

### Run from source

```
git clone https://github.com/creepervm1000/openmetro
cd openmetro/client
pip install requests pywebview
python main.py
```

### Build with PyInstaller

```
pip install pyinstaller
cd client
pyinstaller openmetro.spec
```

Output: `dist/openmetro.exe`

---

## Building an App

An OpenMetro app is a folder of HTML/CSS/JS with an `index.html` entry point. No framework, no SDK, no special APIs required. Apps run fullscreen in a Chromium webview. The hover titlebar is injected automatically by the runner.

### Example app structure
```
my-app/
└── index.html
```

### Submitting to the store

1. Fork [openmetro-server](https://github.com/creepervm1000/openmetro-server)
2. Add your app source to `apps/my-app/src/`
3. Create `apps/my-app/metadata.json` (copy from an existing app)
4. Run `python publish.py ./apps/my-app/src my-app 1.0.0`
5. Add your app to `index.json`
6. Open a pull request

---

## Architecture

```
GitHub (openmetro-server)
    └── Cloudflare Pages  (openmetro-src.creepernet.qzz.io)
            └── Client fetches index.json
                    └── Downloads .zip directly from CF Pages
                            └── Extracts to ~/.openmetro/apps/
                                    └── Opens fullscreen via pywebview
```

No backend server. No database. No rate limit issues. Cloudflare handles DDoS protection automatically.

---

## License

MIT
