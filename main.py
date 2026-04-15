import sys
from parser import parse_command
from actions import execute
import time

def main():
    print("AI Assistant (Shrey) initialized. [Continuous Dynamic Suite]")
    mode = input("Select Mode - (1) Text/CLI (2) Voice/Always-On: ").strip()
    
    use_voice = mode == '2'
    is_awake = False
    conversation_history = []
    
    if use_voice:
        try:
            from voice import listen_for_wake_word, listen_command, speak
        except ImportError as e:
            print("Voice modules not fully installed. Falling back to CLI mode.", e)
            use_voice = False

    while True:
        try:
            # 1. Listen Phase
            user_input = ""
            if use_voice:
                if not is_awake:
                    if listen_for_wake_word():
                        is_awake = True
                    else:
                        continue
                
                user_input = listen_command()
                
                if not user_input:
                    speak("Going back to standby.")
                    is_awake = False
                    continue
                    
                if any(word in user_input.lower() for word in ['bye', 'goodbye', 'stop', 'standby', 'sleep']):
                    speak("Alright, standing by! Say Shrey to wake me up.")
                    is_awake = False
                    continue
            else:
                user_input = input("\n[Listening] You: ")
                if user_input.strip().lower() in ['exit', 'quit', 'bye']:
                    print("Exiting...")
                    break
                if not user_input:
                    continue

            # 2. Planning and Execution Phase
            current_request = user_input
            feedback_str = ""
            
            # Build context from recent conversation history
            if conversation_history:
                context = " | ".join(conversation_history[-5:])  # Last 5 interactions
                feedback_str = f"Recent conversation context: [{context}]"
            
            while True:
                print("Thinking...")
                commands = parse_command(current_request, feedback=feedback_str)

                if not commands:
                    print("No explicit actions. Reverting to listen mode.")
                    break

                step_feedback = []
                asked_question = False
                
                for cmd in commands:
                    if not isinstance(cmd, dict): continue
                    
                    if cmd.get("action") == "ask":
                        question = cmd.get("question", "Can you provide more details?")
                        print(f"\n[Shrey Asks]: {question}")
                        if use_voice:
                            from voice import speak, listen_command
                            speak(question)
                            ans = listen_command()
                        else:
                            ans = input("Your Answer: ")
                            
                        # Feed the user's answer immediately back to the LLM to continue planning
                        feedback_str = f"AI asked: '{question}'. User answered: '{ans}'. Proceed with the action using this info."
                        asked_question = True
                        break # Stop macro block and let LLM rethink!
                    else:
                        res = execute(cmd)
                        if res: step_feedback.append(res)
                
                if asked_question:
                    # Recursive loop! LLM gets pinged instantly with 'current_request' + the new 'feedback_str'
                    continue
                else:
                    # Log this interaction into conversation history
                    summary = f"User said: '{user_input}'"
                    if step_feedback:
                        summary += f" -> Result: {', '.join(step_feedback)}"
                    conversation_history.append(summary)
                    # Keep history manageable
                    if len(conversation_history) > 10:
                        conversation_history = conversation_history[-10:]
                    break # Everything executed properly, break to outer listen phase
                    
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print("Error in main loop:", e)

if __name__ == "__main__":
    main()