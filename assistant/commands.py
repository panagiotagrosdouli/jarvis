import datetime as dt
from assistant.desktop import DesktopAutomation
from assistant.memory import Memory


class CommandHandler:
    def __init__(self, memory: Memory):
        self.memory = memory
        self.desktop = DesktopAutomation()

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
            return self.memory.remember(raw_text[9:])

        if command.startswith("θυμήσου "):
            return self.memory.remember(raw_text[8:])

        if command in {"recall", "show memory", "memory", "μνήμη", "δείξε μνήμη"}:
            memories = self.memory.recall()
            if not memories:
                return "I do not have any memories yet."
            return "Here is what I remember:\n" + "\n".join(f"- {item}" for item in memories)

        if command.startswith("forget "):
            return self.memory.forget(raw_text[7:])

        if command.startswith("ξέχνα "):
            return self.memory.forget(raw_text[6:])

        if command in {"who am i", "whoami", "ποια είμαι", "ποιος είμαι"}:
            return self.memory.profile_summary()

        if command.startswith("memory "):
            key = raw_text[7:].strip().rstrip("?")
            value = self.memory.get_item(key)
            return f"{key}: {value}" if value else f"I do not know {key} yet."

        if command in {"open google", "άνοιξε google"}:
            return self.desktop.open_url("https://www.google.com")

        if command in {"open youtube", "άνοιξε youtube"}:
            return self.desktop.open_url("https://www.youtube.com")

        if command.startswith("open app "):
            return self.desktop.open_app(raw_text[9:])

        if command.startswith("άνοιξε εφαρμογή "):
            return self.desktop.open_app(raw_text[16:])

        if command.startswith("google "):
            return self.desktop.search_google(raw_text[7:])

        if command.startswith("youtube "):
            return self.desktop.search_youtube(raw_text[8:])

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
            "- open google\n"
            "- open youtube\n"
            "- open app chrome\n"
            "- open app vscode\n"
            "- open app spotify\n"
            "- google search words\n"
            "- youtube search words\n"
            "- exit"
        )
