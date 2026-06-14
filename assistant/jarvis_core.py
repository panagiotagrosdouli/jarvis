import datetime as dt

from assistant.daily_companion import DailyCompanion
from assistant.focus import FocusManager
from assistant.smart_memory import SmartMemory
from assistant.weather import WeatherService


class JarvisCore:
    def __init__(self):
        self.daily = DailyCompanion()
        self.focus = FocusManager()
        self.smart = SmartMemory()
        self.weather = WeatherService()

    def status(self) -> str:
        tasks = self.daily.list_tasks()
        focus = self.focus.stats()
        context = self.smart.smart_context()

        lines = [
            "JARVIS STATUS",
            "Systems operational.",
            "",
            context,
            "",
            f"Open tasks: {len(tasks)}",
            focus,
            "",
            f"Recommendation: {self.recommend_next_action(short=True)}",
        ]
        return "\n".join(lines)

    def recommend_next_action(self, short: bool = False) -> str:
        tasks = self.daily.list_tasks()
        focus_status = self.focus.status()
        next_exam = self.smart.next_exam()
        goals_text = self.smart.list_goals()

        if "No focus session" not in focus_status:
            return "Stay with your current focus session. Do not switch tasks right now."

        exam_priority = "No upcoming exams" not in next_exam
        has_goals = "No goals" not in goals_text
        has_tasks = bool(tasks)

        if exam_priority:
            subject = self._subject_from_next_exam(next_exam)
            if short:
                return f"Study {subject} for 25 minutes."
            return (
                f"Your priority is: {subject}.\n"
                f"{next_exam}\n\n"
                "Do this now:\n"
                f"1. Start a 25-minute focus session for {subject}.\n"
                "2. Review theory first.\n"
                "3. Then do active recall: close the notes and explain the topic out loud.\n"
                "4. After the session, ask me for a quiz."
            )

        if has_tasks:
            if short:
                return f"Start with {tasks[0]}."
            return (
                "Your best next action is your first open task.\n"
                f"Task: {tasks[0]}\n\n"
                "Do it for 25 minutes only. The goal is progress, not perfection."
            )

        if has_goals:
            if short:
                return "Work on your first active goal for 25 minutes."
            return (
                "You have active goals but no urgent task selected.\n"
                f"{goals_text}\n\n"
                "Choose the first active goal and do one small action for 25 minutes."
            )

        if short:
            return "Add one useful task and start a 25-minute focus session."
        return (
            "You do not have an urgent item saved yet.\n"
            "Do this now:\n"
            "1. Drink water.\n"
            "2. Add one task.\n"
            "3. Start a 25-minute focus session."
        )

    def what_should_i_study(self) -> str:
        next_exam = self.smart.next_exam()
        if "No upcoming exams" in next_exam:
            return (
                "I do not see an upcoming exam saved.\n"
                "Add one with: add exam Computer Networks on 2026-06-17 at 09:00"
            )
        subject = self._subject_from_next_exam(next_exam)
        return (
            f"Study priority: {subject}.\n"
            f"{next_exam}\n\n"
            "Suggested study order:\n"
            "1. Core theory and definitions.\n"
            "2. Important diagrams or models.\n"
            "3. Exercises or examples.\n"
            "4. Active recall without notes.\n"
            "5. Short quiz before stopping."
        )

    def prepare_for_exam(self, subject_query: str = "") -> str:
        subject_query = subject_query.strip()
        if subject_query:
            countdown = self.smart.days_until_exam(subject_query)
            subject = subject_query
        else:
            countdown = self.smart.next_exam()
            subject = self._subject_from_next_exam(countdown)

        if "could not find" in countdown.lower() or "no upcoming" in countdown.lower():
            return countdown

        focus_response = self.focus.start(subject)
        return (
            f"Exam preparation mode: {subject}\n"
            f"{countdown}\n\n"
            "Plan for this session:\n"
            "1. 10 minutes: scan the theory.\n"
            "2. 15 minutes: study the weakest topic.\n"
            "3. 10 minutes: active recall.\n"
            "4. 10 minutes: solve or explain one example.\n"
            "5. Ask me: create quiz from screen, if your notes are open.\n\n"
            f"{focus_response}"
        )

    def daily_intelligence(self) -> str:
        now = dt.datetime.now()
        weather = self.weather.summary()
        context = self.smart.smart_context()
        recommendation = self.recommend_next_action(short=True)
        tasks = self.daily.list_tasks()

        return (
            f"JARVIS daily intelligence for {now.strftime('%d/%m/%Y')} at {now.strftime('%H:%M')}.\n\n"
            f"{weather}\n\n"
            f"{context}\n\n"
            f"Open tasks: {len(tasks)}\n"
            f"Recommended first action: {recommendation}"
        )

    def _subject_from_next_exam(self, text: str) -> str:
        if ":" in text:
            return text.split(":", 1)[1].split(" on ", 1)[0].strip()
        if " is in " in text:
            return text.split(" is in ", 1)[0].strip()
        return "your next exam"
