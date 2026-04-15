import requests

def ask_llm(user_input):
    prompt = f"""
You are a system assistant.

Return a JSON ARRAY of actions.

STRICT RULES:
- Output must be a LIST []
- Each item must be an object
- No explanation
- No extra text

Allowed actions:
- open_app
- type_text
- ask
- unknown

Format:
[
  {{
    "action": "",
    "app": "",
    "text": "",
    "question": ""
  }}
]

Examples:

User: open chrome and type hello
[
  {{ "action": "open_app", "app": "chrome", "text": "", "question": "" }},
  {{ "action": "type_text", "app": "", "text": "hello", "question": "" }}
]

User: {user_input}
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
        return data.get("response", "")
    except requests.exceptions.RequestException as e:
        print(f"LLM Connection Error: {e}")
        return "[]"