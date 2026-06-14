import datetime as dt
import webbrowser
from assistant.memory import Memory


class CommandHandler:
    def __init__(self, memory: Memory):
        self.memory = memory

    def handle(self, text: str) -> str | None:
        command = text.strip().lower()

        if command in {"help", "commands"}:
            return self.help_text()

        if command in {"exit", "quit", "bye"}:
            return "EXIT"

        if command == "time":
            now = dt.datetime.now().strftime("%H:%M")
            return f"The current time is {now}."

        if command.startswith("remember "):
            content = text.strip()[9:]
            return self.memory.remember(content)

        if command == "recall":
            memories = self.memory.recall()
            if not memories:
                return "I do not have any memories yet."
            return "Here is what I remember:\n" + "\n".join(f"- {item}" for item in memories)

        if command == "open youtube":
            webbrowser.open("https://www.youtube.com")
            return "Opening YouTube."

        if command == "open google":
            webbrowser.open("https://www.google.com")
            return "Opening Google."

        return None

    @staticmethod
    def help_text() -> str:
        return (
            "Available commands:\n"
            "- help\n"
            "- time\n"
            "- remember <something>\n"
            "- recall\n"
            "- open youtube\n"
            "- open google\n"
            "- exit"
        )
