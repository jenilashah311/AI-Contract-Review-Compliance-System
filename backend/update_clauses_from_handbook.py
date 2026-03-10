import json
import re
from pathlib import Path
from urllib import request

import sys

WORKSPACE = Path("/Users/jenilshah/Documents/AI Contract Review & Compliance System")
BACKEND_DIR = WORKSPACE / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.utils.pdf_processor import extract_text_from_pdf, chunk_into_clauses  # noqa: E402

BASE_URL = "http://localhost:8000"
PDF_PATH = BACKEND_DIR / "uploads" / "DH_Handbook.pdf"
MAX_CLAUSES = 18


def http_json(method: str, url: str, payload=None):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = request.Request(url, data=data, headers=headers, method=method)
    with request.urlopen(req, timeout=120) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body) if body else None


def category_for(text: str) -> str:
    t = text.lower()
    rules = [
        ("Attendance", ["attendance", "absence", "late", "punctual", "work hours"]),
        ("Leave", ["leave", "vacation", "sick", "holiday", "pto"]),
        ("Compensation", ["salary", "pay", "compensation", "wage", "overtime"]),
        ("Benefits", ["benefit", "insurance", "medical", "dental", "retirement"]),
        ("Conduct", ["conduct", "discipline", "harassment", "behavior", "ethics"]),
        ("Confidentiality", ["confidential", "privacy", "data", "information security"]),
        ("IT Policy", ["computer", "system", "email", "internet", "device"]),
        ("Safety", ["safety", "incident", "emergency", "injury", "hazard"]),
        ("Grievance", ["complaint", "grievance", "report", "investigation"]),
        ("Employment", ["employment", "termination", "probation", "notice", "resignation"]),
    ]
    for cat, keys in rules:
        if any(k in t for k in keys):
            return cat
    return "General Policy"


def make_title(clause_num: str, text: str, idx: int) -> str:
    first_line = text.splitlines()[0].strip() if text.splitlines() else ""
    first_line = re.sub(r"\s+", " ", first_line)

    if 6 <= len(first_line) <= 80:
        base = first_line
    else:
        words = re.findall(r"[A-Za-z0-9']+", text)
        base = " ".join(words[:8]).strip() or f"Policy Clause {idx}"

    base = re.sub(r"^[\W_]+|[\W_]+$", "", base)
    if clause_num and not base.lower().startswith(clause_num.lower()):
        return f"{clause_num} - {base}"[:120]
    return base[:120]


def normalize_text(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    return s


def build_clauses_from_pdf(pdf_path: Path):
    text = extract_text_from_pdf(str(pdf_path))
    chunks = chunk_into_clauses(text)

    clauses = []
    seen_titles = set()

    for idx, (clause_num, clause_text, _, _) in enumerate(chunks, start=1):
        cleaned = normalize_text(clause_text)
        if len(cleaned) < 80:
            continue

        title = make_title(clause_num, clause_text, idx)
        title_key = title.lower()
        if title_key in seen_titles:
            continue

        seen_titles.add(title_key)
        clauses.append(
            {
                "category": category_for(cleaned),
                "title": title,
                "text": cleaned[:1800],
            }
        )

        if len(clauses) >= MAX_CLAUSES:
            break

    return clauses


def main():
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"PDF not found: {PDF_PATH}")

    new_clauses = build_clauses_from_pdf(PDF_PATH)
    if not new_clauses:
        raise RuntimeError("No suitable clauses extracted from PDF")

    existing = http_json("GET", f"{BASE_URL}/clauses/")
    for c in existing:
        http_json("DELETE", f"{BASE_URL}/clauses/{c['id']}")

    for c in new_clauses:
        http_json("POST", f"{BASE_URL}/clauses/", c)

    final = http_json("GET", f"{BASE_URL}/clauses/")

    print(f"Deleted {len(existing)} clauses")
    print(f"Created {len(new_clauses)} clauses from handbook")
    print(f"Final total in DB: {len(final)}")
    print("Sample titles:")
    for c in final[:8]:
        print(f"- [{c['category']}] {c['title']}")


if __name__ == "__main__":
    main()
