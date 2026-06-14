from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QFrame
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
import sys
from dotenv import load_dotenv

load_dotenv()

from assistant.brain import Brain
from assistant.commands import CommandHandler
from assistant.memory import Memory
from assistant.speech import listen, speak_async, set_language, get_language


class ResponseWorker(QThread):
    finished = pyqtSignal(str, str)

    def __init__(self, text: str, brain: Brain, commands: CommandHandler):
        super().__init__()
        self.text = text
        self.brain = brain
        self.commands = commands

    def run(self):
        response = self.commands.handle(self.text)
        if response is None:
            response = self.brain.answer(self.text)
        self.finished.emit(self.text, response)


class ListenWorker(QThread):
    finished = pyqtSignal(str)

    def run(self):
        self.finished.emit(listen())


class AmbientWorker(QThread):
    heard = pyqtSignal(str)
    status = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = True
        self.awaiting_command = False
        self.wake_words = ["jarvis", "hey jarvis", "τζάρβις", "τζαρβις", "άνοιξε", "ανοιξε"]
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
                self.heard.emit(text)
                continue

            if any(word in lower for word in self.wake_words):
                self.awaiting_command = True
                self.status.emit("Awake")
                self.heard.emit("__WAKE__")


class JarvisWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.brain = Brain()
        self.memory = Memory()
        self.commands = CommandHandler(self.memory)
        self.response_worker = None
        self.listen_worker = None
        self.ambient_worker = None
        self.language = get_language()

        self.setWindowTitle('Jarvis AI Assistant')
        self.resize(980, 680)
        self.setStyleSheet(self.stylesheet())

        root = QVBoxLayout()
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(16)
        root.addWidget(self.build_header())
        root.addWidget(self.build_chat())
        self.setLayout(root)

        self.apply_language_text()
        QTimer.singleShot(1000, self.startup_greeting)
        QTimer.singleShot(2500, self.start_ambient_mode)

    def build_header(self):
        panel = QFrame()
        panel.setObjectName('hero')
        layout = QHBoxLayout()

        left = QVBoxLayout()
        self.title = QLabel('JARVIS')
        self.title.setObjectName('title')
        self.subtitle = QLabel('Smart Personal Assistant')
        self.subtitle.setObjectName('subtitle')
        self.status = QLabel('Online')
        self.status.setObjectName('status')
        left.addWidget(self.title)
        left.addWidget(self.subtitle)
        left.addWidget(self.status)

        self.language_button = QPushButton('English')
        self.language_button.clicked.connect(self.toggle_language)

        layout.addLayout(left, 4)
        layout.addWidget(self.language_button, 1)
        panel.setLayout(layout)
        return panel

    def build_chat(self):
        panel = QFrame()
        panel.setObjectName('chatPanel')
        layout = QVBoxLayout()

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setObjectName('chat')

        row = QHBoxLayout()
        self.input_box = QLineEdit()
        self.input_box.returnPressed.connect(self.send_message)
        self.listen_button = QPushButton('Mic')
        self.listen_button.clicked.connect(self.listen_and_send)
        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.send_message)

        row.addWidget(self.input_box, 7)
        row.addWidget(self.listen_button, 1)
        row.addWidget(self.send_button, 1)

        layout.addWidget(self.chat)
        layout.addLayout(row)
        panel.setLayout(layout)
        return panel

    def startup_greeting(self):
        greeting = 'Good morning Panagiota. I am ready. Say Jarvis when you need me.'
        if self.language == 'el':
            greeting = 'Καλημέρα Παναγιώτα. Είμαι έτοιμος. Πες Jarvis όταν με χρειαστείς.'
        self.chat.append(f'<span class="jarvis">Jarvis:</span> {greeting}')
        speak_async(greeting)
        self.process_text('daily briefing', show_user=False)

    def start_ambient_mode(self):
        if self.ambient_worker and self.ambient_worker.isRunning():
            return
        self.ambient_worker = AmbientWorker()
        self.ambient_worker.heard.connect(self.on_ambient_heard)
        self.ambient_worker.status.connect(self.on_ambient_status)
        self.ambient_worker.start()

    def on_ambient_status(self, text: str):
        self.status.setText(text)

    def on_ambient_heard(self, text: str):
        if text == '__WAKE__':
            message = 'I am listening. What would you like to do?' if self.language == 'en' else 'Σε ακούω. Τι θέλεις να κάνουμε;'
            self.chat.append(f'<span class="jarvis">Jarvis:</span> {message}')
            speak_async(message)
            return
        self.process_text(text)

    def toggle_language(self):
        self.language = 'el' if self.language == 'en' else 'en'
        set_language(self.language)
        self.apply_language_text()
        message = 'Language changed to English.' if self.language == 'en' else 'Η γλώσσα άλλαξε σε Ελληνικά.'
        self.chat.append(f'<span class="jarvis">Jarvis:</span> {message}')
        speak_async(message)

    def apply_language_text(self):
        if self.language == 'el':
            self.subtitle.setText('Έξυπνος Προσωπικός Βοηθός')
            self.language_button.setText('Ελληνικά')
            self.input_box.setPlaceholderText('Πες ή γράψε κάτι στον Jarvis...')
            self.send_button.setText('Αποστολή')
            self.listen_button.setText('Μικρόφωνο')
        else:
            self.subtitle.setText('Smart Personal Assistant')
            self.language_button.setText('English')
            self.input_box.setPlaceholderText('Say or type something to Jarvis...')
            self.send_button.setText('Send')
            self.listen_button.setText('Mic')

    def set_busy(self, is_busy: bool, text: str = 'Online'):
        self.send_button.setDisabled(is_busy)
        self.listen_button.setDisabled(is_busy)
        if text:
            self.status.setText(text)

    def process_text(self, text: str, show_user: bool = True):
        if self.response_worker and self.response_worker.isRunning():
            return
        if show_user:
            self.chat.append(f'<span class="user">You:</span> {text}')
        self.chat.append('<span class="jarvis">Jarvis:</span> Thinking...')
        self.set_busy(True, 'Thinking')
        self.response_worker = ResponseWorker(text, self.brain, self.commands)
        self.response_worker.finished.connect(self.on_response_ready)
        self.response_worker.start()

    def on_response_ready(self, text: str, response: str):
        if response == 'EXIT':
            self.close()
            return
        safe_response = response.replace('\n', '<br>')
        self.chat.append(f'<span class="jarvis">Jarvis:</span> {safe_response}')
        speak_async(response)
        self.set_busy(False, 'Listening for Jarvis')

    def send_message(self):
        text = self.input_box.text().strip()
        if text:
            self.process_text(text)
            self.input_box.clear()

    def listen_and_send(self):
        if self.listen_worker and self.listen_worker.isRunning():
            return
        self.chat.append('<span class="jarvis">Jarvis:</span> Listening...')
        self.set_busy(True, 'Listening')
        self.listen_worker = ListenWorker()
        self.listen_worker.finished.connect(self.on_listen_ready)
        self.listen_worker.start()

    def on_listen_ready(self, text: str):
        self.set_busy(False, 'Listening for Jarvis')
        if not text:
            message = 'I could not hear clearly. Try again.' if self.language == 'en' else 'Δεν άκουσα κάτι καθαρά. Δοκίμασε ξανά.'
            self.chat.append(f'<span class="jarvis">Jarvis:</span> {message}')
            speak_async(message)
            return
        self.process_text(text)

    def closeEvent(self, event):
        if self.ambient_worker:
            self.ambient_worker.stop()
        event.accept()

    @staticmethod
    def stylesheet():
        return """
        QWidget { background-color: #0f172a; color: #e5e7eb; font-family: Segoe UI, Arial; font-size: 14px; }
        QFrame#hero, QFrame#chatPanel { background-color: #111827; border: 1px solid #243244; border-radius: 22px; }
        QLabel#title { color: #38bdf8; font-size: 42px; font-weight: 900; letter-spacing: 4px; }
        QLabel#subtitle { color: #c084fc; font-size: 16px; font-weight: 700; }
        QLabel#status { color: #22c55e; font-weight: 700; }
        QTextEdit#chat { background-color: #020617; border: 1px solid #1e293b; border-radius: 18px; padding: 16px; color: #e5e7eb; font-size: 15px; }
        QLineEdit { background-color: #020617; border: 1px solid #334155; border-radius: 18px; padding: 14px; color: #f8fafc; }
        QPushButton { background-color: #2563eb; color: white; border: none; border-radius: 16px; padding: 13px; font-weight: 800; }
        QPushButton:hover { background-color: #38bdf8; color: #020617; }
        QPushButton:disabled { background-color: #334155; color: #94a3b8; }
        .jarvis { color: #38bdf8; font-weight: 700; }
        .user { color: #c084fc; font-weight: 700; }
        """


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = JarvisWindow()
    window.show()
    sys.exit(app.exec())
