from pathlib import Path
import datetime as dt
import subprocess

from assistant.brain import Brain


class VisionAssistant:
    def __init__(self, output_dir: str = "screenshots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.brain = Brain()

    def capture_screen(self) -> str:
        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self.output_dir / f"screen_{timestamp}.png"

        windows_result = self._capture_with_windows_powershell(path)
        if windows_result:
            return windows_result

        try:
            import pyautogui
            image = pyautogui.screenshot()
            image.save(path)
            return str(path)
        except Exception as exc:
            return f"SCREENSHOT_ERROR: {exc}"

    def _capture_with_windows_powershell(self, path: Path) -> str | None:
        try:
            windows_path = self._wsl_to_windows_path(path)
            script = f"""
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
$bitmap.Save('{windows_path}', [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$bitmap.Dispose()
"""
            result = subprocess.run(
                ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=15,
                check=False,
            )
            if result.returncode == 0 and path.exists():
                return str(path)
        except Exception:
            return None
        return None

    def _wsl_to_windows_path(self, path: Path) -> str:
        try:
            result = subprocess.run(
                ["wslpath", "-w", str(path.resolve())],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().replace("'", "''")
        except Exception:
            pass
        return str(path.resolve()).replace("'", "''")

    def analyze_screen(self) -> str:
        return self._analyze_with_ai("analysis")

    def explain_screen(self) -> str:
        return self._analyze_with_ai("explain")

    def summarize_screen(self) -> str:
        return self._analyze_with_ai("summary")

    def flashcards_from_screen(self) -> str:
        return self._analyze_with_ai("flashcards")

    def quiz_from_screen(self) -> str:
        return self._analyze_with_ai("quiz")

    def raw_screen_text(self) -> str:
        image_path, ocr_text, error = self._capture_and_read()
        if error:
            return error
        if not ocr_text:
            return (
                f"Screen captured: {image_path}\n\n"
                "I captured the screen, but I could not extract readable text."
            )
        return f"Screen captured: {image_path}\n\nText detected on screen:\n{ocr_text[:4000]}"

    def _capture_and_read(self) -> tuple[str, str, str | None]:
        image_path = self.capture_screen()
        if image_path.startswith("SCREENSHOT_ERROR"):
            return "", "", (
                "I could not capture the screen. "
                "If you are using WSL, make sure Windows PowerShell is available. "
                f"Details: {image_path}"
            )
        return image_path, self._try_ocr(image_path), None

    def _analyze_with_ai(self, mode: str) -> str:
        image_path, ocr_text, error = self._capture_and_read()
        if error:
            return error

        if not ocr_text:
            return (
                f"Screen captured: {image_path}\n\n"
                "I captured the screen, but I could not extract readable text. "
                "Open a page with visible text, a PDF, notes, code, or a slide and try again."
            )

        task = self._task_for_mode(mode)
        prompt = (
            f"{task}\n\n"
            "You are analyzing OCR text extracted from the user's current screen. "
            "Be practical and clear. If it looks like code, point out possible problems. "
            "If it looks like university material, explain it like a study tutor. "
            "If the OCR is messy, infer carefully and mention uncertainty.\n\n"
            f"Screenshot path: {image_path}\n\n"
            f"Screen OCR text:\n{ocr_text[:9000]}"
        )
        answer = self.brain.answer(prompt)
        return f"Screen captured: {image_path}\n\n{answer}"

    def _task_for_mode(self, mode: str) -> str:
        if mode == "summary":
            return "Summarize what is on the screen in a short, useful way."
        if mode == "explain":
            return "Explain what is on the screen step by step, as if teaching the user."
        if mode == "flashcards":
            return "Create useful study flashcards from the screen content. Use Question and Answer format."
        if mode == "quiz":
            return "Create a short quiz from the screen content and include the correct answers."
        return (
            "Analyze the current screen. Identify what the user appears to be looking at, "
            "summarize the important information, and suggest the next useful action."
        )

    def _try_ocr(self, image_path: str) -> str:
        try:
            from PIL import Image
            import pytesseract
            text = pytesseract.image_to_string(Image.open(image_path))
            return text.strip()
        except Exception:
            return ""
