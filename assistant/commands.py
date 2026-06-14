import datetime as dt
from assistant.daily_companion import DailyCompanion
from assistant.desktop import DesktopAutomation
from assistant.focus import FocusManager
from assistant.memory import Memory
from assistant.pdf_assistant import PDFAssistant
from assistant.vision import VisionAssistant
from assistant.weather import WeatherService


class CommandHandler:
    def __init__(self, memory: Memory):
        self.memory = memory
        self.desktop = DesktopAutomation()
        self.daily = DailyCompanion()
        self.weather = WeatherService()
        self.pdf = PDFAssistant()
        self.focus = FocusManager()
        self.vision = VisionAssistant()

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

        if command in {"weather", "today weather", "what is the weather", "καιρός", "τι καιρό έχει"}:
            return self.weather.summary()

        if command.startswith("weather "):
            return self.weather.summary(raw_text[8:])

        if command.startswith("καιρός "):
            return self.weather.summary(raw_text[7:])

        if command in {"analyze screen", "screen analysis", "what is on my screen", "screenshot", "analyze my screen"}:
            return self.vision.analyze_screen()

        if command.startswith("start focus"):
            return self.focus.start(raw_text[11:].strip() or "general")

        if command in {"end focus", "stop focus"}:
            return self.focus.end()

        if command in {"focus status", "current focus"}:
            return self.focus.status()

        if command in {"focus stats", "study stats"}:
            return self.focus.stats()

        if command.startswith("pdf summary "):
            return self.pdf.build_prompt(raw_text[12:], "summary")

        if command.startswith("pdf flashcards "):
            return self.pdf.build_prompt(raw_text[15:], "flashcards")

        if command.startswith("pdf quiz "):
            return self.pdf.build_prompt(raw_text[9:], "quiz")

        if command.startswith("pdf exam "):
            return self.pdf.build_prompt(raw_text[9:], "exam")

        if command in {"daily briefing", "briefing", "καλημέρα", "πρωινό"}:
            return self.daily.briefing()

        if command in {"daily lesson", "μάθημα ημέρας"}:
            return self.daily.daily_lesson()

        if command in {"daily tip", "tip", "συμβουλή"}:
            return self.daily.practical_tip()

        if command in {"study mode", "διάβασμα"}:
            return self.daily.study_mode()

        if command in {"home mode", "σπίτι"}:
            return self.daily.home_mode()

        if command in {"evening reflection", "βραδινός απολογισμός"}:
            return self.daily.evening_reflection()

        if command.startswith("add task "):
            return self.daily.add_task(raw_text[9:])

        if command.startswith("βάλε δουλειά "):
            return self.daily.add_task(raw_text[13:])

        if command in {"tasks", "show tasks", "δουλειές", "εργασίες"}:
            tasks = self.daily.list_tasks()
            if not tasks:
                return "Open tasks: none."
            return "Open tasks:\n" + "\n".join(tasks)

        if command.startswith("done "):
            return self.daily.complete_task(raw_text[5:])

        if command.startswith("ολοκλήρωσα "):
            return self.daily.complete_task(raw_text[11:])

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
            "- daily briefing\n"
            "- weather\n"
            "- analyze screen\n"
            "- add task task name\n"
            "- tasks\n"
            "- done 1\n"
            "- start focus topic\n"
            "- end focus\n"
            "- focus status\n"
            "- focus stats\n"
            "- pdf summary path/to/file.pdf\n"
            "- pdf flashcards path/to/file.pdf\n"
            "- pdf quiz path/to/file.pdf\n"
            "- pdf exam path/to/file.pdf\n"
            "- remember key=value\n"
            "- show memory\n"
            "- open google\n"
            "- open youtube\n"
            "- open app chrome\n"
            "- google search words\n"
            "- youtube search words\n"
            "- exit"
        )
