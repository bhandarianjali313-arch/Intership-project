import pandas as pd
import pytest

from ml.src.classification.dataset_utils import (
    add_label_ids,
    create_label_mapping,
    find_conflicting_labels,
    prepare_classification_rows,
    remove_exact_duplicates,
)


def build_test_dataframe():

    return pd.DataFrame(
        {
            "contract_id": [
                1,
                1,
                2,
                3,
            ],
            "clause_label": [
                "AUDIT_RIGHTS",
                "AUDIT_RIGHTS",
                "GOVERNING_LAW",
                "CAP_ON_LIABILITY",
            ],
            "cleaned_clause_text": [
                "Audit books.",
                "Audit books.",
                "Governed by California.",
                "",
            ],
            "has_answer": [
                True,
                True,
                True,
                True,
            ],
            "split": [
                "train",
                "train",
                "train",
                "train",
            ],
        }
    )


def test_prepare_removes_empty_text():

    df = build_test_dataframe()

    result = (
        prepare_classification_rows(
            df
        )
    )

    assert len(result) == 3


def test_prepare_removes_negative_rows():

    df = build_test_dataframe()

    df.loc[
        0,
        "has_answer"
    ] = False

    result = (
        prepare_classification_rows(
            df
        )
    )

    assert len(result) == 2


def test_exact_duplicate_removal():

    df = build_test_dataframe()

    prepared = (
        prepare_classification_rows(
            df
        )
    )

    result, removed = (
        remove_exact_duplicates(
            prepared
        )
    )

    assert len(result) == 2

    assert removed == 1


def test_label_mapping_is_deterministic():

    labels = [
        "GOVERNING_LAW",
        "AUDIT_RIGHTS",
        "CAP_ON_LIABILITY",
    ]

    label_to_id, _ = (
        create_label_mapping(
            labels
        )
    )

    assert (
        label_to_id[
            "AUDIT_RIGHTS"
        ]
        == 0
    )


def test_label_ids_added():

    df = pd.DataFrame(
        {
            "clause_label": [
                "A",
                "B",
            ]
        }
    )

    result = add_label_ids(
        df,
        {
            "A": 0,
            "B": 1,
        },
    )

    assert result[
        "label_id"
    ].tolist() == [
        0,
        1,
    ]


def test_unknown_label_raises():

    df = pd.DataFrame(
        {
            "clause_label": [
                "UNKNOWN"
            ]
        }
    )

    with pytest.raises(
        ValueError
    ):

        add_label_ids(
            df,
            {
                "A": 0
            },
        )


def test_conflicting_labels_detected():

    df = pd.DataFrame(
        {
            "cleaned_clause_text": [
                "Same legal text",
                "Same legal text",
                "Different text",
            ],
            "clause_label": [
                "A",
                "B",
                "A",
            ],
        }
    )

    conflicts = (
        find_conflicting_labels(
            df
        )
    )

    assert len(conflicts) == 2