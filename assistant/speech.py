def speak(text: str) -> None:
    try:
        import pyttsx3
    except ImportError:
        print(text)
        return

    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def listen() -> str:
    try:
        import speech_recognition as sr
    except ImportError:
        return input("You: ")

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return input("Speech service unavailable. Type instead: ")
