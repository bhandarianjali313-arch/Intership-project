"""
Dataset preparation helpers for clause classification.
"""
from typing import Dict, List, Tuple, cast

import pandas as pd


def prepare_classification_rows(
    df: pd.DataFrame,
    text_column: str = "cleaned_clause_text",
    answer_column: str = "has_answer",
) -> pd.DataFrame:
    """Drop rows with empty clause text or with has_answer == False."""
    df = df.copy()

    # Keep only non-null, non-empty text. Convert the mask to a NumPy boolean
    # array for `loc` so pandas' overloads resolve to a DataFrame result.
    text_mask: pd.Series = df[text_column].notna() & (df[text_column].str.strip() != "")
    filtered_df: pd.DataFrame = cast(
        pd.DataFrame,
        df.loc[text_mask.to_numpy(dtype=bool), :],
    ).copy()
    df = filtered_df.reset_index(drop=True)

    # Keep only positive (has_answer == True) rows. Convert the mask to a
    # NumPy boolean array so pandas' overloads resolve to a DataFrame result.
    positive_mask: pd.Series = df[answer_column].eq(True)
    positive_df: pd.DataFrame = cast(
        pd.DataFrame,
        df.loc[positive_mask.to_numpy(dtype=bool), :],
    ).copy()
    df = positive_df.reset_index(drop=True)

    return df.reset_index(drop=True)


def remove_exact_duplicates(
    df: pd.DataFrame,
    text_column: str = "cleaned_clause_text",
    label_column: str = "clause_label",
) -> Tuple[pd.DataFrame, int]:
    """
    Drop rows whose (text, label) pair already exists.
    Returns the cleaned DataFrame and the number of rows removed.
    """
    df = df.copy()
    before = len(df)
    df = df.drop_duplicates(
        subset=[text_column, label_column],
        keep="first",
    ).reset_index(drop=True)
    removed = before - len(df)
    return df, removed


def create_label_mapping(
    labels: List[str],
) -> Tuple[Dict[str, int], Dict[int, str]]:
    """
    Build deterministic label -> id and id -> label maps.
    Sorted alphabetically so the mapping is stable across runs.
    """
    sorted_labels = sorted(set(labels))
    label_to_id = {label: idx for idx, label in enumerate(sorted_labels)}
    id_to_label = {idx: label for label, idx in label_to_id.items()}
    return label_to_id, id_to_label


def add_label_ids(
    df: pd.DataFrame,
    label_to_id: Dict[str, int],
    label_column: str = "clause_label",
    id_column: str = "label_id",
) -> pd.DataFrame:
    """Map each row's clause_label through label_to_id; raise on unknowns."""
    df = df.copy()

    unknown = set(df[label_column].unique()) - set(label_to_id.keys())
    if unknown:
        raise ValueError(f"Unknown labels found in data: {sorted(unknown)}")

    df[id_column] = df[label_column].map(label_to_id)
    return df


def find_conflicting_labels(
    df: pd.DataFrame,
    text_column: str = "cleaned_clause_text",
    label_column: str = "clause_label",
) -> List[Tuple[str, str, str]]:
    """
    Return a list of (text, label, reason) tuples for any clause text
    that appears with more than one distinct label.
    """
    label_counts = df.groupby(text_column)[label_column].nunique()
    conflicting_texts = [
        text for text, count in label_counts.items() if count > 1
    ]

    conflicts: List[Tuple[str, str, str]] = []
    for text in conflicting_texts:
        text_value = str(text)
        text_labels = df.loc[df[text_column].eq(text), label_column]
        labels = pd.Series(text_labels).drop_duplicates()
        for label in labels.tolist():
            conflicts.append((text_value, str(label), "conflict"))
    return conflicts
