from __future__ import annotations

from typing import Iterable

import pandas as pd


REQUIRED_COLUMNS = {
    "contract_id",
    "clause_label",
    "cleaned_clause_text",
    "has_answer",
    "split",
}


def validate_input_columns(
    df: pd.DataFrame,
) -> None:
    """
    Ensure the expected columns exist.
    """

    missing = REQUIRED_COLUMNS - set(
        df.columns
    )

    if missing:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(sorted(missing))
        )


def prepare_classification_rows(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convert processed CUAD records into examples for
    multiclass clause classification.

    Only positive answer spans are suitable here.
    """

    validate_input_columns(df)

    working = df.copy()

    # Keep only actual clause spans.
    working = working[
        working["has_answer"] == True
    ].copy()

    # Defensive cleanup.
    working["cleaned_clause_text"] = (
        working["cleaned_clause_text"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    working["clause_label"] = (
        working["clause_label"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # Empty texts/labels cannot be used for training.
    working = working[
        (
            working["cleaned_clause_text"] != ""
        )
        &
        (
            working["clause_label"] != ""
        )
    ].copy()

    return working


def remove_exact_duplicates(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, int]:
    """
    Remove exact duplicate text/label examples.

    We intentionally include contract_id in the key so
    identical wording from different contracts is not
    automatically discarded.
    """

    before = len(df)

    result = df.drop_duplicates(
        subset=[
            "contract_id",
            "clause_label",
            "cleaned_clause_text",
        ],
        keep="first",
    ).copy()

    removed = before - len(result)

    return result, removed


def find_conflicting_labels(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Find text strings associated with multiple labels.

    These examples are not automatically deleted because
    legal text may legitimately express multiple concepts.
    """

    label_counts = (
        df.groupby(
            "cleaned_clause_text"
        )["clause_label"]
        .nunique()
    )

    conflicting_texts = set(
        label_counts[
            label_counts > 1
        ].index
    )

    if not conflicting_texts:
        return df.iloc[0:0].copy()

    return (
        df[
            df["cleaned_clause_text"]
            .isin(conflicting_texts)
        ]
        .sort_values(
            [
                "cleaned_clause_text",
                "clause_label",
            ]
        )
        .copy()
    )


def create_label_mapping(
    labels: Iterable[str],
) -> tuple[
    dict[str, int],
    dict[int, str],
]:
    """
    Create deterministic label <-> integer mappings.
    """

    unique_labels = sorted(
        set(labels)
    )

    label_to_id = {
        label: index
        for index, label
        in enumerate(unique_labels)
    }

    id_to_label = {
        index: label
        for label, index
        in label_to_id.items()
    }

    return (
        label_to_id,
        id_to_label,
    )


def add_label_ids(
    df: pd.DataFrame,
    label_to_id: dict[str, int],
) -> pd.DataFrame:
    """
    Add integer class IDs.
    """

    result = df.copy()

    result["label_id"] = (
        result["clause_label"]
        .map(label_to_id)
    )

    if result["label_id"].isna().any():
        raise ValueError(
            "Some clause labels were not found "
            "in label_to_id."
        )

    result["label_id"] = (
        result["label_id"]
        .astype(int)
    )

    return result