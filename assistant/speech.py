import asyncio
import os
import shutil
import subprocess
import tempfile
import threading

LANGUAGE = os.getenv("JARVIS_LANGUAGE", "en")


def set_language(language: str) -> None:
    global LANGUAGE
    LANGUAGE = "el" if language.lower().startswith("el") or language.lower().startswith("gr") else "en"


def get_language() -> str:
    return LANGUAGE


def _voice_for_language() -> str:
    if LANGUAGE == "el":
        return os.getenv("JARVIS_EDGE_VOICE_EL", "el-GR-AthinaNeural")
    return os.getenv("JARVIS_EDGE_VOICE_EN", "en-US-AriaNeural")


def speak_async(text: str) -> None:
    thread = threading.Thread(target=speak, args=(text,), daemon=True)
    thread.start()


def speak(text: str) -> None:
    clean_text = text.strip()
    if not clean_text:
        return

    voice = _voice_for_language()
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
                timeout=90,
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


def _preferred_microphone_index(microphones: list[str]) -> int | None:
    if not microphones:
        return None

    preferred_names = ["pulse", "default", "rdpsource", "microphone", "mic"]
    for preferred in preferred_names:
        for index, name in enumerate(microphones):
            if preferred in name.lower():
                return index

    return 0


def listen() -> str:
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()

        microphones = sr.Microphone.list_microphone_names()
        device_index = _preferred_microphone_index(microphones)
        if device_index is None:
            return ""

        with sr.Microphone(device_index=device_index) as source:
            print(f"Listening with microphone: {microphones[device_index]}")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=12)

        primary = "el-GR" if LANGUAGE == "el" else "en-US"
        secondary = "en-US" if LANGUAGE == "el" else "el-GR"

        try:
            return recognizer.recognize_google(audio, language=primary)
        except Exception:
            return recognizer.recognize_google(audio, language=secondary)
    except Exception:
        return ""
