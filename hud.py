import datetime as dt
import sys

from PyQt6.QtCore import Qt, QTimer, QPoint, QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QFrame
from dotenv import load_dotenv

load_dotenv()

from assistant.brain import Brain
from assistant.commands import CommandHandler
from assistant.daily_companion import DailyCompanion
from assistant.focus import FocusManager
from assistant.memory import Memory
from assistant.settings import SettingsManager
from assistant.speech import listen, speak_async
from assistant.weather import WeatherService


class HUDResponseWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, text: str, brain: Brain, commands: CommandHandler):
        super().__init__()
        self.text = text
        self.brain = brain
        self.commands = commands

    def run(self):
        response = self.commands.handle(self.text)
        if response is None:
            response = self.brain.answer(self.text)
        self.finished.emit(response)


class HUDVoiceWorker(QThread):
    wake = pyqtSignal()
    command = pyqtSignal(str)
    status = pyqtSignal(str)

    def __init__(self, wake_words: list[str]):
        super().__init__()
        self.running = True
        self.awaiting_command = False
        self.wake_words = wake_words
        self.stop_words = ["stop listening", "stop", "σταμάτα", "σταματα"]

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            self.status.emit("Listening for Jarvis")
            text = listen().strip()
            if not text:
                continue

            lower = text.lower()
            if any(word in lower for word in self.stop_words):
                self.awaiting_command = False
                self.status.emit("Paused")
                continue

            if self.awaiting_command:
                self.awaiting_command = False
                self.command.emit(text)
                continue

            if any(word in lower for word in self.wake_words):
                self.awaiting_command = True
                self.status.emit("Awake")
                self.wake.emit()


class JarvisHUD(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = SettingsManager()
        self.weather = WeatherService()
        self.daily = DailyCompanion()
        self.focus = FocusManager()
        self.memory = Memory()
        self.brain = Brain()
        self.commands = CommandHandler(self.memory)
        self.voice_worker = None
        self.response_worker = None
        self.drag_position = QPoint()

        self.setWindowTitle("Jarvis HUD")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(self.settings.transparency())
        self.resize(340, 330)

        self.panel = QFrame()
        self.panel.setObjectName("panel")

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        self.title = QLabel("JARVIS")
        self.title.setObjectName("title")

        self.time_label = QLabel("--:--")
        self.time_label.setObjectName("time")

        self.weather_label = QLabel("Weather: loading")
        self.tasks_label = QLabel("Tasks: loading")
        self.focus_label = QLabel("Focus: none")
        self.status_label = QLabel("Status: starting")
        self.last_command_label = QLabel("Command: none")
        self.last_answer_label = QLabel("Answer: ready")

        for label in [
            self.weather_label,
            self.tasks_label,
            self.focus_label,
            self.status_label,
            self.last_command_label,
            self.last_answer_label,
        ]:
            label.setObjectName("line")
            label.setWordWrap(True)

        layout.addWidget(self.title)
        layout.addWidget(self.time_label)
        layout.addWidget(self.weather_label)
        layout.addWidget(self.tasks_label)
        layout.addWidget(self.focus_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.last_command_label)
        layout.addWidget(self.last_answer_label)
        self.panel.setLayout(layout)

        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self.panel)
        self.setLayout(root)
        self.setStyleSheet(self.stylesheet())

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(60000)
        self.refresh()
        self.move_to_top_right()

        QTimer.singleShot(900, self.start_voice_mode)
        QTimer.singleShot(1200, self.speak_startup)

    def start_voice_mode(self):
        if self.voice_worker and self.voice_worker.isRunning():
            return
        self.voice_worker = HUDVoiceWorker(self.settings.wake_words())
        self.voice_worker.wake.connect(self.on_wake)
        self.voice_worker.command.connect(self.on_voice_command)
        self.voice_worker.status.connect(self.set_status)
        self.voice_worker.start()

    def speak_startup(self):
        message = "Jarvis HUD is online. Say Jarvis when you need me."
        self.set_status("Online")
        speak_async(message)

    def on_wake(self):
        message = "I am listening."
        self.set_status("Awake")
        self.last_answer_label.setText("Answer: I am listening")
        speak_async(message)

    def on_voice_command(self, text: str):
        self.last_command_label.setText(f"Command: {text}")
        self.set_status("Thinking")

        if self.response_worker and self.response_worker.isRunning():
            return

        self.response_worker = HUDResponseWorker(text, self.brain, self.commands)
        self.response_worker.finished.connect(self.on_response)
        self.response_worker.start()

    def on_response(self, response: str):
        short_response = response.replace("\n", " ")[:180]
        self.last_answer_label.setText(f"Answer: {short_response}")
        self.set_status("Speaking")
        speak_async(response)
        QTimer.singleShot(2500, lambda: self.set_status("Listening for Jarvis"))
        self.refresh()

    def set_status(self, text: str):
        self.status_label.setText(f"Status: {text}")

    def move_to_top_right(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.right() - self.width() - 24, screen.top() + 24)

    def refresh(self):
        now = dt.datetime.now()
        self.time_label.setText(now.strftime("%H:%M"))

        try:
            weather = self.weather.summary()
            weather_short = weather.split(". ")[0]
            self.weather_label.setText(f"Weather: {weather_short}")
        except Exception:
            self.weather_label.setText("Weather: unavailable")

        try:
            tasks = self.daily.list_tasks()
            self.tasks_label.setText(f"Tasks: {len(tasks)} pending")
        except Exception:
            self.tasks_label.setText("Tasks: unavailable")

        try:
            focus_status = self.focus.status()
            self.focus_label.setText(f"Focus: {focus_status}")
        except Exception:
            self.focus_label.setText("Focus: none")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if self.width() > 120:
            self.resize(120, 90)
            self.weather_label.hide()
            self.tasks_label.hide()
            self.focus_label.hide()
            self.status_label.hide()
            self.last_command_label.hide()
            self.last_answer_label.hide()
        else:
            self.resize(340, 330)
            self.weather_label.show()
            self.tasks_label.show()
            self.focus_label.show()
            self.status_label.show()
            self.last_command_label.show()
            self.last_answer_label.show()
        event.accept()

    def closeEvent(self, event):
        if self.voice_worker:
            self.voice_worker.stop()
        event.accept()

    @staticmethod
    def stylesheet():
        return """
        QFrame#panel {
            background-color: rgba(2, 6, 23, 225);
            border: 1px solid #38bdf8;
            border-radius: 22px;
        }
        QLabel#title {
            color: #38bdf8;
            font-family: Segoe UI, Arial;
            font-size: 30px;
            font-weight: 900;
            letter-spacing: 4px;
        }
        QLabel#time {
            color: #f8fafc;
            font-family: Segoe UI, Arial;
            font-size: 28px;
            font-weight: 800;
        }
        QLabel#line {
            color: #cbd5e1;
            font-family: Segoe UI, Arial;
            font-size: 13px;
            font-weight: 600;
        }
        """


if __name__ == "__main__":
    app = QApplication(sys.argv)
    hud = JarvisHUD()
    hud.show()
    sys.exit(app.exec())
