import re, os
from pathlib import Path
from typing import List, Dict, Any, Tuple

def extract_text_from_file(file_path: Path, filename: str) -> Tuple[str, List[Dict[str, Any]], int]:
    ext = file_path.suffix.lower()
    full_text = ""
    if ext in [".txt", ".md"]:
        full_text = file_path.read_text(encoding="utf-8", errors="ignore")
    elif ext == ".docx":
        try:
            import docx
            doc = docx.Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            full_text = "\n\n".join(paragraphs)
        except Exception:
            full_text = file_path.read_text(encoding="utf-8", errors="ignore")
    elif ext == ".pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            pages_text = []
            for i, page in enumerate(reader.pages):
                txt = page.extract_text() or ""
                pages_text.append(f"--- PAGE {i+1} ---\n" + txt)
            full_text = "\n\n".join(pages_text)
        except Exception:
            full_text = file_path.read_text(encoding="utf-8", errors="ignore")
    else:
        full_text = file_path.read_text(encoding="utf-8", errors="ignore")

    sections, total_pages = segment_contract_text(full_text)
    return full_text, sections, total_pages

def segment_contract_text(text: str) -> Tuple[List[Dict[str, Any]], int]:
    lines = text.split("\n")
    sections = []
    current_sec_num = "Preamble"
    current_sec_title = "Preamble & Recitals"
    current_sec_text = []
    current_page = 1
    words_count = 0
    WORDS_PER_PAGE = 300

    heading_regex = re.compile(
        r"^(\d+(\.\d+)*|[A-Z]+|\bSection\s+\d+(\.\d+)*|\bArticle\s+[IVXLCDM\d]+)[\.:\s\-]+([A-Z0-9\s,&/()'\"]{3,80})$",
        re.IGNORECASE
    )

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        page_match = re.match(r"^---\s*PAGE\s*(\d+)\s*---", stripped, re.IGNORECASE)
        if page_match:
            current_page = int(page_match.group(1))
            continue

        words = stripped.split()
        words_count += len(words)
        calc_page = max(current_page, (words_count // WORDS_PER_PAGE) + 1)

        h_match = heading_regex.match(stripped)
        is_all_caps_short = (stripped.isupper() and 4 < len(stripped) < 60 and not stripped.endswith("."))

        if (h_match or is_all_caps_short) and len(current_sec_text) > 0:
            sec_body = "\n".join(current_sec_text).strip()
            if sec_body:
                sections.append({
                    "section_number": current_sec_num,
                    "title": current_sec_title,
                    "text": sec_body,
                    "page_number": calc_page
                })
            current_sec_text = [stripped]
            if h_match:
                current_sec_num = h_match.group(1)
                current_sec_title = h_match.group(4).strip() if len(h_match.groups()) >= 4 and h_match.group(4) else stripped
            else:
                current_sec_num = f"Sec {len(sections)+1}"
                current_sec_title = stripped
        else:
            current_sec_text.append(stripped)

    if current_sec_text:
        sec_body = "\n".join(current_sec_text).strip()
        if sec_body:
            sections.append({
                "section_number": current_sec_num,
                "title": current_sec_title,
                "text": sec_body,
                "page_number": max(1, (words_count // WORDS_PER_PAGE) + 1)
            })

    total_pages = max(1, (words_count // WORDS_PER_PAGE) + 1)
    if not sections:
        sections = [{
            "section_number": "1",
            "title": "Entire Agreement",
            "text": text,
            "page_number": 1
        }]

    return sections, total_pages
