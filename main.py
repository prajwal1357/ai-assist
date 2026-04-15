from parser import parse_command
from actions import execute
import time

def main():
    print("AI Assistant (Shrey) initialized. [Full Suite Active]")
    mode = input("Select Mode - (1) Text/CLI (2) Voice/Always-On: ").strip()
    
    use_voice = mode == '2'
    
    if use_voice:
        try:
            from voice import listen_for_wake_word, listen_command, speak
        except ImportError as e:
            print("Voice modules not fully installed. Falling back to CLI mode.", e)
            use_voice = False

    while True:
        try:
            user_input = ""
            if use_voice:
                if listen_for_wake_word():
                    user_input = listen_command()
                    if not user_input:
                        speak("I didn't catch that.")
                        continue
            else:
                user_input = input("\nYou: ")
            
            if user_input.strip().lower() in ['exit', 'quit']:
                if use_voice: speak("Goodbye!")
                print("Exiting...")
                break
            
            if not user_input:
                continue

            print("Thinking...")
            # We start with empty feedback
            commands = parse_command(user_input, feedback="")

            if not commands:
                print("No clear actions found.")
                continue

            print("PARSED PLAN:", commands)

            step_feedback = []
            for cmd in commands:
                if isinstance(cmd, dict):
                    res = execute(cmd)
                    if res: step_feedback.append(res)
                else:
                    print("Invalid command format:", cmd)

            # In a full recursive planner, we could pass step_feedback back to ask_llm
            if step_feedback:
                print("Execution summary:", " | ".join(step_feedback))

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print("Error in main loop:", e)

if __name__ == "__main__":
    main()