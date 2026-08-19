from __future__ import annotations

from typing import Any

import spacy


DEFAULT_MODEL = "en_core_web_sm"


def load_ner_model(
    model_name: str = DEFAULT_MODEL,
):
    """
    Load a spaCy NER model.
    """

    return spacy.load(model_name)


def extract_entities(
    text: str,
    nlp=None,
) -> list[dict[str, Any]]:
    """
    Extract named entities from text.

    Returns:
    - entity text
    - entity label
    - start character
    - end character
    """

    if not isinstance(text, str):
        return []

    if not text.strip():
        return []

    if nlp is None:
        nlp = load_ner_model()

    doc = nlp(text)

    entities = []

    for entity in doc.ents:

        entities.append(
            {
                "text": entity.text,
                "label": entity.label_,
                "start_char": entity.start_char,
                "end_char": entity.end_char,
            }
        )

    return entities 