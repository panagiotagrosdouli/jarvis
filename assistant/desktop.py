import os
import platform
import shutil
import subprocess
import webbrowser


class DesktopAutomation:
    def __init__(self):
        self.system = platform.system().lower()

    def open_url(self, url: str) -> str:
        webbrowser.open(url)
        return f"Opening {url}"

    def open_app(self, app_name: str) -> str:
        app = app_name.strip().lower()

        aliases = {
            "chrome": ["google-chrome", "google-chrome-stable", "chrome"],
            "google chrome": ["google-chrome", "google-chrome-stable", "chrome"],
            "vscode": ["code"],
            "vs code": ["code"],
            "visual studio code": ["code"],
            "spotify": ["spotify"],
            "calculator": ["gnome-calculator", "kcalc", "xcalc"],
            "files": ["nautilus", "xdg-open"],
        }

        commands = aliases.get(app, [app])

        for command in commands:
            executable = shutil.which(command)
            if executable:
                try:
                    subprocess.Popen([executable], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return f"Opening {app_name}."
                except Exception as exc:
                    return f"I found {app_name}, but could not open it: {exc}"

        return f"I could not find {app_name} on this system."

    def search_google(self, query: str) -> str:
        clean_query = query.strip()
        if not clean_query:
            return "Tell me what to search for."
        url = "https://www.google.com/search?q=" + clean_query.replace(" ", "+")
        webbrowser.open(url)
        return f"Searching Google for: {clean_query}"

    def search_youtube(self, query: str) -> str:
        clean_query = query.strip()
        if not clean_query:
            return "Tell me what to search on YouTube."
        url = "https://www.youtube.com/results?search_query=" + clean_query.replace(" ", "+")
        webbrowser.open(url)
        return f"Searching YouTube for: {clean_query}"
