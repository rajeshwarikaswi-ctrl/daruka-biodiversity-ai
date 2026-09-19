import httpx
from typing import Optional
from app.config import OPENAI_API_KEY, OPENAI_MODEL, OLLAMA_HOST, OLLAMA_MODEL

SYSTEM = (
    "You are an environmental scientist. ONLY rephrase the structured findings "
    "given to you. Do NOT add facts, numbers, or references not present in the input. "
    "If unsure, keep the original wording."
)

def polish(prompt: str) -> Optional[str]:
    try:
        if OPENAI_API_KEY:
            r = httpx.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                json={
                    "model": OPENAI_MODEL,
                    "messages": [{"role": "system", "content": SYSTEM},
                                 {"role": "user", "content": prompt}],
                    "temperature": 0.2,
                },
                timeout=30,
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
        if OLLAMA_HOST:
            r = httpx.post(
                f"{OLLAMA_HOST}/api/chat",
                json={"model": OLLAMA_MODEL, "stream": False,
                      "messages": [{"role": "system", "content": SYSTEM},
                                   {"role": "user", "content": prompt}]},
                timeout=60,
            )
            r.raise_for_status()
            return r.json()["message"]["content"].strip()
    except Exception:
        return None
    return None
