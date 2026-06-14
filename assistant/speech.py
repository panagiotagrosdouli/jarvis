import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def speak(text: str) -> None:
    clean_text = text.strip()
    if not clean_text:
        return

    model_path = Path(os.getenv("PIPER_VOICE_MODEL", "voices/en_US-amy-medium.onnx"))
    piper_bin = shutil.which("piper")
    ffplay_bin = shutil.which("ffplay")

    if piper_bin and ffplay_bin and model_path.exists():
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                output_path = temp_audio.name

            subprocess.run(
                [piper_bin, "--model", str(model_path), "--output-file", output_path],
                input=clean_text,
                text=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
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
