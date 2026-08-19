from __future__ import annotations

import html
import re
import unicodedata


def normalize_unicode(text: str) -> str:
    if not isinstance(text, str):
        return ""

    return unicodedata.normalize("NFKC", text)


def decode_html_entities(text: str) -> str:
    if not text:
        return ""

    return html.unescape(text)


def remove_control_characters(text: str) -> str:
    if not text:
        return ""

    return "".join(
        character
        for character in text
        if (
            character in "\n\t"
            or unicodedata.category(character)[0] != "C"
        )
    )


def normalize_whitespace(text: str) -> str:
    if not text:
        return ""

    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


def clean_legal_text(text: str) -> str:
    if not isinstance(text, str):
        return ""

    text = normalize_unicode(text)
    text = decode_html_entities(text)
    text = remove_control_characters(text)
    text = normalize_whitespace(text)

    return text


def count_words(text: str) -> int:
    if not text:
        return 0

    return len(text.split())