import datetime as dt
import json
from pathlib import Path

from assistant.daily_companion import DailyCompanion
from assistant.smart_memory import SmartMemory
from assistant.weather import WeatherService


class StartupBriefing:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.state_path = self.data_dir / "startup_state.json"
        self.daily = DailyCompanion()
        self.smart = SmartMemory()
        self.weather = WeatherService()

    def should_speak_today(self) -> bool:
        today = dt.date.today().isoformat()
        try:
            if self.state_path.exists():
                state = json.loads(self.state_path.read_text(encoding="utf-8"))
                return state.get("last_startup_briefing_date") != today
        except Exception:
            return True
        return True

    def mark_spoken_today(self) -> None:
        today = dt.date.today().isoformat()
        state = {}
        try:
            if self.state_path.exists():
                state = json.loads(self.state_path.read_text(encoding="utf-8"))
        except Exception:
            state = {}
        state["last_startup_briefing_date"] = today
        self.state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    def build(self) -> str:
        now = dt.datetime.now()
        hour = now.hour
        if 5 <= hour < 12:
            greeting = "Good morning Panagiota."
        elif 12 <= hour < 18:
            greeting = "Good afternoon Panagiota."
        else:
            greeting = "Good evening Panagiota."

        parts = [
            "JARVIS online.",
            "Systems operational.",
            greeting,
            f"Current time is {now.strftime('%H:%M')}.",
        ]

        try:
            weather = self.weather.summary()
            parts.append(weather)
        except Exception:
            pass

        try:
            context = self.smart.smart_context()
            if context and "No exams or goals" not in context:
                parts.append(context)
        except Exception:
            pass

        try:
            tasks = self.daily.list_tasks()
            if tasks:
                parts.append(f"You have {len(tasks)} open tasks.")
                parts.append(f"First useful task: {tasks[0]}.")
            else:
                parts.append("You have no open tasks yet.")
        except Exception:
            pass

        parts.append("Recommended first action: choose one 25 minute focus session.")
        parts.append("Say Jarvis when you need me.")
        return "\n".join(parts)

    def short_welcome(self) -> str:
        return "JARVIS online. Welcome back Panagiota. Say Jarvis when you need me."

    def startup_message(self) -> str:
        if self.should_speak_today():
            message = self.build()
            self.mark_spoken_today()
            return message
        return self.short_welcome()
