import json
from pathlib import Path
from typing import Any


DEFAULT_SETTINGS = {
    "language": "en",
    "voice_en": "en-US-AriaNeural",
    "voice_el": "el-GR-AthinaNeural",
    "wake_words": ["jarvis", "hey jarvis", "τζάρβις", "τζαρβις", "άνοιξε", "ανοιξε"],
    "theme": "ironman",
    "transparency": 0.92,
    "city": "Thessaloniki",
    "briefing_once_per_day": True,
}


class SettingsManager:
    def __init__(self, path: str = "settings.json"):
        self.path = Path(path)
        self.settings = DEFAULT_SETTINGS.copy()
        self.load()

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            self.save()
            return self.settings

        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                self.settings.update(data)
        except Exception:
            self.settings = DEFAULT_SETTINGS.copy()
            self.save()
        return self.settings

    def save(self) -> None:
        self.path.write_text(json.dumps(self.settings, indent=2, ensure_ascii=False), encoding="utf-8")

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.settings[key] = value
        self.save()

    def language(self) -> str:
        return str(self.get("language", "en"))

    def city(self) -> str:
        return str(self.get("city", "Thessaloniki"))

    def transparency(self) -> float:
        try:
            value = float(self.get("transparency", 0.92))
            return max(0.35, min(1.0, value))
        except Exception:
            return 0.92

    def wake_words(self) -> list[str]:
        words = self.get("wake_words", DEFAULT_SETTINGS["wake_words"])
        if isinstance(words, list):
            return [str(word).lower() for word in words]
        return DEFAULT_SETTINGS["wake_words"]

    def voice_for_language(self, language: str | None = None) -> str:
        lang = (language or self.language()).lower()
        if lang.startswith("el") or lang.startswith("gr"):
            return str(self.get("voice_el", "el-GR-AthinaNeural"))
        return str(self.get("voice_en", "en-US-AriaNeural"))
