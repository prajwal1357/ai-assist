import sys
from parser import parse_command
from actions import execute
import time

def safe_speak(text, use_voice):
    """Always speak out loud if voice mode is on, print otherwise."""
    print(f"\n[jarvis]: {text}")
    if use_voice:
        try:
            from voice import speak
            speak(text)
        except Exception:
            pass

def safe_listen(use_voice):
    """Listen via mic if voice mode, otherwise read from keyboard."""
    if use_voice:
        try:
            from voice import listen_command
            return listen_command()
        except Exception:
            return input("Your Answer: ")
    else:
        return input("Your Answer: ")

def main():
    print("AI Assistant (jarvis) initialized. [Continuous Dynamic Suite]")
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
                
                # Stay awake! Keep trying to listen until we get something
                max_retries = 3
                for attempt in range(max_retries):
                    user_input = listen_command()
                    if user_input:
                        break
                    if attempt < max_retries - 1:
                        safe_speak("I didn't catch that. Say it again.", use_voice)
                
                if not user_input:
                    safe_speak("Still listening. Just say something when you're ready.", use_voice)
                    continue  # Stay awake! Do NOT go to standby
                    
                # ONLY go to sleep if user explicitly says so
                if any(word in user_input.lower() for word in ['bye', 'goodbye', 'standby', 'go to sleep']):
                    safe_speak("Alright, going to standby. Say my name to wake me up!", use_voice)
                    is_awake = False
                    continue
            else:
                user_input = input("\n[Listening] You: ")
                if user_input.strip().lower() in ['exit', 'quit']:
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
                    safe_speak("I'm not sure what to do with that. Can you rephrase?", use_voice)
                    break

                step_feedback = []
                asked_question = False
                
                for cmd in commands:
                    if not isinstance(cmd, dict): continue
                    
                    if cmd.get("action") == "ask":
                        question = cmd.get("question", "Can you provide more details?")
                        
                        # Speak the question out loud
                        safe_speak(question, use_voice)
                        
                        # Listen for the answer
                        ans = safe_listen(use_voice)
                        
                        if not ans:
                            safe_speak("I didn't hear your answer. Let me ask again.", use_voice)
                            ans = safe_listen(use_voice)
                            
                        if ans:
                            # Feed the user's answer immediately back to the LLM to continue planning
                            feedback_str = f"AI asked: '{question}'. User answered: '{ans}'. Proceed with the action using this info."
                            # Also append to conversation history
                            conversation_history.append(f"AI asked: '{question}' -> User answered: '{ans}'")
                        else:
                            feedback_str = f"AI asked: '{question}'. User did not answer. Ask again or try a different approach."
                        
                        asked_question = True
                        break  # Stop macro block and let LLM rethink!
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
                    
                    # Confirm completion via voice
                    safe_speak("Done!", use_voice)
                    break  # Everything executed properly, break to outer listen phase
                    
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print("Error in main loop:", e)

if __name__ == "__main__":
    main()