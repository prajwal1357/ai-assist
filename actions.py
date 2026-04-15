import os
import time
import pyautogui
from pywinauto import Application

app_instance = None

def execute(cmd):
    global app_instance

    action = cmd.get("action")

    if action == "open_app":
        app = cmd.get("app", "").lower()

        if "notepad" in app:
            try:
                # Windows 11 Notepad UWP workaround:
                os.system("start notepad")
                time.sleep(1.5)  # Give the app time to render
                
                from pywinauto import Desktop
                # Find all Notepad windows
                windows = Desktop(backend="uia").windows(title_re=".*Notepad.*")
                if windows:
                    # Target the first found Notepad window's process to avoid ambiguity
                    target_pid = windows[0].process_id()
                    app_instance = Application(backend="uia").connect(process=target_pid)
                    # Bring it to front
                    app_instance.top_window().set_focus()
                else:
                    print("Could not find a Notepad window.")
            except Exception as e:
                print("Failed to start or connect to notepad:", e)
        else:
            print(f"Currently only notepad is supported. Requested: {app}")

    elif action == "type_text":
        text = cmd.get("text", "")

        try:
            if app_instance:
                window = app_instance.top_window()
                window.set_focus()   # 👈 IMPORTANT
                window.type_keys(text, with_spaces=True)
            else:
                print("No active app")
        except Exception as e:
            print("Typing failed:", e)

    else:
        print("Unhandled action:", action)