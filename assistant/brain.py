import os
from openai import OpenAI


class Brain:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def answer(self, user_message: str) -> str:
        if not user_message.strip():
            return "Please say or type something."

        if self.client is None:
            return (
                "I am running in offline mode. Add OPENAI_API_KEY to your .env file "
                "to enable AI responses."
            )

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Jarvis, a helpful personal assistant. "
                        "Answer clearly, safely, and practically."
                    ),
                },
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content or "I could not generate a response."
