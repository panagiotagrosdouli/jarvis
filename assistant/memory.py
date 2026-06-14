import sqlite3
from pathlib import Path


class Memory:
    def __init__(self, db_path: str = "jarvis_memory.db"):
        self.db_path = Path(db_path)
        self._create_tables()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _create_tables(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_items (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    @staticmethod
    def _normalize_key(key: str) -> str:
        return key.strip().lower().replace(" ", "_")

    def remember(self, content: str) -> str:
        clean_content = content.strip()
        if not clean_content:
            return "I need something meaningful to remember."

        if "=" not in clean_content:
            return "Use this format: remember key=value"

        key, value = clean_content.split("=", 1)
        return self.set_item(key=key, value=value)

    def set_item(self, key: str, value: str, category: str = "general") -> str:
        clean_key = self._normalize_key(key)
        clean_value = value.strip()
        clean_category = category.strip() or "general"

        if not clean_key or not clean_value:
            return "Both key and value are required. Example: remember name=Panagiota"

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO memory_items (key, value, category)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    category = excluded.category,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (clean_key, clean_value, clean_category),
            )
        return f"I remembered {clean_key}: {clean_value}"

    def get_item(self, key: str) -> str | None:
        clean_key = self._normalize_key(key)
        with self._connect() as connection:
            row = connection.execute(
                "SELECT value FROM memory_items WHERE key = ?",
                (clean_key,),
            ).fetchone()
        return row[0] if row else None

    def forget(self, key: str) -> str:
        clean_key = self._normalize_key(key)
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM memory_items WHERE key = ?",
                (clean_key,),
            )
        if cursor.rowcount == 0:
            return f"I could not find a memory for {clean_key}."
        return f"I forgot {clean_key}."

    def recall(self, limit: int = 20) -> list[str]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT key, value FROM memory_items
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [f"{key}: {value}" for key, value in rows]

    def profile_summary(self) -> str:
        items = self.recall(limit=50)
        if not items:
            return "I do not know anything about you yet."
        return "Here is what I know about you:\n" + "\n".join(f"- {item}" for item in items)
