import asyncio
import os
import shutil
import subprocess
import tempfile


def speak(text: str) -> None:
    clean_text = text.strip()
    if not clean_text:
        return

    voice = os.getenv("JARVIS_EDGE_VOICE", "en-US-AriaNeural")
    ffplay_bin = shutil.which("ffplay")

    try:
        import edge_tts

        async def _save_audio(output_path: str) -> None:
            communicate = edge_tts.Communicate(clean_text, voice)
            await communicate.save(output_path)

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
            output_path = temp_audio.name

        asyncio.run(_save_audio(output_path))

        if ffplay_bin:
            subprocess.run(
                [ffplay_bin, "-nodisp", "-autoexit", "-loglevel", "quiet", output_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )

        try:
            os.remove(output_path)
        except OSError:
            pass
        return
    except Exception:
        pass

    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(clean_text)
        engine.runAndWait()
    except Exception:
        print(clean_text)


def listen() -> str:
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()

        microphones = sr.Microphone.list_microphone_names()
        if not microphones:
            return ""

        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

        return recognizer.recognize_google(audio, language="el-GR")
    except Exception:
        return ""
