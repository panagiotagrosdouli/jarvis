from pathlib import Path
import datetime as dt


class VisionAssistant:
    def __init__(self, output_dir: str = "screenshots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def capture_screen(self) -> str:
        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self.output_dir / f"screen_{timestamp}.png"

        try:
            import pyautogui
            image = pyautogui.screenshot()
            image.save(path)
            return str(path)
        except Exception as exc:
            return f"SCREENSHOT_ERROR: {exc}"

    def analyze_screen(self) -> str:
        image_path = self.capture_screen()
        if image_path.startswith("SCREENSHOT_ERROR"):
            return (
                "I could not capture the screen. "
                "Install the required packages and make sure screen capture is allowed. "
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
