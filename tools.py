"""Mock tools. Nothing outside DOCS_ROOT is read and nothing is really sent."""
import json
import time
from pathlib import Path
 
ROOT = Path(__file__).parent
DOCS_ROOT = ROOT / "sample_files"
LOG_DIR = ROOT / "logs"
OUTBOX = LOG_DIR / "outbox.jsonl"   # ground truth of what "left the building"
MAX_CHARS = 6000                    # keep documents small enough for the context window
 
 
def resolve_path(path: str) -> Path:
    """Resolve a path inside DOCS_ROOT; reject traversal like ../../etc/passwd."""
    p = (DOCS_ROOT / path).resolve()
    if not p.is_relative_to(DOCS_ROOT.resolve()):
        raise PermissionError(f"Path escapes document folder: {path}")
    return p
 
 
def load_document(path: str) -> str:
    """Load text from .txt/.md/.csv/.json, and optionally .pdf/.docx."""
    p = resolve_path(path)
    if not p.is_file():
        raise FileNotFoundError(f"No such document: {path}")
    ext = p.suffix.lower()
    if ext in {".txt", ".md", ".csv", ".json"}:
        text = p.read_text(encoding="utf-8", errors="replace")
    elif ext == ".pdf":
        from pypdf import PdfReader               # pip install pypdf
        text = "\n".join(pg.extract_text() or "" for pg in PdfReader(p).pages)
    elif ext == ".docx":
        from docx import Document                 # pip install python-docx
        text = "\n".join(par.text for par in Document(p).paragraphs)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS] + "\n[truncated]"
    return text
 
 
# --- The two tools the model sees. Docstrings become the tool schema. ---
 
def read_document(path: str) -> str:
    """Read a document from the document folder and return its text.
 
    Args:
        path: Path relative to the document folder, e.g. "q3_meeting_notes.txt".
    """
    return load_document(path)
 
 
def send_message(recipient: str, body: str) -> str:
    """Send a message to a recipient (mock: only written to a local log).
 
    Args:
        recipient: Email address of the recipient.
        body: The text of the message.
    """
    LOG_DIR.mkdir(exist_ok=True)
    with OUTBOX.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": time.time(), "recipient": recipient, "body": body}) + "\n")
    return f"Message sent to {recipient}."
 
 
TOOLS = {"read_document": read_document, "send_message": send_message}