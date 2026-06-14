import datetime as dt
import random
import sqlite3
from pathlib import Path

from assistant.weather import WeatherService


class DailyCompanion:
    def __init__(self, db_path: str = "jarvis_memory.db"):
        self.db_path = Path(db_path)
        self.weather = WeatherService()
        self._create_tables()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _create_tables(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    is_done INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def add_task(self, content: str, category: str = "general") -> str:
        clean = content.strip()
        if not clean:
            return "Tell me what task you want to add."

        with self._connect() as connection:
            connection.execute(
                "INSERT INTO tasks (content, category) VALUES (?, ?)",
                (clean, category),
            )
        return f"Added to your task list: {clean}"

    def list_tasks(self) -> list[str]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, content, category FROM tasks WHERE is_done = 0 ORDER BY created_at ASC"
            ).fetchall()
        return [f"{task_id}. [{category}] {content}" for task_id, content, category in rows]

    def complete_task(self, task_id_text: str) -> str:
        try:
            task_id = int(task_id_text.strip())
        except ValueError:
            return "Give me a task number. Example: done 2"

        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE tasks SET is_done = 1 WHERE id = ?",
                (task_id,),
            )
        if cursor.rowcount == 0:
            return "I could not find a task with that number."
        return "Marked as completed. Good progress."

    def encouragement(self) -> str:
        messages = [
            "Welcome back, Panagiota. Let us make today useful and calm.",
            "Good morning, Panagiota. Start with one clear step and build from there.",
            "Welcome back. Today does not need to be perfect. It needs direction.",
            "Good morning. Choose one small win and begin there.",
            "Welcome back. Focus, clarity, and consistency are enough for today.",
            "Good morning. Your future self will thank you for one focused hour today.",
        ]
        return random.choice(messages)

    def practical_tip(self) -> str:
        tips = [
            "Tip: Start with the smallest task. Momentum matters.",
            "Tip: If you have laundry, start it before studying so it runs while you work.",
            "Tip: Set a 25-minute timer and focus on one thing only.",
            "Tip: Before going out, check phone, keys, wallet, and water.",
            "Tip: If the room feels messy, do a 10-minute reset. Do not try to clean everything at once.",
            "Tip: Write the three most important tasks of the day and treat everything else as optional.",
        ]
        return random.choice(tips)

    def daily_lesson(self) -> str:
        lessons = [
            "Daily lesson: Spaced repetition improves long-term memory more than rereading.",
            "Daily lesson: Neural networks learn by reducing prediction error over many examples.",
            "Daily lesson: Active recall is usually stronger than passive reading.",
            "Daily lesson: The Pomodoro method helps reduce cognitive overload.",
            "Daily lesson: Learning improves when you combine theory, examples, and practice.",
            "Daily lesson: Consistency is more reliable than motivation because motivation changes.",
        ]
        return random.choice(lessons)

    def evening_reflection(self) -> str:
        return (
            "Evening reflection:\n"
            "1. What did you complete today?\n"
            "2. What made the day difficult?\n"
            "3. What is the most important step for tomorrow?\n"
            "Progress matters more than perfection."
        )

    def study_mode(self) -> str:
        return (
            "Study mentor mode:\n"
            "Choose a topic and I will break it into theory, examples, key terms, and exam-style questions."
        )

    def home_mode(self) -> str:
        return (
            "Home organizer mode:\n"
            "Start with one area only: laundry, trash, desk, or dishes. Work for 10 minutes."
        )

    def briefing(self) -> str:
        now = dt.datetime.now()
        tasks = self.list_tasks()
        weather_text = self.weather.summary()

        if tasks:
            task_text = "Open tasks:\n" + "\n".join(f"- {task}" for task in tasks[:8])
            focus = f"Suggested focus: Start with {tasks[0]}."
        else:
            task_text = "Open tasks: none. Add one important task when you are ready."
            focus = "Suggested focus: Choose one useful action for the next 25 minutes."

        return (
            f"{self.encouragement()}\n\n"
            f"Time: {now.strftime('%H:%M')}\n"
            f"Date: {now.strftime('%d/%m/%Y')}\n\n"
            f"{weather_text}\n\n"
            f"{task_text}\n\n"
            f"{focus}\n\n"
            f"{self.practical_tip()}\n\n"
            f"{self.daily_lesson()}"
        )
