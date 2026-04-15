import json
import re
from llm import ask_llm

def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)
    return None

def parse_command(user_input):
    raw = ask_llm(user_input)
    print("RAW:", raw)

    json_str = extract_json(raw)

    if not json_str:
        return {"action": "unknown"}

    try:
        return json.loads(json_str)
    except:
        return {"action": "unknown"}