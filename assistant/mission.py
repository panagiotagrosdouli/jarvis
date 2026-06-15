import json
from pathlib import Path
from typing import Any


DEFAULT_OBJECTIVES = ["Routing", "TCP/IP", "DNS", "Subnetting", "Security"]


class MissionManager:
    def __init__(self, path: str = "data/missions.json"):
        self.path = Path(path)
        self.path.parent.mkdir(exist_ok=True)
        if not self.path.exists():
            self._write({"active_mission": None})

    def _read(self) -> dict[str, Any]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {"active_mission": None}
        except Exception:
            return {"active_mission": None}

    def _write(self, data: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def create_mission(self, name: str, objectives: list[str] | None = None) -> str:
        name = name.strip()
        if not name:
            return "Tell me the mission name. Example: create mission Pass Computer Networks"

        objective_names = objectives or DEFAULT_OBJECTIVES
        mission = {
            "name": name,
            "objectives": [{"name": item, "done": False} for item in objective_names],
        }
        self._write({"active_mission": mission})
        return self.mission_status(prefix="Mission created.")

    def show_mission(self) -> str:
        return self.mission_status()

    def mission_status(self, prefix: str = "") -> str:
        mission = self._active_mission()
        if not mission:
            return "No active mission. Create one with: create mission Pass Computer Networks"

        objectives = mission.get("objectives", [])
        total = len(objectives)
        done = len([item for item in objectives if item.get("done")])
        progress = int((done / total) * 100) if total else 0

        lines = []
        if prefix:
            lines.append(prefix)
            lines.append("")
        lines.extend([
            "MISSION STATUS",
            f"Mission: {mission.get('name', 'Unnamed mission')}",
            f"Progress: {progress}%",
            "",
            "Objectives:",
        ])
        for objective in objectives:
            marker = "✓" if objective.get("done") else "□"
            lines.append(f"{marker} {objective.get('name')}")

        next_objective = self.next_objective()
        if next_objective:
            lines.extend(["", f"Next objective: {next_objective}"])
        return "\n".join(lines)

    def complete_objective(self, objective_query: str) -> str:
        objective_query = objective_query.lower().strip()
        data = self._read()
        mission = data.get("active_mission")
        if not mission:
            return "No active mission."

        for objective in mission.get("objectives", []):
            if objective_query in objective.get("name", "").lower():
                objective["done"] = True
                self._write(data)
                return self.mission_status(prefix=f"Objective completed: {objective.get('name')}.")
        return "I could not find that objective."

    def add_objective(self, objective_name: str) -> str:
        objective_name = objective_name.strip()
        if not objective_name:
            return "Tell me the objective name."
        data = self._read()
        mission = data.get("active_mission")
        if not mission:
            return "No active mission. Create a mission first."
        mission.setdefault("objectives", []).append({"name": objective_name, "done": False})
        self._write(data)
        return self.mission_status(prefix=f"Objective added: {objective_name}.")

    def next_objective(self) -> str:
        mission = self._active_mission()
        if not mission:
            return ""
        for objective in mission.get("objectives", []):
            if not objective.get("done"):
                return objective.get("name", "")
        return "All objectives completed"

    def mission_briefing(self) -> str:
        mission = self._active_mission()
        if not mission:
            return "No active mission. Create one with: create mission Pass Computer Networks"
        status = self.mission_status()
        next_objective = self.next_objective()
        return (
            f"MISSION BRIEFING\n\n"
            f"{status}\n\n"
            "Recommended action:\n"
            f"Start a 25-minute focus session on {next_objective}."
        )

    def _active_mission(self) -> dict[str, Any] | None:
        mission = self._read().get("active_mission")
        return mission if isinstance(mission, dict) else None
