import json
import os
import urllib.error
import urllib.request

from dotenv import load_dotenv
from assistant.speech import get_language

load_dotenv()


class Brain:
    def __init__(self):
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    def answer(self, user_message: str) -> str:
        if not user_message.strip():
            return "Please say or type something." if get_language() == "en" else "Πες μου ή γράψε μου κάτι για να σε βοηθήσω."

        if get_language() == "el":
            language_rule = "Always answer in natural Greek, even if the user writes Greeklish."
        else:
            language_rule = "Always answer in clear natural English, unless the user explicitly asks for Greek."

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are Jarvis, Panagiota's intelligent personal AI assistant. "
                        "You are not a simple chatbot. You must give useful, complete, structured answers. "
                        f"{language_rule} "
                        "Do not give tiny answers unless the user asks for a tiny answer. "
                        "For normal questions, answer with: 1) clear explanation, 2) key points, "
                        "3) practical steps or examples, and 4) what to do next. "
                        "For university or scientific topics, answer academically with definitions, theory, "
                        "examples, and step-by-step reasoning. "
                        "For productivity or life organization, give an ordered action plan. "
                        "Focus on being helpful, smart, practical, and organized. "
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
                if content.strip():
                    return content.strip()
                return "I could not generate a response." if get_language() == "en" else "Δεν μπόρεσα να δημιουργήσω απάντηση."
        except urllib.error.URLError:
            if get_language() == "en":
                return f"Ollama is not running. Open a terminal and run: ollama run {self.model}"
            return f"Το Ollama δεν τρέχει. Άνοιξε terminal και γράψε: ollama run {self.model}"
        except Exception as exc:
            return f"Local AI error: {exc}" if get_language() == "en" else f"Σφάλμα τοπικού AI: {exc}"
