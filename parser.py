import json
import re
from llm import ask_llm

def clean_json_string(text):
    """Aggressively clean LLM output to extract valid JSON."""
    # Remove single-line comments ONLY outside of strings
    # We avoid stripping :// inside URLs by requiring // to be preceded by whitespace or start of line
    text = re.sub(r'(?<![:])\s*//.*?(?=\n|$)', '', text)
    # Remove multi-line comments (/* ... */)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    # Remove trailing commas before ] or }
    text = re.sub(r',\s*([}\]])', r'\1', text)
    return text.strip()

def flatten_action(obj):
    """
    Normalize LLM output into flat action dicts.
    Handles both:
      {"action": "open_browser", "url": "..."} (correct)
      {"open_browser": {"url": "..."}}          (LLM sometimes does this)
    """
    if "action" in obj:
        return obj  # Already correct format

    # Try to detect nested format: {"action_name": {fields...}}
    for key, value in obj.items():
        if isinstance(value, dict):
            flat = {"action": key}
            flat.update(value)
            return flat
        elif isinstance(value, str):
            # e.g. {"open_app": "notepad"} -> {"action": "open_app", "app": "notepad"}
            return {"action": key, "text": value}

    return obj  # Return as-is if we can't figure it out

def extract_json(text):
    """Extract JSON array from potentially messy LLM output."""
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        return clean_json_string(match.group(0))
    return None

def parse_command(user_input, feedback=""):
    raw = ask_llm(user_input, feedback)
    print("RAW:", raw)

    json_str = extract_json(raw)

    if not json_str:
        print("Could not extract JSON from LLM output.")
        return []

    try:
        data = json.loads(json_str)

        # Ensure list
        if isinstance(data, dict):
            data = [data]

        # Normalize every action to flat format
        result = []
        for i, item in enumerate(data):
            if isinstance(item, dict):
                result.append(flatten_action(item))
            elif isinstance(item, str):
                # Handle cases like ["ask", "What would you like to do?"]
                if item.lower() == "ask" and i + 1 < len(data) and isinstance(data[i + 1], str):
                    result.append({"action": "ask", "question": data[i + 1]})
                elif item.lower() in ["ask", "unknown"]:
                    result.append({"action": "ask", "question": "What would you like me to do?"})
                # Skip non-action strings (they're likely the question text already consumed)
        return result

    except Exception as e:
        print("JSON Parse Error:", e)
        print("Attempted to parse:", json_str[:300])
        return []