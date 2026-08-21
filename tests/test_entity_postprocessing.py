from ml.src.ner.entity_postprocessing import (
    is_legal_role,
    normalize_entity_text,
    postprocess_entity,
    postprocess_entities,
)


def test_normalize_entity_text():

    result = normalize_entity_text(
        "  Microsoft   Corporation "
    )

    assert result == (
        "Microsoft Corporation"
    )


def test_licensee_becomes_legal_role():

    entity = {
        "text": "Licensee",
        "label": "PERSON",
        "start_char": 0,
        "end_char": 8,
    }

    result = postprocess_entity(
        entity
    )

    assert result is not None

    assert (
        result[
            "normalized_label"
        ]
        == "LEGAL_ROLE"
    )


def test_agreement_false_positive_removed():

    entity = {
        "text": "Agreement",
        "label": "PRODUCT",
        "start_char": 10,
        "end_char": 19,
    }

    result = postprocess_entity(
        entity
    )

    assert result is None


def test_org_is_preserved():

    entity = {
        "text": "Microsoft",
        "label": "ORG",
        "start_char": 0,
        "end_char": 9,
    }

    result = postprocess_entity(
        entity
    )

    assert result is not None

    assert (
        result[
            "normalized_label"
        ]
        == "ORG"
    )


def test_unwanted_label_removed():

    entity = {
        "text": "some title",
        "label": "WORK_OF_ART",
        "start_char": 0,
        "end_char": 10,
    }

    result = postprocess_entity(
        entity
    )

    assert result is None


def test_multiple_entities():

    entities = [
        {
            "text": "Licensee",
            "label": "PERSON",
            "start_char": 0,
            "end_char": 8,
        },
        {
            "text": "Agreement",
            "label": "PRODUCT",
            "start_char": 10,
            "end_char": 19,
        },
        {
            "text": "$5 million",
            "label": "MONEY",
            "start_char": 20,
            "end_char": 30,
        },
    ]

    result = postprocess_entities(
        entities
    )

    assert len(result) == 2


def test_legal_role_detection():

    assert is_legal_role(
        "Licensor"
    )

    assert is_legal_role(
        "Seller"
    )

    assert not is_legal_role(
        "Microsoft"
    )