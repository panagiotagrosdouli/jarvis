import datetime as dt
import sqlite3
from pathlib import Path


class FocusManager:
    def __init__(self, db_path: str = "jarvis_memory.db"):
        self.db_path = Path(db_path)
        self._create_tables()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS focus_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    minutes INTEGER DEFAULT 0
                )
                """
            )

    def start(self, topic: str = "general") -> str:
        topic = topic.strip() or "general"
        if self.current():
            return "A focus session is already running. Say: end focus"
        now = dt.datetime.now().replace(microsecond=0).isoformat()
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO focus_sessions (topic, started_at) VALUES (?, ?)",
                (topic, now),
            )
        return f"Focus session started: {topic}. Work on one task only."

    def end(self) -> str:
        session = self.current()
        if not session:
            return "No focus session is running."
        session_id, topic, started_at = session
        start_time = dt.datetime.fromisoformat(started_at)
        now = dt.datetime.now().replace(microsecond=0)
        minutes = max(1, int((now - start_time).total_seconds() // 60))
        with self._connect() as connection:
            connection.execute(
                "UPDATE focus_sessions SET ended_at = ?, minutes = ? WHERE id = ?",
                (now.isoformat(), minutes, session_id),
            )
        return f"Focus session ended. Topic: {topic}. Duration: {minutes} minutes."

    def current(self):
        with self._connect() as connection:
            return connection.execute(
                "SELECT id, topic, started_at FROM focus_sessions WHERE ended_at IS NULL ORDER BY id DESC LIMIT 1"
            ).fetchone()

    def status(self) -> str:
        session = self.current()
        if not session:
            return "No focus session is running."
        _, topic, started_at = session
        start_time = dt.datetime.fromisoformat(started_at)
        minutes = max(1, int((dt.datetime.now() - start_time).total_seconds() // 60))
        return f"Current focus: {topic}. Time: {minutes} minutes."

    def stats(self) -> str:
        today = dt.date.today().isoformat()
        with self._connect() as connection:
            today_minutes = connection.execute(
                "SELECT COALESCE(SUM(minutes), 0) FROM focus_sessions WHERE ended_at IS NOT NULL AND date(started_at) = ?",
                (today,),
            ).fetchone()[0]
            total_minutes = connection.execute(
                "SELECT COALESCE(SUM(minutes), 0) FROM focus_sessions WHERE ended_at IS NOT NULL"
            ).fetchone()[0]
        return f"Focus stats:\nToday: {today_minutes} minutes\nTotal: {total_minutes} minutes"
