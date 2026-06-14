import json
import os
import urllib.error
import urllib.request

from dotenv import load_dotenv

load_dotenv()


class Brain:
    def __init__(self):
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    def answer(self, user_message: str) -> str:
        if not user_message.strip():
            return "Please say or type something."

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are Jarvis, a helpful personal desktop assistant. "
                        "Answer clearly, safely, and practically. "
                        "If the user writes Greek or Greeklish, answer in Greek."
                    ),
                },
                {"role": "user", "content": user_message},
            ],
            "stream": False,
        }

        url = f"{self.base_url.rstrip('/')}/api/chat"
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                result = json.loads(response.read().decode("utf-8"))
                message = result.get("message", {})
                return message.get("content", "I could not generate a local AI response.")
        except urllib.error.URLError:
            return (
                "Ollama is not running. Install Ollama and run a model first: "
                f"ollama run {self.model}"
            )
        except Exception as exc:
            return f"Local AI error: {exc}"
