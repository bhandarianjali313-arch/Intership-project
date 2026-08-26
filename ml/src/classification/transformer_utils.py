from __future__ import annotations

from typing import Any

import numpy as np

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)


TEXT_COLUMN = "cleaned_clause_text"
LABEL_COLUMN = "label_id"


def validate_transformer_dataframe(
    dataframe,
) -> None:
    """
    Validate columns required for transformer training.
    """

    required_columns = {
        TEXT_COLUMN,
        LABEL_COLUMN,
        "clause_label",
        "contract_id",
    }

    missing_columns = (
        required_columns
        - set(dataframe.columns)
    )

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(
                sorted(missing_columns)
            )
        )


def prepare_transformer_dataframe(
    dataframe,
):
    """
    Clean and prepare classification data.
    """

    validate_transformer_dataframe(
        dataframe
    )

    df = dataframe.copy()

    df[TEXT_COLUMN] = (
        df[TEXT_COLUMN]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # Remove empty clauses.
    df = df[
        df[TEXT_COLUMN] != ""
    ].copy()

    df[LABEL_COLUMN] = (
        df[LABEL_COLUMN]
        .astype(int)
    )

    return df


def tokenize_batch(
    examples: dict[str, Any],
    tokenizer,
    max_length: int = 256,
) -> dict[str, Any]:
    """
    Tokenize legal clause text.

    Dynamic padding is performed later by
    DataCollatorWithPadding.
    """

    return tokenizer(
        examples[TEXT_COLUMN],
        truncation=True,
        max_length=max_length,
    )


def compute_classification_metrics(
    predictions,
    labels,
) -> dict[str, float]:
    """
    Calculate multiclass classification metrics.

    Macro F1 is especially important because the
    CUAD classes are highly imbalanced.
    """

    predicted_labels = np.argmax(
        predictions,
        axis=-1,
    )

    return {
        "accuracy": float(
            accuracy_score(
                labels,
                predicted_labels,
            )
        ),
        "macro_precision": float(
            precision_score(
                labels,
                predicted_labels,
                average="macro",
                zero_division=0,
            )
        ),
        "macro_recall": float(
            recall_score(
                labels,
                predicted_labels,
                average="macro",
                zero_division=0,
            )
        ),
        "macro_f1": float(
            f1_score(
                labels,
                predicted_labels,
                average="macro",
                zero_division=0,
            )
        ),
        "weighted_f1": float(
            f1_score(
                labels,
                predicted_labels,
                average="weighted",
                zero_division=0,
            )
        ),
    }


def trainer_metrics(
    evaluation_prediction,
) -> dict[str, float]:
    """
    Hugging Face Trainer metric adapter.
    """

    predictions = (
        evaluation_prediction.predictions
    )

    labels = (
        evaluation_prediction.label_ids
    )

    return compute_classification_metrics(
        predictions,
        labels,
    )