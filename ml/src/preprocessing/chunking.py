from __future__ import annotations


def split_words(text: str) -> list[str]:
    """
    Convert text into whitespace-separated words.
    """

    if not isinstance(text, str):
        return []

    return text.split()


def create_word_chunks(
    text: str,
    chunk_size: int = 350,
    overlap: int = 50,
) -> list[dict]:
    """
    Split text into overlapping word-based chunks.

    Returns a list containing:
    - chunk_id
    - chunk_text
    - word_start
    - word_end
    - word_count
    """

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0"
        )

    if overlap < 0:
        raise ValueError(
            "overlap cannot be negative"
        )

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    words = split_words(text)

    if not words:
        return []

    chunks = []

    step = chunk_size - overlap

    chunk_id = 0

    for start in range(
        0,
        len(words),
        step,
    ):

        end = min(
            start + chunk_size,
            len(words),
        )

        chunk_words = words[
            start:end
        ]

        chunk_text = " ".join(
            chunk_words
        )

        chunks.append(
            {
                "chunk_id": chunk_id,
                "chunk_text": chunk_text,
                "word_start": start,
                "word_end": end,
                "word_count": len(
                    chunk_words
                ),
            }
        )

        chunk_id += 1

        if end == len(words):
            break

    return chunks