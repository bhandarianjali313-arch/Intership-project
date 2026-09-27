"""
Thin wrapper around a spaCy NER pipeline for legal text.
"""
from functools import lru_cache
from typing import Dict, List, Optional

try:
    import spacy  # type: ignore[import-not-found]
except ImportError:
    spacy = None  # type: ignore[assignment]


@lru_cache(maxsize=1)
def load_ner_model(model_name: str = "en_core_web_sm"):
    """
    Load (and cache) the spaCy NER model.
    Downloads automatically on first use.
    """
    # If the top-level import failed, try to import spaCy here so static
    # type checkers don't assume `spacy` is None. If it's not available,
    # raise a clear ImportError.
    global spacy
    if spacy is None:
        try:
            import importlib

            spacy = importlib.import_module("spacy")
        except Exception as e:  # pragma: no cover - environment dependent
            raise ImportError("spaCy is not installed") from e

    try:
        return spacy.load(model_name)
    except OSError:
        spacy.cli.download(model_name)
        return spacy.load(model_name)


def extract_entities(
    text: str,
    nlp=None,
) -> List[Dict]:
    """
    Run the NER pipeline on `text` and return a list of dicts with
    keys: text, label, start_char, end_char.
    """
    if nlp is None:
        nlp = load_ner_model()

    if not text:
        return []

    doc = nlp(text)
    return [
        {
            "text": ent.text,
            "label": ent.label_,
            "start_char": ent.start_char,
            "end_char": ent.end_char,
        }
        for ent in doc.ents
    ]
