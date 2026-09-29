import pytest

from ml.src.classification.labels import (
    CLAUSE_LABELS,
    ID_TO_LABEL,
    LABEL_TO_ID,
    decode_clause_label,
    encode_clause_label,
)


def test_total_clause_labels():

    assert len(
        CLAUSE_LABELS
    ) == 41


def test_id_to_label_mapping():

    assert (
        ID_TO_LABEL[13]
        == "GOVERNING_LAW"
    )

    assert (
        ID_TO_LABEL[22]
        == "NON_COMPETE"
    )

    assert (
        ID_TO_LABEL[35]
        == "TERMINATION_FOR_CONVENIENCE"
    )


def test_decode_numeric_integer():

    assert (
        decode_clause_label(
            22
        )
        == "NON_COMPETE"
    )


def test_decode_numeric_string():

    assert (
        decode_clause_label(
            "13"
        )
        == "GOVERNING_LAW"
    )


def test_decode_existing_text_label():

    assert (
        decode_clause_label(
            "governing_law"
        )
        == "GOVERNING_LAW"
    )


def test_encode_clause_label():

    assert (
        encode_clause_label(
            "NON_COMPETE"
        )
        == 22
    )


def test_reverse_mapping_is_consistent():

    for class_id, label in (
        ID_TO_LABEL.items()
    ):

        assert (
            LABEL_TO_ID[
                label
            ]
            == class_id
        )


def test_unknown_numeric_id_rejected():

    with pytest.raises(
        ValueError
    ):

        decode_clause_label(
            999
        )


def test_none_label_rejected():

    with pytest.raises(
        TypeError
    ):

        decode_clause_label(
            None
        )