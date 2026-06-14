import datetime as dt
import sys

from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QFrame
from dotenv import load_dotenv

load_dotenv()

from assistant.daily_companion import DailyCompanion
from assistant.focus import FocusManager
from assistant.weather import WeatherService


class JarvisHUD(QWidget):
    def __init__(self):
        super().__init__()
        self.weather = WeatherService()
        self.daily = DailyCompanion()
        self.focus = FocusManager()
        self.drag_position = QPoint()

        self.setWindowTitle("Jarvis HUD")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(0.92)
        self.resize(320, 300)

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
        self.status_label = QLabel("Status: listening")

        for label in [self.weather_label, self.tasks_label, self.focus_label, self.status_label]:
            label.setObjectName("line")
            label.setWordWrap(True)

        layout.addWidget(self.title)
        layout.addWidget(self.time_label)
        layout.addWidget(self.weather_label)
        layout.addWidget(self.tasks_label)
        layout.addWidget(self.focus_label)
        layout.addWidget(self.status_label)
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

        self.status_label.setText("Status: listening for Jarvis")

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
        else:
            self.resize(320, 300)
            self.weather_label.show()
            self.tasks_label.show()
            self.focus_label.show()
            self.status_label.show()
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
