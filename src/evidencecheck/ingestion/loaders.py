"""Load .txt/.md/.pdf into page-level records."""
from __future__ import annotations
import re
from pathlib import Path


def clean_text(t: str) -> str:
    return re.sub(r"[ \t]+", " ", re.sub(r"\r\n?", "\n", t)).strip()


def load_documents(folder: Path) -> list[dict]:
    """Return records: document_id, source, page, text."""
    docs: list[dict] = []
    for p in sorted(Path(folder).glob("*")):
        if p.suffix.lower() in {".txt", ".md"}:
            pages = [(None, p.read_text(encoding="utf-8", errors="ignore"))]
        elif p.suffix.lower() == ".pdf":
            from pypdf import PdfReader
            pages = [(i + 1, pg.extract_text() or "") for i, pg in enumerate(PdfReader(str(p)).pages)]
        else:
            continue
        for page, text in pages:
            text = clean_text(text)
            if text:
                docs.append({"document_id": p.stem, "source": p.name, "page": page, "text": text})
    return docs


def load_uploaded(name: str, data: bytes) -> list[dict]:
    """Parse an uploaded .txt/.md/.pdf (bytes) into page-level records."""
    import io
    stem, ext = name.rsplit(".", 1)[0], name.rsplit(".", 1)[-1].lower()
    if ext in ("txt", "md"):
        pages = [(None, data.decode("utf-8", errors="ignore"))]
    elif ext == "pdf":
        from pypdf import PdfReader
        pages = [(i + 1, pg.extract_text() or "") for i, pg in enumerate(PdfReader(io.BytesIO(data)).pages)]
    else:
        raise ValueError("Unsupported file type. Use .txt, .md or .pdf")
    return [{"document_id": stem, "source": name, "page": pg, "text": clean_text(t)} for pg, t in pages if clean_text(t)]
