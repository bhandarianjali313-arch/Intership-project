import html
import re
from typing import Optional


_WHITESPACE_PATTERN = re.compile(r"\s+")


def clean_legal_text(text: Optional[str]) -> str:
    """
    Clean legal text by decoding HTML entities and normalizing whitespace
    while preserving legal symbols ($, %, commas in numbers, etc.).
    """
    if not text:
        return ""

    # Decode HTML entities (e.g., &amp; -> &)
    text = html.unescape(text)

    # Collapse all whitespace (spaces, tabs, newlines) into a single space
    text = _WHITESPACE_PATTERN.sub(" ", text).strip()

    return text


def count_words(text: Optional[str]) -> int:
    """Return the number of whitespace-separated tokens in text."""
    if not text:
        return 0
    return len(text.split())
