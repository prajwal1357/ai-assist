from parser import parse_command
from actions import execute

def main():
    print("AI Assistant Phase 1. Type 'exit' to quit.")
    while True:
        try:
            user_input = input("You: ")
            if user_input.strip().lower() in ['exit', 'quit']:
                break
            
            commands = parse_command(user_input)

            print("PARSED:", commands)

            for cmd in commands:
                if isinstance(cmd, dict):
                    execute(cmd)
                else:
                    print("Invalid command format:", cmd)

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print("Error in main loop:", e)

if __name__ == "__main__":
    main()