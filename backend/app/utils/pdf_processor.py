"""PDF text extraction utilities."""
import fitz  # PyMuPDF
from typing import List, Tuple


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from PDF file.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text as string
    """
    doc = fitz.open(pdf_path)
    text = ""
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text += page.get_text()
    
    doc.close()
    return text


def chunk_into_clauses(text: str) -> List[Tuple[str, str, int, int]]:
    """
    Split contract text into clauses based on patterns.
    
    Uses rule-based approach:
    - Numbered sections (1., 1.1, a., etc.)
    - Headings (ALL CAPS lines)
    - Double line breaks
    
    Args:
        text: Full contract text
        
    Returns:
        List of tuples: (clause_number, clause_text, start_pos, end_pos)
    """
    import re
    
    clauses = []
    
    # Pattern for numbered clauses: "1.", "1.1", "a)", "(a)", "Article 1"
    number_pattern = r'^(?:\d+\.(?:\d+)?|\([a-z]\)|[a-z]\)|Article\s+\d+|Section\s+\d+)'
    
    # Split by double newlines first
    sections = re.split(r'\n\s*\n', text)
    
    current_pos = 0
    clause_num = 1
    
    for section in sections:
        section = section.strip()
        if not section or len(section) < 20:  # Skip very short sections
            current_pos += len(section) + 2
            continue
        
        # Check if section starts with a number pattern
        lines = section.split('\n')
        first_line = lines[0].strip()
        
        match = re.match(number_pattern, first_line, re.IGNORECASE)
        
        if match:
            clause_number = match.group(0).strip()
        else:
            # Check if it's a heading (short, all caps or title case)
            if len(first_line) < 100 and (first_line.isupper() or first_line.istitle()):
                clause_number = first_line[:50]
            else:
                clause_number = f"Clause {clause_num}"
        
        start_pos = text.find(section, current_pos)
        end_pos = start_pos + len(section)
        
        clauses.append((clause_number, section, start_pos, end_pos))
        clause_num += 1
        current_pos = end_pos
    
    # Fallback for handbook/policy PDFs where text may not contain double line breaks.
    # Split on heading-like lines such as "1.1 A Welcome Policy".
    if len(clauses) <= 2:
        heading_pattern = re.compile(
            r'^(?:\d+\.\d+\s+.+|\d+\.\d+\.\d+\s+.+|\d+\.0\s+.+|Article\s+\d+\b.*|Section\s+\d+\b.*)$',
            re.IGNORECASE
        )

        lines = [ln.strip() for ln in text.split('\n')]
        rebuilt = []
        current_heading = None
        current_lines = []
        cursor = 0

        def flush_current():
            nonlocal cursor, rebuilt, current_heading, current_lines
            if not current_lines:
                return
            chunk_text = '\n'.join(current_lines).strip()
            if len(chunk_text) < 40:
                current_lines = []
                return
            start = text.find(chunk_text, cursor)
            if start == -1:
                start = cursor
            end = start + len(chunk_text)
            label = current_heading or f"Clause {len(rebuilt) + 1}"
            rebuilt.append((label[:80], chunk_text, start, end))
            cursor = end
            current_lines = []

        for ln in lines:
            if not ln:
                continue

            if heading_pattern.match(ln):
                flush_current()
                current_heading = ln
                current_lines = [ln]
            else:
                if not current_lines:
                    current_heading = None
                current_lines.append(ln)

        flush_current()

        if len(rebuilt) >= 3:
            clauses = rebuilt

    # If still no useful clauses found, treat whole text as one clause
    if not clauses:
        clauses.append(("Document", text, 0, len(text)))
    
    return clauses
