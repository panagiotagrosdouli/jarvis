import datetime as dt
import webbrowser
from assistant.memory import Memory


class CommandHandler:
    def __init__(self, memory: Memory):
        self.memory = memory

    def handle(self, text: str) -> str | None:
        raw_text = text.strip()
        command = raw_text.lower()

        if command in {"help", "commands", "βοήθεια", "εντολές"}:
            return self.help_text()

        if command in {"exit", "quit", "bye", "έξοδος", "σταμάτα"}:
            return "EXIT"

        if command in {"time", "ώρα", "τι ώρα είναι"}:
            now = dt.datetime.now().strftime("%H:%M")
            return f"The current time is {now}."

        if command.startswith("remember "):
            content = raw_text[9:]
            return self.memory.remember(content)

        if command.startswith("θυμήσου "):
            content = raw_text[8:]
            return self.memory.remember(content)

        if command in {"recall", "show memory", "memory", "μνήμη", "δείξε μνήμη"}:
            memories = self.memory.recall()
            if not memories:
                return "I do not have any memories yet."
            return "Here is what I remember:\n" + "\n".join(f"- {item}" for item in memories)

        if command.startswith("forget "):
            key = raw_text[7:]
            return self.memory.forget(key)

        if command.startswith("ξέχνα "):
            key = raw_text[6:]
            return self.memory.forget(key)

        if command in {"who am i", "whoami", "ποια είμαι", "ποιος είμαι"}:
            return self.memory.profile_summary()

        if command.startswith("memory "):
            key = raw_text[7:].strip().rstrip("?")
            value = self.memory.get_item(key)
            if value is None:
                return f"I do not know {key} yet."
            return f"{key}: {value}"

        if command.startswith("what do you know about "):
            key = raw_text[24:].strip().rstrip("?")
            value = self.memory.get_item(key)
            if value is None:
                return f"I do not have a saved memory for {key} yet."
            return f"{key}: {value}"

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
            "- help / βοήθεια\n"
            "- time / ώρα\n"
            "- remember key=value\n"
            "- θυμήσου key=value\n"
            "- show memory / μνήμη\n"
            "- forget key / ξέχνα key\n"
            "- who am i\n"
            "- memory key\n"
            "- what do you know about key\n"
            "- open youtube\n"
            "- open google\n"
            "- exit"
        )
