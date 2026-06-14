from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton
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

        self.setWindowTitle('Jarvis AI')
        self.resize(700, 500)

        layout = QVBoxLayout()

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)

        self.input_box = QLineEdit()
        self.input_box.returnPressed.connect(self.send_message)

        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.send_message)

        self.voice_button = QPushButton('Start Listening')
        self.voice_button.clicked.connect(self.listen_and_send)

        layout.addWidget(self.chat)
        layout.addWidget(self.input_box)
        layout.addWidget(self.send_button)
        layout.addWidget(self.voice_button)

        self.setLayout(layout)
        self.chat.append('Jarvis: Hello Panagiota! Voice mode is available.')

    def process_text(self, text: str):
        self.chat.append(f'You: {text}')

        response = self.commands.handle(text)

        if response == 'EXIT':
            self.close()
            return

        if response is None:
            response = self.brain.answer(text)

        self.chat.append(f'Jarvis: {response}')
        speak(response)

    def send_message(self):
        text = self.input_box.text().strip()
        if not text:
            return

        self.process_text(text)
        self.input_box.clear()

    def listen_and_send(self):
        self.chat.append('Jarvis: Listening...')
        text = listen()

        if not text:
            self.chat.append('Jarvis: I could not hear anything.')
            return

        self.process_text(text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = JarvisWindow()
    window.show()
    sys.exit(app.exec())