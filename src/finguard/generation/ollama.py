import json
import re
from urllib.request import Request, urlopen


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3:4b"

def _remove_thinking(text: str) -> str:
    """Remove model reasoning from the returned answer."""

    if "</think>" in text:
        text = text.split("</think>", 1)[1]

    return text.strip()

def generate_answer( question: str,context: str,) -> str:
    """Generate an answer grounded in retrieved document context."""

    system_prompt = (
        "You are a financial policy assistant. "
        "Answer the user's question using only the supplied context. "
        "Do not use outside knowledge. "
        "If the context does not contain enough information to answer, "
        "say: 'I don't have enough information in the provided documents.' "
        "Keep the answer concise."
    )

    user_prompt = f"""Question:{question}
Context:{context} """

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        "stream": False,
        "think": False,
    }

    request = Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=300) as response:
        result = json.loads(response.read().decode("utf-8"))

    return _remove_thinking(result["message"]["content"])