import os
import pyautogui

def execute(cmd):
    action = cmd.get("action")

    if action == "open_app" or action == "open":
        app = cmd.get("app", "").lower()

        if "chrome" in app:
            os.system("start chrome")
        elif "notepad" in app:
            os.system("start notepad")
        else:
            print("App not supported yet")

    elif action == "type_text":
        text = cmd.get("text", "")
        pyautogui.write(text)

    else:
        print("Unhandled action:", action)