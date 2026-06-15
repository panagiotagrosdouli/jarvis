from assistant.auto_study_tracker import AutoStudyTracker
from assistant.smart_memory import SmartMemory
from assistant.window_monitor import WindowMonitor


class StudyDetector:
    STUDY_KEYWORDS = [
        "pdf",
        "moodle",
        "eclass",
        "lecture",
        "notes",
        "slides",
        "university",
        "course",
        "assignment",
        "exam",
        "vscode",
        "visual studio code",
        "powerpoint",
        "onenote",
    ]

    DISTRACTION_KEYWORDS = [
        "youtube",
        "tiktok",
        "instagram",
        "facebook",
        "netflix",
        "reddit",
    ]

    def __init__(self):
        self.window = WindowMonitor()
        self.tracker = AutoStudyTracker()
        self.smart = SmartMemory()

    def detect_once(self) -> str:
        title = self.window.active_window_title()
        if not title:
            return "I could not read the active window title."

        subject = self._subject_from_title(title)
        if subject:
            status = self.tracker.status()
            if "idle" in status.lower():
                started = self.tracker.start(subject, source="window_detected")
                return f"Study detected from window: {title}\n{started}"
            return f"Study window detected: {title}\n{status}"

        if self._looks_distracting(title):
            return f"Possible distraction detected: {title}"

        return f"No study activity detected. Active window: {title}"

    def current_window(self) -> str:
        title = self.window.active_window_title()
        return f"Active window: {title or 'unknown'}"

    def _subject_from_title(self, title: str) -> str:
        lower = title.lower()

        exams_text = self.smart.list_exams()
        for line in exams_text.splitlines():
            if ":" in line:
                subject = line.split(":", 1)[0].replace("-", "").strip()
                if subject and subject.lower() in lower:
                    return subject

        known_subjects = {
            "network": "Computer Networks",
            "networks": "Computer Networks",
            "δίκτυα": "Δίκτυα Υπολογιστών",
            "diktya": "Δίκτυα Υπολογιστών",
            "subnet": "Computer Networks",
            "routing": "Computer Networks",
            "tcp": "Computer Networks",
            "dns": "Computer Networks",
            "ai": "Artificial Intelligence",
            "artificial intelligence": "Artificial Intelligence",
            "machine learning": "Machine Learning",
            "database": "Databases",
            "databases": "Databases",
        }
        for keyword, subject in known_subjects.items():
            if keyword in lower:
                return subject

        if any(keyword in lower for keyword in self.STUDY_KEYWORDS):
            return "general study"
        return ""

    def _looks_distracting(self, title: str) -> bool:
        lower = title.lower()
        return any(keyword in lower for keyword in self.DISTRACTION_KEYWORDS)
