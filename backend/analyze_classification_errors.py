"""
Helpers for inspecting classifier errors and the classification report.
"""
from typing import List, Tuple, cast

import pandas as pd


SUMMARY_ROW_NAMES = {"accuracy", "macro avg", "weighted avg", "micro avg"}


def clean_report(report_df: pd.DataFrame) -> pd.DataFrame:
    """
    Strip aggregate rows (macro avg, weighted avg, accuracy, ...)
    from a sklearn classification_report DataFrame.
    """
    report_df = report_df.copy()
    mask = ~report_df.index.astype(str).isin(SUMMARY_ROW_NAMES)
    return report_df[mask]


def get_worst_classes(
    report_df: pd.DataFrame,
    top_n: int = 3,
    score_column: str = "f1-score",
) -> pd.DataFrame:
    """Return the `top_n` classes with the lowest score (ascending)."""
    cleaned = clean_report(report_df)
    return (
        cleaned.sort_values(by=score_column, ascending=True)
        .head(top_n)
    )


def get_best_classes(
    report_df: pd.DataFrame,
    top_n: int = 3,
    score_column: str = "f1-score",
) -> pd.DataFrame:
    """Return the `top_n` classes with the highest score (descending)."""
    cleaned = clean_report(report_df)
    return (
        cleaned.sort_values(by=score_column, ascending=False)
        .head(top_n)
    )


def build_top_confusions(
    matrix: pd.DataFrame,
    top_n: int = 10,
) -> pd.DataFrame:
    """
    From a confusion matrix, produce a DataFrame of off-diagonal
    (true_label, predicted_label, count) pairs sorted by count desc.
    """
    records: List[dict] = []
    for true_label, row in matrix.iterrows():
        for predicted_label, count in row.items():
            if true_label == predicted_label:
                continue
            if count == 0:
                continue
            records.append(
                {
                    "true_label": true_label,
                    "predicted_label": predicted_label,
                    "count": int(count),
                }
            )

    if not records:
        return pd.DataFrame(
            columns=["true_label", "predicted_label", "count"]
        )

    result = pd.DataFrame(records)
    return (
        result.sort_values(by="count", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )


def get_high_confidence_errors(
    df: pd.DataFrame,
    top_n: int = 10,
    label_column: str = "label_id",
    predicted_column: str = "predicted_label_id",
    confidence_column: str = "confidence",
) -> pd.DataFrame:
    """
    Return the `top_n` rows where label != predicted_label,
    ordered by descending confidence.
    """
    df = df.copy()
    mask = df[label_column].ne(df[predicted_column])
    errors = cast(pd.DataFrame, df.loc[mask, :])
    return (
        errors.copy()
        .sort_values(by=[confidence_column], ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )


def build_support_summary(
    report_df: pd.DataFrame,
    score_column: str = "f1-score",
) -> pd.DataFrame:
    """
    Append dataset-level columns (mean_f1, total_support) to the
    per-class classification report.
    """
    df = clean_report(report_df).copy()
    df["mean_f1"] = df[score_column].mean()
    df["total_support"] = df["support"].sum()
    return df
