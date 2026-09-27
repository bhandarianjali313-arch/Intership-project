"""
Word-based chunking for long legal documents.
"""
from typing import Dict, List


def create_word_chunks(
    text: str,
    chunk_size: int,
    overlap: int,
) -> List[Dict]:
    """
    Split text into overlapping chunks of words.

    Parameters
    ----------
    text : str
        The text to chunk.
    chunk_size : int
        Maximum number of words per chunk.
    overlap : int
        Number of words shared between consecutive chunks. Must be
        strictly less than chunk_size.

    Returns
    -------
    List[Dict]
        Each dict has keys: chunk_text, word_count, start_word, end_word.
    """
    if not text:
        return []

    if overlap >= chunk_size:
        raise ValueError(
            f"overlap ({overlap}) must be less than chunk_size ({chunk_size})"
        )

    words = text.split()
    if not words:
        return []

    step = chunk_size - overlap
    chunks: List[Dict] = []
    start = 0
    total = len(words)

    while start < total:
        end = min(start + chunk_size, total)
        chunk_words = words[start:end]
        chunks.append(
            {
                "chunk_text": " ".join(chunk_words),
                "word_count": len(chunk_words),
                "start_word": start,
                "end_word": end,
            }
        )
        if end >= total:
            break
        start += step

    return chunks
