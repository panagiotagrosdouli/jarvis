from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton
import sys

from assistant.brain import Brain
from assistant.commands import CommandHandler
from assistant.memory import Memory


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

        self.button = QPushButton('Send')
        self.button.clicked.connect(self.send_message)

        layout.addWidget(self.chat)
        layout.addWidget(self.input_box)
        layout.addWidget(self.button)

        self.setLayout(layout)
        self.chat.append('Jarvis: Hello Panagiota!')

    def send_message(self):
        text = self.input_box.text().strip()
        if not text:
            return

        self.chat.append(f'You: {text}')

        response = self.commands.handle(text)
        if response == 'EXIT':
            self.close()
            return

        if response is None:
            response = self.brain.answer(text)

        self.chat.append(f'Jarvis: {response}')
        self.input_box.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = JarvisWindow()
    window.show()
    sys.exit(app.exec())
