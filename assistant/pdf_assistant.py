from pathlib import Path


class PDFAssistant:
    def extract_text(self, file_path: str, max_chars: int = 12000) -> str:
        path = Path(file_path).expanduser()
        if not path.exists():
            return f"PDF not found: {path}"
        if path.suffix.lower() != ".pdf":
            return "Please provide a PDF file path."

        try:
            from pypdf import PdfReader
        except Exception:
            return "Missing dependency: install pypdf with: pip install pypdf"

        try:
            reader = PdfReader(str(path))
            parts: list[str] = []
            for page_number, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                if text.strip():
                    parts.append(f"Page {page_number}:\n{text.strip()}")
                if sum(len(part) for part in parts) >= max_chars:
                    break
            content = "\n\n".join(parts).strip()
            if not content:
                return "I could not extract readable text from this PDF. It may be scanned or image-based."
            return content[:max_chars]
        except Exception as exc:
            return f"PDF reading error: {exc}"

    def build_prompt(self, file_path: str, mode: str) -> str:
        text = self.extract_text(file_path)
        if text.startswith("PDF not found") or text.startswith("Please provide") or text.startswith("Missing dependency") or text.startswith("I could not") or text.startswith("PDF reading error"):
            return text

        if mode == "summary":
            task = (
                "Create university-level study notes from this PDF. Include: "
                "1. short summary, 2. main concepts, 3. important definitions, "
                "4. step-by-step explanation, 5. what to study first."
            )
        elif mode == "flashcards":
            task = (
                "Create 15 study flashcards from this PDF. Use clear question-answer format. "
                "Focus on concepts that are likely to appear in exams."
            )
        elif mode == "quiz":
            task = (
                "Create a quiz from this PDF with 10 questions. Include multiple choice questions, "
                "short answer questions, and the correct answers at the end."
            )
        elif mode == "exam":
            task = (
                "Create likely exam questions from this PDF. Include theory questions, practical questions, "
                "and a short answer guide for each one."
            )
        else:
            task = "Analyze this PDF clearly for university study."

        return f"{task}\n\nPDF content:\n{text}"
