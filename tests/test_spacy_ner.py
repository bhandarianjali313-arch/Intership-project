from ml.src.ner.spacy_ner import (
    extract_entities,
    load_ner_model,
)


def test_empty_text_returns_empty():

    nlp = load_ner_model()

    result = extract_entities(
        "",
        nlp=nlp,
    )

    assert result == []


def test_entity_output_structure():

    nlp = load_ner_model()

    text = (
        "Microsoft signed the agreement "
        "on January 10, 2026."
    )

    entities = extract_entities(
        text,
        nlp=nlp,
    )

    for entity in entities:

        assert "text" in entity
        assert "label" in entity
        assert "start_char" in entity
        assert "end_char" in entity


def test_entity_offsets_are_valid():

    nlp = load_ner_model()

    text = (
        "Microsoft Corporation paid "
        "$5 million on January 10, 2026."
    )

    entities = extract_entities(
        text,
        nlp=nlp,
    )

    for entity in entities:

        extracted = text[
            entity["start_char"]:
            entity["end_char"]
        ]

        assert extracted == (
            entity["text"]
        )