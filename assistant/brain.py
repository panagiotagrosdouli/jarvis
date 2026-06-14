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
            return "Πες μου ή γράψε μου κάτι για να σε βοηθήσω."

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are Jarvis, Panagiota's intelligent personal AI assistant. "
                        "You are not a simple chatbot. You must give useful, complete, structured answers. "
                        "If the user writes Greek or Greeklish, answer in natural Greek. "
                        "Do not give tiny answers unless the user asks for a tiny answer. "
                        "For normal questions, answer with: 1) clear explanation, 2) key points, "
                        "3) practical steps or examples, and 4) what to do next. "
                        "For university or scientific topics, answer academically with definitions, theory, "
                        "examples, and step-by-step reasoning. "
                        "For productivity or life organization, give an ordered action plan. "
                        "The user does not care about citations inside this local assistant; focus on being helpful, "
                        "smart, practical, and organized. "
                        "When the topic is complex, explain it deeply but simply. "
                        "When giving tasks, use numbered steps. "
                        "Always try to be encouraging without sounding fake or exaggerated."
                    ),
                },
                {"role": "user", "content": user_message},
            ],
            "stream": False,
            "options": {
                "temperature": 0.55,
                "num_predict": 900,
                "top_p": 0.9,
            },
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
            with urllib.request.urlopen(request, timeout=180) as response:
                result = json.loads(response.read().decode("utf-8"))
                message = result.get("message", {})
                content = message.get("content", "")
                return content.strip() or "Δεν μπόρεσα να δημιουργήσω απάντηση."
        except urllib.error.URLError:
            return (
                "Το Ollama δεν τρέχει. Άνοιξε terminal και γράψε: "
                f"ollama run {self.model}"
            )
        except Exception as exc:
            return f"Σφάλμα τοπικού AI: {exc}"
