from pathlib import Path
import datetime as dt
import subprocess


class VisionAssistant:
    def __init__(self, output_dir: str = "screenshots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

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
        image_path = self.capture_screen()
        if image_path.startswith("SCREENSHOT_ERROR"):
            return (
                "I could not capture the screen. "
                "If you are using WSL, make sure Windows PowerShell is available. "
                f"Details: {image_path}"
            )

        ocr_text = self._try_ocr(image_path)
        if ocr_text:
            return (
                f"Screen captured: {image_path}\n\n"
                "Text detected on screen:\n"
                f"{ocr_text[:4000]}\n\n"
                "You can ask me to explain this screen, debug it, summarize it, or turn it into study notes."
            )

        return (
            f"Screen captured: {image_path}\n\n"
            "I captured the screen, but I could not extract readable text. "
            "If this is a slide, image, or app screen, we can add stronger computer vision in the next step."
        )

    def _try_ocr(self, image_path: str) -> str:
        try:
            from PIL import Image
            import pytesseract
            text = pytesseract.image_to_string(Image.open(image_path))
            return text.strip()
        except Exception:
            return ""
