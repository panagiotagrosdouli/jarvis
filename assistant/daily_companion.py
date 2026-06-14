import datetime as dt
import sqlite3
from pathlib import Path


class DailyCompanion:
    def __init__(self, db_path: str = "jarvis_memory.db"):
        self.db_path = Path(db_path)
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
            return "Tell me what task to add."

        with self._connect() as connection:
            connection.execute(
                "INSERT INTO tasks (content, category) VALUES (?, ?)",
                (clean, category),
            )
        return f"Task added: {clean}"

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
            return "I could not find that task."
        return "Task completed. Good job."

    def daily_lesson(self) -> str:
        return "Daily lesson: Small consistent progress is more powerful than waiting for perfect motivation."

    def practical_tip(self) -> str:
        return "Tip: Pick the three most important tasks for today and start with the easiest one."

    def encouragement(self) -> str:
        return "Good morning. Start calmly, choose one small win, and build your day from there."

    def briefing(self) -> str:
        now = dt.datetime.now()
        tasks = self.list_tasks()
        if tasks:
            task_text = "Today you have:\n" + "\n".join(f"- {task}" for task in tasks[:8])
        else:
            task_text = "You do not have open tasks yet."

        return (
            f"{self.encouragement()}\n\n"
            f"Time: {now.strftime('%H:%M')}\n"
            f"Date: {now.strftime('%d/%m/%Y')}\n\n"
            f"{task_text}\n\n"
            f"{self.practical_tip()}\n\n"
            f"{self.daily_lesson()}"
        )
