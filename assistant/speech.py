def speak(text: str) -> None:
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception:
        print(text)


def listen() -> str:
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()

        try:
            microphone = sr.Microphone()
        except Exception:
            return ""

        with microphone as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

        return recognizer.recognize_google(audio, language="el-GR")
    except Exception:
        return ""
