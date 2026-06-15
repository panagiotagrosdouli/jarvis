import datetime as dt
from assistant.care_coach import CareCoach
from assistant.daily_companion import DailyCompanion
from assistant.desktop import DesktopAutomation
from assistant.focus import FocusManager
from assistant.jarvis_core import JarvisCore
from assistant.memory import Memory
from assistant.mission import MissionManager
from assistant.pdf_assistant import PDFAssistant
from assistant.smart_memory import SmartMemory
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
        self.care = CareCoach()
        self.smart = SmartMemory()
        self.core = JarvisCore()
        self.mission = MissionManager()

    def handle(self, text: str) -> str | None:
        raw_text = text.strip()
        command = raw_text.lower()

        parsed_exam = self.smart.parse_exam_sentence(raw_text)
        if parsed_exam:
            return parsed_exam
        parsed_goal = self.smart.parse_goal_sentence(raw_text)
        if parsed_goal:
            return parsed_goal

        if command in {"help", "commands"}:
            return self.help_text()
        if command in {"exit", "quit", "bye", "stop"}:
            return "EXIT"
        if command in {"time", "what time is it"}:
            return f"The current time is {dt.datetime.now().strftime('%H:%M')}."

        if command.startswith("create mission "):
            return self.mission.create_mission(raw_text[15:])
        if command in {"show mission", "mission status", "active mission"}:
            return self.mission.show_mission()
        if command in {"mission briefing", "mission"}:
            return self.mission.mission_briefing()
        if command.startswith("complete objective "):
            return self.mission.complete_objective(raw_text[19:])
        if command.startswith("add objective "):
            return self.mission.add_objective(raw_text[14:])

        if command in {"jarvis status", "status", "system status"}:
            return self.core.status()
        if command in {"what should i do now", "what now"}:
            return self.core.recommend_next_action()
        if command in {"what should i study", "study priority"}:
            return self.core.what_should_i_study()
        if command.startswith("prepare me for "):
            return self.core.prepare_for_exam(raw_text[15:].replace(" exam", "").strip())
        if command.startswith("prepare for "):
            return self.core.prepare_for_exam(raw_text[12:].replace(" exam", "").strip())
        if command in {"prepare me for exam", "exam prep", "study plan"}:
            return self.core.prepare_for_exam()
        if command in {"daily intelligence", "intelligence briefing"}:
            return self.core.daily_intelligence()

        if command.startswith("add exam "):
            parts = raw_text[9:].split(" on ", 1)
            if len(parts) == 2:
                subject = parts[0]
                date_part = parts[1]
                time_text = ""
                if " at " in date_part:
                    date_part, time_text = date_part.split(" at ", 1)
                return self.smart.add_exam(subject, date_part, time_text)
            return "Use: add exam Computer Networks on 2026-06-17 at 09:00"
        if command in {"show exams", "exams", "my exams"}:
            return self.smart.list_exams()
        if command in {"next exam", "what is my next exam"}:
            return self.smart.next_exam()
        if command.startswith("days until "):
            return self.smart.days_until_exam(raw_text[11:])
        if command.startswith("add goal "):
            goal_text = raw_text[9:]
            if " by " in goal_text:
                goal, deadline = goal_text.split(" by ", 1)
                return self.smart.add_goal(goal, deadline)
            return self.smart.add_goal(goal_text)
        if command in {"show goals", "goals", "my goals"}:
            return self.smart.list_goals()
        if command.startswith("complete goal "):
            return self.smart.complete_goal(raw_text[14:])
        if command in {"smart context", "what do you know"}:
            return self.smart.smart_context()

        if command in {"care mode", "digital mama", "coach me"}:
            return self.care.care_mode()
        if command in {"plan my day", "organize my day"}:
            return self.care.plan_day()
        if command in {"home reset", "cleaning plan"}:
            return self.care.home_reset()
        if command in {"study push", "push me to study"}:
            return self.care.study_push()

        if command in {"weather", "today weather", "what is the weather"}:
            return self.weather.summary()
        if command.startswith("weather "):
            return self.weather.summary(raw_text[8:])

        if command in {"analyze screen", "screen analysis", "what is on my screen", "analyze my screen", "what am i looking at"}:
            return self.vision.analyze_screen()
        if command in {"explain screen", "explain this screen"}:
            return self.vision.explain_screen()
        if command in {"summarize screen", "summarize this page", "summarize page"}:
            return self.vision.summarize_screen()
        if command in {"create flashcards from screen", "flashcards from screen", "screen flashcards"}:
            return self.vision.flashcards_from_screen()
        if command in {"create quiz from screen", "quiz from screen", "screen quiz"}:
            return self.vision.quiz_from_screen()
        if command in {"screenshot", "screen text", "read screen"}:
            return self.vision.raw_screen_text()

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

        if command in {"daily briefing", "briefing"}:
            return self.daily.briefing()
        if command in {"daily lesson"}:
            return self.daily.daily_lesson()
        if command in {"daily tip", "tip"}:
            return self.daily.practical_tip()
        if command in {"study mode"}:
            return self.daily.study_mode()
        if command in {"home mode"}:
            return self.daily.home_mode()
        if command in {"evening reflection"}:
            return self.daily.evening_reflection()

        if command.startswith("add task "):
            return self.daily.add_task(raw_text[9:])
        if command in {"tasks", "show tasks"}:
            tasks = self.daily.list_tasks()
            return "Open tasks: none." if not tasks else "Open tasks:\n" + "\n".join(tasks)
        if command.startswith("done "):
            return self.daily.complete_task(raw_text[5:])

        if command.startswith("remember "):
            return self.memory.remember(raw_text[9:])
        if command in {"recall", "show memory", "memory"}:
            memories = self.memory.recall()
            return "I do not have any memories yet." if not memories else "Here is what I remember:\n" + "\n".join(f"- {item}" for item in memories)
        if command.startswith("forget "):
            return self.memory.forget(raw_text[7:])
        if command in {"who am i", "whoami"}:
            return self.memory.profile_summary()
        if command.startswith("memory "):
            key = raw_text[7:].strip().rstrip("?")
            value = self.memory.get_item(key)
            return f"{key}: {value}" if value else f"I do not know {key} yet."

        if command in {"open google"}:
            return self.desktop.open_url("https://www.google.com")
        if command in {"open youtube"}:
            return self.desktop.open_url("https://www.youtube.com")
        if command.startswith("open app "):
            return self.desktop.open_app(raw_text[9:])
        if command.startswith("google "):
            return self.desktop.search_google(raw_text[7:])
        if command.startswith("youtube "):
            return self.desktop.search_youtube(raw_text[8:])

        return None

    @staticmethod
    def help_text() -> str:
        return (
            "Available commands:\n"
            "- create mission Pass Computer Networks\n"
            "- show mission\n"
            "- mission briefing\n"
            "- add objective Subnetting\n"
            "- complete objective Routing\n"
            "- jarvis status\n"
            "- what should i do now\n"
            "- what should i study\n"
            "- prepare me for Computer Networks exam\n"
            "- daily intelligence\n"
            "- add exam Computer Networks on 2026-06-17 at 09:00\n"
            "- show exams\n"
            "- show goals\n"
            "- weather\n"
            "- analyze screen\n"
            "- add task task name\n"
            "- start focus topic\n"
            "- end focus\n"
            "- help"
        )
