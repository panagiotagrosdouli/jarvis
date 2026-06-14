import sqlite3
from pathlib import Path


class Memory:
    def __init__(self, db_path: str = "jarvis_memory.db"):
        self.db_path = Path(db_path)
        self._create_table()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _create_table(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def remember(self, content: str) -> str:
        clean_content = content.strip()
        if not clean_content:
            return "I need something meaningful to remember."

        with self._connect() as connection:
            connection.execute(
                "INSERT INTO memories (content) VALUES (?)",
                (clean_content,),
            )
        return "I saved that to memory."

    def recall(self, limit: int = 10) -> list[str]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT content FROM memories ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [row[0] for row in rows]
