import datetime as dt
import json
from pathlib import Path
from typing import Any


class AutoStudyTracker:
    def __init__(self, path: str = "data/auto_study.json"):
        self.path = Path(path)
        self.path.parent.mkdir(exist_ok=True)
        if not self.path.exists():
            self._write({"active": None, "sessions": []})

    def _read(self) -> dict[str, Any]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                data.setdefault("active", None)
                data.setdefault("sessions", [])
                return data
        except Exception:
            pass
        return {"active": None, "sessions": []}

    def _write(self, data: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def start(self, topic: str = "general", source: str = "manual") -> str:
        topic = topic.strip() or "general"
        data = self._read()
        if data.get("active"):
            active = data["active"]
            return f"Auto study is already tracking: {active.get('topic')}. Say: stop auto study"

        data["active"] = {
            "topic": topic,
            "source": source,
            "started_at": dt.datetime.now().replace(microsecond=0).isoformat(),
        }
        self._write(data)
        return f"Auto study tracking started: {topic}. I will count this as study time."

    def stop(self) -> str:
        data = self._read()
        active = data.get("active")
        if not active:
            return "Auto study tracking is not running."

        started_at = dt.datetime.fromisoformat(active["started_at"])
        ended_at = dt.datetime.now().replace(microsecond=0)
        minutes = max(1, int((ended_at - started_at).total_seconds() // 60))
        session = {
            "topic": active.get("topic", "general"),
            "source": active.get("source", "manual"),
            "started_at": active["started_at"],
            "ended_at": ended_at.isoformat(),
            "minutes": minutes,
        }
        data["sessions"].append(session)
        data["active"] = None
        self._write(data)
        return f"Auto study tracking stopped. Topic: {session['topic']}. Duration: {minutes} minutes."

    def status(self) -> str:
        data = self._read()
        active = data.get("active")
        if not active:
            return "Auto study tracking is idle."
        started_at = dt.datetime.fromisoformat(active["started_at"])
        minutes = max(1, int((dt.datetime.now() - started_at).total_seconds() // 60))
        return f"Auto study active: {active.get('topic')}. Time: {minutes} minutes."

    def report(self) -> str:
        data = self._read()
        sessions = data.get("sessions", [])
        today = dt.date.today().isoformat()
        today_sessions = [s for s in sessions if str(s.get("started_at", "")).startswith(today)]

        totals: dict[str, int] = {}
        for session in today_sessions:
            topic = session.get("topic", "general")
            totals[topic] = totals.get(topic, 0) + int(session.get("minutes", 0))

        if not totals:
            return "Auto study report: no completed study sessions today."

        lines = ["Auto study report for today:"]
        total_minutes = 0
        for topic, minutes in sorted(totals.items(), key=lambda item: item[1], reverse=True):
            total_minutes += minutes
            lines.append(f"- {topic}: {minutes} minutes")
        lines.append(f"Total: {total_minutes} minutes")
        return "\n".join(lines)

    def today_minutes(self) -> int:
        data = self._read()
        today = dt.date.today().isoformat()
        return sum(
            int(session.get("minutes", 0))
            for session in data.get("sessions", [])
            if str(session.get("started_at", "")).startswith(today)
        )
