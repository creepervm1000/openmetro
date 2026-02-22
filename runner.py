"""
runner.py — launched as a subprocess to open an app fullscreen.
Usage: python runner.py <path_to_index.html> <app_name>
"""
import sys

TITLEBAR_JS = """
(function() {
    var bar = document.createElement('div');
    bar.id = '__om_titlebar';
    bar.innerHTML = `
        <div id="__om_left">
            <button id="__om_home" title="Start">&#x2756;</button>
            <span id="__om_title"></span>
        </div>
        <div id="__om_controls">
            <button id="__om_close">&#x2715;</button>
        </div>
    `;
    document.body.appendChild(bar);

    var style = document.createElement('style');
    style.textContent = `
        #__om_titlebar {
            position: fixed;
            top: -56px;
            left: 0; right: 0;
            height: 24px;
            background: rgba(0,0,0,0.88);
            backdrop-filter: blur(8px);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 8px 0 4px;
            z-index: 999999;
            transition: top 0.15s ease;
            font-family: 'Segoe UI', sans-serif;
            box-sizing: border-box;
        }
        #__om_titlebar.visible {
            top: 0;
        }
        #__om_left {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        #__om_title {
            color: #fff;
            font-size: 13px;
            font-weight: 400;
            letter-spacing: 0.5px;
            opacity: 0.9;
            user-select: none;
        }
        #__om_controls {
            display: flex;
            gap: 4px;
        }
        #__om_home, #__om_close {
            background: transparent;
            border: none;
            color: #fff;
            font-size: 16px;
            width: 40px;
            height: 36px;
            cursor: pointer;
            border-radius: 2px;
            transition: background 0.1s;
        }
        #__om_home:hover {
            background: #0078D4;
        }
        #__om_close:hover {
            background: #C42B1C;
        }
        #__om_trigger {
            position: fixed;
            top: 0; left: 0; right: 0;
            height: 4px;
            z-index: 1000000;
        }
    `;
    document.head.appendChild(style);

    document.getElementById('__om_title').textContent = document.title || 'OpenMetro App';

    var trigger = document.createElement('div');
    trigger.id = '__om_trigger';
    document.body.appendChild(trigger);

    var hideTimer = null;

    function showBar() {
        clearTimeout(hideTimer);
        bar.classList.add('visible');
    }

    function hideBar() {
        clearTimeout(hideTimer);
        bar.classList.remove('visible');
    }

    document.addEventListener('mousemove', function(e) {
        if (e.clientY <= 48) {
            showBar();
        } else {
            clearTimeout(hideTimer);
            hideTimer = setTimeout(hideBar, 400);
        }
    });

    document.getElementById('__om_close').addEventListener('click', function() {
        pywebview.api.close();
    });

    document.getElementById('__om_home').addEventListener('click', function() {
        pywebview.api.go_home();
    });
})();
"""

def main():
    if len(sys.argv) < 3:
        print("Usage: runner.py <entry_html> <app_name>")
        sys.exit(1)

    entry = sys.argv[1]
    name = sys.argv[2]

    try:
        import webview
    except ImportError:
        import webbrowser
        webbrowser.open(f"file:///{entry}")
        print("pywebview not installed - opened in browser instead.")
        return

    class Api:
        def close(self):
            window.destroy()

        def go_home(self):
            # Minimize this app window and bring the OpenMetro client to front
            import ctypes
            import subprocess
            import sys as _sys

            # Minimize the webview window
            hwnd = ctypes.windll.user32.FindWindowW(None, name)
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 6)  # SW_MINIMIZE

            # Bring OpenMetro client to foreground by finding its window
            client_hwnd = ctypes.windll.user32.FindWindowW(None, "OpenMetro")
            if client_hwnd:
                ctypes.windll.user32.ShowWindow(client_hwnd, 9)   # SW_RESTORE
                ctypes.windll.user32.SetForegroundWindow(client_hwnd)

    api = Api()
    window = webview.create_window(
        name,
        url=f"file:///{entry}",
        fullscreen=True,
        frameless=True,
        easy_drag=False,
        js_api=api,
    )

    def on_loaded():
        window.evaluate_js(TITLEBAR_JS)

    window.events.loaded += on_loaded
    webview.start(debug=False, private_mode=False, http_server=True)

if __name__ == "__main__":
    main()
