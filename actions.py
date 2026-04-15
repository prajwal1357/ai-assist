import os
import time
import pyautogui
import webbrowser
from pywinauto import Application, Desktop

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    HAVE_SELENIUM = True
except ImportError:
    HAVE_SELENIUM = False

app_instance = None
browser_driver = None

def get_browser():
    global browser_driver
    if not browser_driver:
        if HAVE_SELENIUM:
            try:
                options = webdriver.EdgeOptions()
                options.add_experimental_option("detach", True)
                browser_driver = webdriver.Edge(options=options)
            except Exception:
                options = webdriver.ChromeOptions()
                options.add_experimental_option("detach", True)
                browser_driver = webdriver.Chrome(options=options)
    return browser_driver

def execute(cmd):
    global app_instance

    action = cmd.get("action")
    feedback = ""

    if action == "open_app":
        app = cmd.get("app", "").lower()
        if "notepad" in app:
            try:
                os.system("start notepad")
                time.sleep(1.5)
                from pywinauto import Desktop
                windows = Desktop(backend="uia").windows(title_re=".*Notepad.*")
                if windows:
                    target_pid = windows[0].process_id()
                    app_instance = Application(backend="uia").connect(process=target_pid)
                    app_instance.top_window().set_focus()
                    feedback = "Notepad opened successfully."
                else:
                    feedback = "Could not find a Notepad window after launch."
                    print(feedback)
            except Exception as e:
                feedback = f"Failed to start or connect to notepad: {e}"
                print(feedback)
        else:
            try:
                os.system(f"start {app}")
                feedback = f"Opened {app} using generic command."
            except Exception as e:
                feedback = f"Failed to open app {app}: {e}"
                print(feedback)

    elif action == "type_text":
        text = cmd.get("text", "")
        # Use pywinauto if linked, else pyautogui
        if app_instance:
            try:
                window = app_instance.top_window()
                window.set_focus()
                window.type_keys(text, with_spaces=True)
                feedback = f"Typed '{text}' via pywinauto."
            except Exception as e:
                print(f"Pywinauto typing failed: {e}. Falling back to PyAutoGUI.")
                pyautogui.write(text, interval=0.02)
                feedback = f"Typed '{text}' via PyAutoGUI."
        else:
            pyautogui.write(text, interval=0.02)
            feedback = f"Typed '{text}' via PyAutoGUI."

    elif action == "hotkey":
        keys = cmd.get("keys", "")
        if keys:
            key_list = [k.strip() for k in keys.split(",")]
            pyautogui.hotkey(*key_list)
            feedback = f"Pressed hotkey {keys}."

    elif action == "open_browser":
        url = cmd.get("url", "")
        if url:
            if not url.startswith("http"):
                url = "https://" + url
            if HAVE_SELENIUM:
                try:
                    driver = get_browser()
                    driver.get(url)
                    feedback = f"Selenium navigated to: {url}"
                except Exception as e:
                    print("Selenium fail, fallback to webbrowser:", e)
                    webbrowser.open(url)
                    feedback = f"Opened browser via native fallback: {url}"
            else:
                webbrowser.open(url)
                feedback = f"Opened browser via native fallback: {url}"

    elif action == "browser_search":
        query = cmd.get("text", "")
        if query:
            if HAVE_SELENIUM:
                try:
                    driver = get_browser()
                    driver.get("https://www.google.com")
                    search_box = driver.find_element(By.NAME, "q")
                    search_box.send_keys(query)
                    search_box.send_keys(Keys.RETURN)
                    feedback = f"Searched google for '{query}'"
                except Exception as e:
                    print(f"Browser search failed: {e}")
                    feedback = "Selenium search failed."
            else:
                webbrowser.open(f"https://www.google.com/search?q={query}")
                feedback = "Searched via native browser."

    elif action == "ask":
        question = cmd.get("question", "")
        if not question: question = "Can you provide more details?"
        print(f"\n[Shrey]: {question}")
        try:
            from voice import speak
            speak(question)
        except:
            pass
        ans = input("You: ")
        feedback = f"User answered: {ans}"

    elif action == "remember":
        key = cmd.get("key", "")
        val = cmd.get("value", "")
        if key and val:
            from memory import save_memory
            save_memory(key, val)
            print(f"-> Learned: {key} = {val}")
            feedback = f"Remembered {key} over persistent memory."

    else:
        feedback = f"Unhandled action {action}"
        print(feedback)

    return feedback