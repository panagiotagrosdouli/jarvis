import os
from dotenv import load_dotenv

from assistant.brain import Brain
from assistant.commands import CommandHandler
from assistant.memory import Memory
from assistant.speech import listen, speak


def main() -> None:
    load_dotenv()

    voice_enabled = os.getenv("JARVIS_VOICE", "false").lower() == "true"
    brain = Brain()
    memory = Memory()
    commands = CommandHandler(memory)

    greeting = "Hello, I am Jarvis. Type help to see what I can do."
    print(greeting)
    if voice_enabled:
        speak(greeting)

    while True:
        user_text = listen() if voice_enabled else input("You: ")
        if not user_text.strip():
            continue

        command_response = commands.handle(user_text)
        if command_response == "EXIT":
            goodbye = "Goodbye."
            print(f"Jarvis: {goodbye}")
            if voice_enabled:
                speak(goodbye)
            break

        if command_response is not None:
            response = command_response
        else:
            response = brain.answer(user_text)

        print(f"Jarvis: {response}")
        if voice_enabled:
            speak(response)


if __name__ == "__main__":
    main()
