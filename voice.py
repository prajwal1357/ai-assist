import pyttsx3
import speech_recognition as sr

def speak(text):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 160)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[TTS Disabled] Said: {text}")

def listen_for_wake_word(wake_word="hello"):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print(f"\n[Listening for wake word '{wake_word}']...")
        r.adjust_for_ambient_noise(source)
        while True:
            try:
                audio = r.listen(source, timeout=10, phrase_time_limit=3)
                text = r.recognize_google(audio).lower()
                if wake_word in text:
                    print("[Wake word detected!]")
                    speak("Yes?")
                    return True
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except Exception as e:
                print("Voice module error:", e)
                return False

def listen_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n[Listening for command...]")
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=15)
            text = r.recognize_google(audio)
            print(f"You (Voice): {text}")
            return text
        except sr.UnknownValueError:
            return None
        except Exception:
            return None
