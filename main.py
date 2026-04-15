from parser import parse_command
from actions import execute

while True:
    user_input = input("You: ")
    
    cmd = parse_command(user_input)
    print("PARSED:", cmd)

    execute(cmd)