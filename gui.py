from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QLabel,
    QFrame,
)
from PyQt6.QtCore import Qt
import sys
from dotenv import load_dotenv

load_dotenv()

from assistant.brain import Brain
from assistant.commands import CommandHandler
from assistant.memory import Memory
from assistant.speech import listen, speak


class JarvisWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.brain = Brain()
        self.memory = Memory()
        self.commands = CommandHandler(self.memory)

        self.setWindowTitle('Jarvis AI Dashboard')
        self.resize(1100, 720)
        self.setStyleSheet(self.stylesheet())

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(16)

        sidebar = self.build_sidebar()
        chat_panel = self.build_chat_panel()
        info_panel = self.build_info_panel()

        main_layout.addWidget(sidebar, 1)
        main_layout.addWidget(chat_panel, 3)
        main_layout.addWidget(info_panel, 1)

        self.setLayout(main_layout)
        self.chat.append('<span class="jarvis">Jarvis:</span> Welcome back, Panagiota. Voice mode is available.')

    def build_sidebar(self):
        panel = QFrame()
        panel.setObjectName('panel')
        layout = QVBoxLayout()
        layout.setSpacing(14)

        title = QLabel('JARVIS')
        title.setObjectName('title')
        subtitle = QLabel('Personal AI Companion')
        subtitle.setObjectName('subtitle')

        status = QLabel('● Online')
        status.setObjectName('status')

        self.voice_button = QPushButton('🎤 Start Listening')
        self.voice_button.clicked.connect(self.listen_and_send)

        self.voice_chat_button = QPushButton('🗣 Voice Conversation')
        self.voice_chat_button.clicked.connect(self.voice_conversation)

        briefing_button = QPushButton('☀ Daily Briefing')
        briefing_button.clicked.connect(lambda: self.process_text('daily briefing'))

        tasks_button = QPushButton('✅ Tasks')
        tasks_button.clicked.connect(lambda: self.process_text('tasks'))

        study_button = QPushButton('🎓 Study Mode')
        study_button.clicked.connect(lambda: self.process_text('study mode'))

        home_button = QPushButton('🏠 Home Mode')
        home_button.clicked.connect(lambda: self.process_text('home mode'))

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(status)
        layout.addSpacing(12)
        layout.addWidget(self.voice_button)
        layout.addWidget(self.voice_chat_button)
        layout.addWidget(briefing_button)
        layout.addWidget(tasks_button)
        layout.addWidget(study_button)
        layout.addWidget(home_button)
        layout.addStretch()

        footer = QLabel('Always ready to help')
        footer.setObjectName('footer')
        layout.addWidget(footer)

        panel.setLayout(layout)
        return panel

    def build_chat_panel(self):
        panel = QFrame()
        panel.setObjectName('chatPanel')
        layout = QVBoxLayout()
        layout.setSpacing(12)

        header = QLabel('AI Conversation')
        header.setObjectName('sectionTitle')

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setObjectName('chat')

        input_row = QHBoxLayout()
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText('Ask Jarvis anything...')
        self.input_box.returnPressed.connect(self.send_message)

        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.send_message)

        input_row.addWidget(self.input_box, 4)
        input_row.addWidget(self.send_button, 1)

        layout.addWidget(header)
        layout.addWidget(self.chat)
        layout.addLayout(input_row)
        panel.setLayout(layout)
        return panel

    def build_info_panel(self):
        panel = QFrame()
        panel.setObjectName('panel')
        layout = QVBoxLayout()
        layout.setSpacing(14)

        layout.addWidget(self.card('Today', 'Daily briefing, tasks, study goals'))
        layout.addWidget(self.card('Voice', 'Edge Neural Voice enabled'))
        layout.addWidget(self.card('Memory', 'Personal facts and reminders'))
        layout.addWidget(self.card('Modes', 'Study • Home • Evening'))
        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def card(self, title: str, body: str):
        frame = QFrame()
        frame.setObjectName('card')
        layout = QVBoxLayout()
        label = QLabel(title)
        label.setObjectName('cardTitle')
        text = QLabel(body)
        text.setObjectName('cardText')
        text.setWordWrap(True)
        layout.addWidget(label)
        layout.addWidget(text)
        frame.setLayout(layout)
        return frame

    def process_text(self, text: str):
        self.chat.append(f'<span class="user">You:</span> {text}')

        response = self.commands.handle(text)

        if response == 'EXIT':
            self.close()
            return

        if response is None:
            response = self.brain.answer(text)

        safe_response = response.replace('\n', '<br>')
        self.chat.append(f'<span class="jarvis">Jarvis:</span> {safe_response}')
        speak(response)

    def send_message(self):
        text = self.input_box.text().strip()
        if not text:
            return

        self.process_text(text)
        self.input_box.clear()

    def listen_and_send(self):
        self.chat.append('<span class="jarvis">Jarvis:</span> Listening...')
        text = listen()

        if not text:
            message = 'I could not hear anything. Check your microphone settings.'
            self.chat.append(f'<span class="jarvis">Jarvis:</span> {message}')
            speak(message)
            return

        self.process_text(text)

    def voice_conversation(self):
        speak('I am listening.')
        self.listen_and_send()

    @staticmethod
    def stylesheet():
        return """
        QWidget {
            background-color: #0f172a;
            color: #e5e7eb;
            font-family: Segoe UI, Arial;
            font-size: 14px;
        }
        QFrame#panel, QFrame#chatPanel {
            background-color: #111827;
            border: 1px solid #243244;
            border-radius: 18px;
        }
        QLabel#title {
            color: #38bdf8;
            font-size: 34px;
            font-weight: 800;
            letter-spacing: 3px;
        }
        QLabel#subtitle, QLabel#footer, QLabel#cardText {
            color: #94a3b8;
        }
        QLabel#status {
            color: #22c55e;
            font-weight: 700;
        }
        QLabel#sectionTitle {
            color: #f8fafc;
            font-size: 22px;
            font-weight: 700;
        }
        QFrame#card {
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 14px;
        }
        QLabel#cardTitle {
            color: #c084fc;
            font-size: 16px;
            font-weight: 700;
        }
        QTextEdit#chat {
            background-color: #020617;
            border: 1px solid #1e293b;
            border-radius: 14px;
            padding: 14px;
            color: #e5e7eb;
            font-size: 15px;
        }
        QLineEdit {
            background-color: #020617;
            border: 1px solid #334155;
            border-radius: 14px;
            padding: 12px;
            color: #f8fafc;
        }
        QPushButton {
            background-color: #2563eb;
            color: white;
            border: none;
            border-radius: 14px;
            padding: 12px;
            font-weight: 700;
        }
        QPushButton:hover {
            background-color: #38bdf8;
            color: #020617;
        }
        .jarvis {
            color: #38bdf8;
            font-weight: 700;
        }
        .user {
            color: #c084fc;
            font-weight: 700;
        }
        """


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = JarvisWindow()
    window.show()
    sys.exit(app.exec())
