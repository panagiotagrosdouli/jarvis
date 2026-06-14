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
from PyQt6.QtCore import QThread, pyqtSignal
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


class JarvisWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.brain = Brain()
        self.memory = Memory()
        self.commands = CommandHandler(self.memory)
        self.response_worker = None
        self.listen_worker = None
        self.language = get_language()

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
        self.apply_language_text()
        self.chat.append('<span class="jarvis">Jarvis:</span> Welcome back, Panagiota. Voice mode is active.')

    def build_sidebar(self):
        panel = QFrame()
        panel.setObjectName('panel')
        layout = QVBoxLayout()
        layout.setSpacing(14)

        title = QLabel('JARVIS')
        title.setObjectName('title')
        self.subtitle = QLabel('Personal AI Companion')
        self.subtitle.setObjectName('subtitle')

        self.status = QLabel('● Online')
        self.status.setObjectName('status')

        self.language_button = QPushButton('🌐 Language: English')
        self.language_button.clicked.connect(self.toggle_language)

        self.voice_button = QPushButton('🎤 Listen')
        self.voice_button.clicked.connect(self.listen_and_send)

        self.voice_chat_button = QPushButton('🗣 Voice Conversation')
        self.voice_chat_button.clicked.connect(self.voice_conversation)

        self.briefing_button = QPushButton('☀ Daily Briefing')
        self.briefing_button.clicked.connect(lambda: self.process_text('daily briefing'))

        self.tasks_button = QPushButton('✅ Tasks')
        self.tasks_button.clicked.connect(lambda: self.process_text('tasks'))

        self.study_button = QPushButton('🎓 Study Mode')
        self.study_button.clicked.connect(lambda: self.process_text('study mode'))

        self.home_button = QPushButton('🏠 Home Mode')
        self.home_button.clicked.connect(lambda: self.process_text('home mode'))

        layout.addWidget(title)
        layout.addWidget(self.subtitle)
        layout.addWidget(self.status)
        layout.addSpacing(12)
        layout.addWidget(self.language_button)
        layout.addWidget(self.voice_button)
        layout.addWidget(self.voice_chat_button)
        layout.addWidget(self.briefing_button)
        layout.addWidget(self.tasks_button)
        layout.addWidget(self.study_button)
        layout.addWidget(self.home_button)
        layout.addStretch()

        self.footer = QLabel('Always ready to help')
        self.footer.setObjectName('footer')
        layout.addWidget(self.footer)

        panel.setLayout(layout)
        return panel

    def build_chat_panel(self):
        panel = QFrame()
        panel.setObjectName('chatPanel')
        layout = QVBoxLayout()
        layout.setSpacing(12)

        self.header = QLabel('AI Conversation')
        self.header.setObjectName('sectionTitle')

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

        layout.addWidget(self.header)
        layout.addWidget(self.chat)
        layout.addLayout(input_row)
        panel.setLayout(layout)
        return panel

    def build_info_panel(self):
        panel = QFrame()
        panel.setObjectName('panel')
        layout = QVBoxLayout()
        layout.setSpacing(14)

        self.today_card = self.card('Today', 'Daily briefing, tasks, study goals')
        self.voice_card = self.card('Voice', 'English Neural Voice enabled')
        self.memory_card = self.card('Memory', 'Personal facts and reminders')
        self.modes_card = self.card('Modes', 'Study • Home • Evening')

        layout.addWidget(self.today_card)
        layout.addWidget(self.voice_card)
        layout.addWidget(self.memory_card)
        layout.addWidget(self.modes_card)
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
        frame.title_label = label
        frame.body_label = text
        return frame

    def toggle_language(self):
        self.language = 'el' if self.language == 'en' else 'en'
        set_language(self.language)
        self.apply_language_text()
        message = 'Language changed to Greek.' if self.language == 'el' else 'Language changed to English.'
        if self.language == 'el':
            message = 'Η γλώσσα άλλαξε σε Ελληνικά.'
        self.chat.append(f'<span class="jarvis">Jarvis:</span> {message}')
        speak_async(message)

    def apply_language_text(self):
        if self.language == 'el':
            self.subtitle.setText('Προσωπικός AI Βοηθός')
            self.language_button.setText('🌐 Γλώσσα: Ελληνικά')
            self.voice_button.setText('🎤 Άκουσέ με')
            self.voice_chat_button.setText('🗣 Φωνητική Συνομιλία')
            self.briefing_button.setText('☀ Πρωινό Briefing')
            self.tasks_button.setText('✅ Εργασίες')
            self.study_button.setText('🎓 Λειτουργία Διαβάσματος')
            self.home_button.setText('🏠 Λειτουργία Σπιτιού')
            self.footer.setText('Πάντα έτοιμος να βοηθήσω')
            self.header.setText('Συνομιλία AI')
            self.input_box.setPlaceholderText('Ρώτα τον Jarvis οτιδήποτε...')
            self.today_card.title_label.setText('Σήμερα')
            self.today_card.body_label.setText('Πρωινό briefing, εργασίες, στόχοι διαβάσματος')
            self.voice_card.title_label.setText('Φωνή')
            self.voice_card.body_label.setText('Ελληνική Neural φωνή ενεργή')
            self.memory_card.title_label.setText('Μνήμη')
            self.memory_card.body_label.setText('Προσωπικά στοιχεία και υπενθυμίσεις')
            self.modes_card.title_label.setText('Λειτουργίες')
            self.modes_card.body_label.setText('Διάβασμα • Σπίτι • Βράδυ')
        else:
            self.subtitle.setText('Personal AI Companion')
            self.language_button.setText('🌐 Language: English')
            self.voice_button.setText('🎤 Listen')
            self.voice_chat_button.setText('🗣 Voice Conversation')
            self.briefing_button.setText('☀ Daily Briefing')
            self.tasks_button.setText('✅ Tasks')
            self.study_button.setText('🎓 Study Mode')
            self.home_button.setText('🏠 Home Mode')
            self.footer.setText('Always ready to help')
            self.header.setText('AI Conversation')
            self.input_box.setPlaceholderText('Ask Jarvis anything...')
            self.today_card.title_label.setText('Today')
            self.today_card.body_label.setText('Daily briefing, tasks, study goals')
            self.voice_card.title_label.setText('Voice')
            self.voice_card.body_label.setText('English Neural Voice enabled')
            self.memory_card.title_label.setText('Memory')
            self.memory_card.body_label.setText('Personal facts and reminders')
            self.modes_card.title_label.setText('Modes')
            self.modes_card.body_label.setText('Study • Home • Evening')

    def set_busy(self, is_busy: bool, text: str = '● Online'):
        self.send_button.setDisabled(is_busy)
        self.voice_button.setDisabled(is_busy)
        self.voice_chat_button.setDisabled(is_busy)
        self.status.setText(text)

    def process_text(self, text: str):
        if self.response_worker and self.response_worker.isRunning():
            msg = 'Please wait for the previous answer to finish.' if self.language == 'en' else 'Περίμενε να τελειώσει η προηγούμενη απάντηση.'
            self.chat.append(f'<span class="jarvis">Jarvis:</span> {msg}')
            return

        self.chat.append(f'<span class="user">You:</span> {text}')
        thinking = 'Thinking...' if self.language == 'en' else 'Σκέφτομαι...'
        self.chat.append(f'<span class="jarvis">Jarvis:</span> {thinking}')
        self.set_busy(True, '● Thinking')

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
        self.set_busy(False, '● Online')

    def send_message(self):
        text = self.input_box.text().strip()
        if not text:
            return

        self.process_text(text)
        self.input_box.clear()

    def listen_and_send(self):
        if self.listen_worker and self.listen_worker.isRunning():
            return

        listening = 'Listening...' if self.language == 'en' else 'Σε ακούω...'
        self.chat.append(f'<span class="jarvis">Jarvis:</span> {listening}')
        self.set_busy(True, '● Listening')
        self.listen_worker = ListenWorker()
        self.listen_worker.finished.connect(self.on_listen_ready)
        self.listen_worker.start()

    def on_listen_ready(self, text: str):
        self.set_busy(False, '● Online')
        if not text:
            message = 'I could not hear clearly. Check your microphone and try again.'
            if self.language == 'el':
                message = 'Δεν άκουσα κάτι καθαρά. Έλεγξε το μικρόφωνο και δοκίμασε ξανά.'
            self.chat.append(f'<span class="jarvis">Jarvis:</span> {message}')
            speak_async(message)
            return

        self.process_text(text)

    def voice_conversation(self):
        message = 'I am listening.' if self.language == 'en' else 'Σε ακούω.'
        speak_async(message)
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
        QPushButton:disabled {
            background-color: #334155;
            color: #94a3b8;
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
