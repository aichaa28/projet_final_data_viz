import os
import requests
from dotenv import load_dotenv

load_dotenv()
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

def ask_claude(prompt):
    url = "https://api.anthropic.com/v1/complete"
    headers = {"x-api-key": CLAUDE_API_KEY, "Content-Type": "application/json"}
    data = {"model": "claude-2", "prompt": prompt, "max_tokens": 200}
    
    response = requests.post(url, headers=headers, json=data)
    return response.json().get("completion", "Erreur API")
