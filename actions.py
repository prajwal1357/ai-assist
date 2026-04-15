import os
import time
import webbrowser
import urllib.parse
import pyautogui
from pywinauto import Application, Desktop

app_instance = None

# Map of common app names to their Windows launch commands/protocols
APP_LAUNCH_MAP = {
    "whatsapp": "whatsapp://",
    "telegram": "tg://",
    "discord": "discord://",
    "spotify": "spotify://",
    "slack": "slack://",
    "teams": "msteams://",
    "settings": "ms-settings:",
    "store": "ms-windows-store:",
    "calculator": "calc.exe",
    "notepad": "notepad.exe",
    "paint": "mspaint.exe",
    "wordpad": "wordpad.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "explorer": "explorer.exe",
    "chrome": "chrome",
    "brave": "brave",
    "firefox": "firefox",
    "edge": "msedge",
}

def launch_app(app_name):
    """Reliably launch any Windows app by name."""
    app = app_name.lower().strip()

    # Check our known map first
    if app in APP_LAUNCH_MAP:
        target = APP_LAUNCH_MAP[app]
        try:
            if "://" in target or target.endswith(":"):
                # UWP protocol-based app
                os.startfile(target)
            elif target.endswith(".exe"):
                # Classic Win32 executable
                os.system(f"start \"\" \"{target}\"")
            else:
                # Browser-type apps
                os.system(f"start {target}")
            return f"Opened {app} successfully."
        except Exception as e:
            return f"Failed to open {app}: {e}"
    else:
        # Fallback: try generic start command
        try:
            os.system(f"start {app}")
            return f"Opened {app} via generic start."
        except Exception as e:
            return f"Failed to open {app}: {e}"


def execute(cmd):
    global app_instance

    action = cmd.get("action")
    feedback = ""

    # ─── OPEN APP ─────────────────────────────────────────
    if action == "open_app":
        app = cmd.get("app", "").lower().strip()
        if "notepad" in app:
            try:
                os.system("start notepad")
                time.sleep(1.5)
                windows = Desktop(backend="uia").windows(title_re=".*Notepad.*")
                if windows:
                    target_pid = windows[0].process_id()
                    app_instance = Application(backend="uia").connect(process=target_pid)
                    app_instance.top_window().set_focus()
                    feedback = "Notepad opened successfully."
                else:
                    feedback = "Could not find Notepad window."
                    print(feedback)
            except Exception as e:
                feedback = f"Failed to open notepad: {e}"
                print(feedback)
        else:
            feedback = launch_app(app)

    # ─── TYPE TEXT ────────────────────────────────────────
    elif action == "type_text":
        text = cmd.get("text", "")
        if not text:
            feedback = "No text provided to type."
        elif app_instance:
            try:
                window = app_instance.top_window()
                window.set_focus()
                window.type_keys(text, with_spaces=True)
                feedback = f"Typed '{text}' via pywinauto."
            except Exception as e:
                print(f"Pywinauto typing failed: {e}. Falling back to PyAutoGUI.")
                pyautogui.write(text, interval=0.02)
                feedback = f"Typed '{text}' via PyAutoGUI fallback."
        else:
            pyautogui.write(text, interval=0.02)
            feedback = f"Typed '{text}' via PyAutoGUI."

    # ─── HOTKEY ───────────────────────────────────────────
    elif action == "hotkey":
        keys = cmd.get("keys", "")
        if keys:
            key_list = [k.strip() for k in keys.split(",")]
            pyautogui.hotkey(*key_list)
            feedback = f"Pressed hotkey: {keys}"

    # ─── PRESS KEY ────────────────────────────────────────
    elif action == "press":
        key = cmd.get("key", "")
        if key:
            pyautogui.press(key.lower().strip())
            feedback = f"Pressed key: {key}"

    # ─── SLEEP ────────────────────────────────────────────
    elif action == "sleep":
        duration = float(cmd.get("duration", 1))
        time.sleep(duration)
        feedback = f"Waited {duration}s."

    # ─── OPEN BROWSER URL ────────────────────────────────
    elif action == "open_browser":
        url = cmd.get("url", "")
        if url:
            if not url.startswith("http"):
                url = "https://" + url
            webbrowser.open(url)
            feedback = f"Opened browser: {url}"

    # ─── BROWSER SEARCH (Google/YouTube) ─────────────────
    elif action == "browser_search":
        query = cmd.get("text", "")
        platform = cmd.get("platform", "google").lower()
        if query:
            encoded = urllib.parse.quote_plus(query)
            if "youtube" in platform:
                url = f"https://www.youtube.com/results?search_query={encoded}"
            else:
                url = f"https://www.google.com/search?q={encoded}"
            webbrowser.open(url)
            feedback = f"Searched '{query}' on {platform}."

    # ─── ASK (handled by main.py) ─────────────────────────
    elif action == "ask":
        # Handled by the orchestration loop in main.py
        pass

    # ─── REMEMBER ─────────────────────────────────────────
    elif action == "remember":
        key = cmd.get("key", "")
        val = cmd.get("value", "")
        if key and val:
            from memory import save_memory
            save_memory(key, val)
            print(f"-> Learned: {key} = {val}")
            feedback = f"Remembered {key}."

    # ─── UNKNOWN ──────────────────────────────────────────
    else:
        feedback = f"Unhandled action: {action}"
        print(feedback)

    return feedback