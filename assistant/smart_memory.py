import datetime as dt
import json
import re
from pathlib import Path
from typing import Any


class SmartMemory:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.exams_path = self.data_dir / "exams.json"
        self.goals_path = self.data_dir / "goals.json"
        self._ensure_files()

    def _ensure_files(self):
        if not self.exams_path.exists():
            self.exams_path.write_text("[]", encoding="utf-8")
        if not self.goals_path.exists():
            self.goals_path.write_text("[]", encoding="utf-8")

    def _read(self, path: Path) -> list[dict[str, Any]]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def _write(self, path: Path, data: list[dict[str, Any]]):
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def add_exam(self, subject: str, date_text: str, time_text: str = "") -> str:
        subject = subject.strip()
        if not subject:
            return "Tell me the exam subject. Example: add exam Computer Networks on 2026-06-17 at 09:00"

        exam_date = self._parse_date(date_text)
        if not exam_date:
            return "I could not understand the exam date. Use format: 2026-06-17"

        exams = self._read(self.exams_path)
        exams.append({
            "subject": subject,
            "date": exam_date.isoformat(),
            "time": time_text.strip(),
            "created_at": dt.datetime.now().isoformat(timespec="seconds"),
        })
        exams.sort(key=lambda item: item.get("date", "9999-12-31"))
        self._write(self.exams_path, exams)
        time_part = f" at {time_text.strip()}" if time_text.strip() else ""
        return f"Saved exam: {subject} on {exam_date.strftime('%d/%m/%Y')}{time_part}."

    def list_exams(self) -> str:
        exams = self._read(self.exams_path)
        if not exams:
            return "No exams saved yet."
        today = dt.date.today()
        lines = ["Saved exams:"]
        for exam in exams:
            date_obj = dt.date.fromisoformat(exam["date"])
            days = (date_obj - today).days
            suffix = "today" if days == 0 else f"in {days} days" if days > 0 else f"{abs(days)} days ago"
            time_part = f" at {exam.get('time')}" if exam.get("time") else ""
            lines.append(f"- {exam['subject']}: {date_obj.strftime('%d/%m/%Y')}{time_part} ({suffix})")
        return "\n".join(lines)

    def next_exam(self) -> str:
        exams = self._read(self.exams_path)
        today = dt.date.today()
        upcoming = []
        for exam in exams:
            date_obj = dt.date.fromisoformat(exam["date"])
            if date_obj >= today:
                upcoming.append((date_obj, exam))
        if not upcoming:
            return "No upcoming exams saved."
        date_obj, exam = sorted(upcoming, key=lambda item: item[0])[0]
        days = (date_obj - today).days
        day_text = "today" if days == 0 else f"in {days} days"
        time_part = f" at {exam.get('time')}" if exam.get("time") else ""
        return f"Next exam: {exam['subject']} on {date_obj.strftime('%d/%m/%Y')}{time_part}, {day_text}."

    def days_until_exam(self, subject_query: str) -> str:
        subject_query = subject_query.lower().strip()
        exams = self._read(self.exams_path)
        today = dt.date.today()
        for exam in exams:
            if subject_query in exam.get("subject", "").lower():
                date_obj = dt.date.fromisoformat(exam["date"])
                days = (date_obj - today).days
                if days == 0:
                    return f"{exam['subject']} is today."
                if days > 0:
                    return f"{exam['subject']} is in {days} days."
                return f"{exam['subject']} was {abs(days)} days ago."
        return "I could not find that exam."

    def add_goal(self, goal: str, deadline_text: str = "") -> str:
        goal = goal.strip()
        if not goal:
            return "Tell me the goal. Example: add goal finish Neural Networks by 2026-06-30"

        deadline = self._parse_date(deadline_text) if deadline_text.strip() else None
        goals = self._read(self.goals_path)
        goals.append({
            "goal": goal,
            "deadline": deadline.isoformat() if deadline else "",
            "done": False,
            "created_at": dt.datetime.now().isoformat(timespec="seconds"),
        })
        self._write(self.goals_path, goals)
        deadline_part = f" by {deadline.strftime('%d/%m/%Y')}" if deadline else ""
        return f"Saved goal: {goal}{deadline_part}."

    def list_goals(self) -> str:
        goals = self._read(self.goals_path)
        if not goals:
            return "No goals saved yet."
        today = dt.date.today()
        lines = ["Saved goals:"]
        for index, goal in enumerate(goals, start=1):
            status = "done" if goal.get("done") else "active"
            deadline = goal.get("deadline") or ""
            extra = ""
            if deadline:
                date_obj = dt.date.fromisoformat(deadline)
                days = (date_obj - today).days
                extra = f" - deadline {date_obj.strftime('%d/%m/%Y')} ({days} days left)"
            lines.append(f"{index}. {goal['goal']} [{status}]{extra}")
        return "\n".join(lines)

    def complete_goal(self, query: str) -> str:
        query = query.lower().strip()
        goals = self._read(self.goals_path)
        for goal in goals:
            if query in goal.get("goal", "").lower():
                goal["done"] = True
                goal["completed_at"] = dt.datetime.now().isoformat(timespec="seconds")
                self._write(self.goals_path, goals)
                return f"Completed goal: {goal['goal']}. Good work."
        return "I could not find that goal."

    def smart_context(self) -> str:
        parts = []
        next_exam = self.next_exam()
        if "No upcoming" not in next_exam:
            parts.append(next_exam)
        goals = self._read(self.goals_path)
        active_goals = [goal for goal in goals if not goal.get("done")]
        if active_goals:
            parts.append(f"Active goals: {len(active_goals)}")
            parts.append(f"Suggested goal focus: {active_goals[0]['goal']}")
        if not parts:
            return "No exams or goals saved yet."
        return "\n".join(parts)

    def _parse_date(self, text: str) -> dt.date | None:
        text = text.strip()
        if not text:
            return None
        patterns = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%d/%m",
            "%d-%m",
        ]
        for pattern in patterns:
            try:
                parsed = dt.datetime.strptime(text, pattern).date()
                if pattern in {"%d/%m", "%d-%m"}:
                    year = dt.date.today().year
                    parsed = parsed.replace(year=year)
                    if parsed < dt.date.today():
                        parsed = parsed.replace(year=year + 1)
                return parsed
            except ValueError:
                continue
        return None

    def parse_exam_sentence(self, text: str) -> str | None:
        clean = text.strip()
        lower = clean.lower()
        if not ("exam" in lower or "εξέταση" in lower or "εξεταση" in lower):
            return None

        match = re.search(r"(?:my\s+)?(.+?)\s+exam\s+(?:is\s+)?(?:on\s+)?(.+)", clean, re.IGNORECASE)
        if match:
            return self.add_exam(match.group(1).strip(), match.group(2).strip())

        match = re.search(r"εξ[εέ]ταση\s+(.+?)\s+(?:στις\s+)?(.+)", clean, re.IGNORECASE)
        if match:
            return self.add_exam(match.group(1).strip(), match.group(2).strip())
        return None

    def parse_goal_sentence(self, text: str) -> str | None:
        clean = text.strip()
        lower = clean.lower()
        if "goal" not in lower and "στόχος" not in lower and "στοχος" not in lower:
            return None

        match = re.search(r"(?:my\s+)?goal\s+(?:is\s+)?(.+?)(?:\s+by\s+(.+))?$", clean, re.IGNORECASE)
        if match:
            return self.add_goal(match.group(1).strip(), (match.group(2) or "").strip())

        match = re.search(r"στ[όο]χος\s+(?:μου\s+)?(?:είναι\s+|ειναι\s+)?(.+?)(?:\s+μέχρι\s+(.+)|\s+μεχρι\s+(.+))?$", clean, re.IGNORECASE)
        if match:
            deadline = match.group(2) or match.group(3) or ""
            return self.add_goal(match.group(1).strip(), deadline.strip())
        return None
