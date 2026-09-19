from pathlib import Path

import pymupdf

SUPPORTED_SUFFIXES = {".pdf", ".txt"}

def extract_text(file_path: Path) -> str:
    path = Path(file_path)
    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix.lower() == ".pdf":
        with pymupdf.open(path) as pdf:
            return "\n".join(page.get_text() for page in pdf)
    raise ValueError("Only PDF and TXT files are supported.")
