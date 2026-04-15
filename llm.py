import requests
import json
from memory import get_all_memories

def ask_llm(user_input, feedback=""):
    memories = get_all_memories()
    memory_context = json.dumps(memories) if memories else "None"

    feedback_text = f"\nSystem Feedback from previous step: {feedback}\n" if feedback else ""

    prompt = f"""
You are an advanced system assistant named Shrey.

MEMORY CONTEXT:
{memory_context}

Return a strict JSON ARRAY of actions to fulfill the user request.
Break it down into logical steps. Do not include introductory text, markdown formatting outside of the JSON block, or conversational filler. ONLY return valid JSON.

Allowed actions:
1. open_app (app name)
2. type_text (text to type)
3. hotkey (keys to press, e.g. "ctrl,c")
4. open_browser (url)
5. browser_search (query text)
6. remember (key, value)
7. ask (question to ask user for clarification)

Format:
[
  {{
    "action": "open_app",
    "app": "chrome",
    "text": "",
    "url": "",
    "keys": "",
    "question": "",
    "key": "",
    "value": ""
  }}
]

User: {user_input}{feedback_text}
"""

    try:
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
        )
        res.raise_for_status()
        data = res.json()
        return data.get("response", "[]")
    except requests.exceptions.RequestException as e:
        print(f"LLM Connection Error: {e}")
        return "[]"