import requests

def ask_llm(user_input):
    prompt = f"""
You are a system assistant.

Return ONLY JSON.

STRICT RULES:
- Use ONLY these actions:
  - open_app
  - type_text
  - unknown

Format:
{{
  "action": "",
  "app": "",
  "text": ""
}}

User: {user_input}
"""

    res = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
    )

    data = res.json()
    return data.get("response", "")