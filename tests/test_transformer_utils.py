import numpy as np
import pandas as pd
import pytest

from ml.src.classification.transformer_utils import (
    compute_classification_metrics,
    prepare_transformer_dataframe,
    validate_transformer_dataframe,
)


def build_dataframe():

    return pd.DataFrame(
        {
            "contract_id": [
                1,
                2,
            ],
            "cleaned_clause_text": [
                "Agreement governed by California.",
                "Licensee may inspect records.",
            ],
            "clause_label": [
                "GOVERNING_LAW",
                "AUDIT_RIGHTS",
            ],
            "label_id": [
                0,
                1,
            ],
        }
    )


def test_valid_dataframe():

    df = build_dataframe()

    validate_transformer_dataframe(
        df
    )


def test_missing_column_raises():

    df = (
        build_dataframe()
        .drop(
            columns=[
                "label_id"
            ]
        )
    )

    with pytest.raises(
        ValueError
    ):

        validate_transformer_dataframe(
            df
        )


def test_empty_text_removed():

    df = build_dataframe()

    df.loc[
        0,
        "cleaned_clause_text"
    ] = ""

    result = (
        prepare_transformer_dataframe(
            df
        )
    )

    assert len(result) == 1


def test_whitespace_text_removed():

    df = build_dataframe()

    df.loc[
        0,
        "cleaned_clause_text"
    ] = "     "

    result = (
        prepare_transformer_dataframe(
            df
        )
    )

    assert len(result) == 1


def test_label_ids_are_integer():

    df = build_dataframe()

    result = (
        prepare_transformer_dataframe(
            df
        )
    )

    assert (
        result[
            "label_id"
        ].dtype.kind
        in "iu"
    )


def test_metrics_perfect_prediction():

    logits = np.array(
        [
            [
                10.0,
                0.0,
            ],
            [
                0.0,
                10.0,
            ],
        ]
    )

    labels = np.array(
        [
            0,
            1,
        ]
    )

    metrics = (
        compute_classification_metrics(
            logits,
            labels,
        )
    )

    assert (
        metrics[
            "accuracy"
        ]
        == 1.0
    )

    assert (
        metrics[
            "macro_f1"
        ]
        == 1.0
    )

    assert (
        metrics[
            "weighted_f1"
        ]
        == 1.0
    )


def test_metrics_range():

    logits = np.array(
        [
            [
                0.2,
                0.8,
            ],
            [
                0.7,
                0.3,
            ],
            [
                0.6,
                0.4,
            ],
        ]
    )

    labels = np.array(
        [
            1,
            1,
            0,
        ]
    )

    metrics = (
        compute_classification_metrics(
            logits,
            labels,
        )
    )

    for value in (
        metrics.values()
    ):

        assert (
            0.0
            <= value
            <= 1.0
        )