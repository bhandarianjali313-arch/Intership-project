from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def load_json(path: Path) -> dict:
    """
    Load a JSON file safely.
    """

    if not path.exists():
        raise FileNotFoundError(
            f"Required file not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def extract_metric(
    metrics: dict,
    metric_name: str,
) -> float | None:
    """
    Support metric names saved with either
    eval_ or test_ prefixes.
    """

    candidates = [
        metric_name,
        f"eval_{metric_name}",
        f"test_{metric_name}",
    ]

    for key in candidates:

        if key in metrics:
            return float(
                metrics[key]
            )

    return None


def build_model_row(
    model_name: str,
    metrics: dict,
    training_strategy: str,
    training_seconds: float | None = None,
    max_length: int | None = None,
    epochs: float | None = None,
) -> dict:
    """
    Convert one experiment into a common comparison row.
    """

    return {
        "model": model_name,
        "training_strategy": training_strategy,

        "accuracy": extract_metric(
            metrics,
            "accuracy",
        ),

        "macro_precision": extract_metric(
            metrics,
            "macro_precision",
        ),

        "macro_recall": extract_metric(
            metrics,
            "macro_recall",
        ),

        "macro_f1": extract_metric(
            metrics,
            "macro_f1",
        ),

        "weighted_f1": extract_metric(
            metrics,
            "weighted_f1",
        ),

        "training_seconds": training_seconds,

        "max_length": max_length,

        "epochs": epochs,
    }


def select_best_model(
    comparison_df: pd.DataFrame,
) -> dict:
    """
    Select the preferred model primarily using Macro-F1.

    Macro-F1 is prioritized because CUAD is strongly
    imbalanced and minority legal categories matter.
    """

    if comparison_df.empty:
        raise ValueError(
            "Model comparison dataframe is empty."
        )

    usable = comparison_df[
        comparison_df["macro_f1"].notna()
    ].copy()

    if usable.empty:
        raise ValueError(
            "No model contains Macro-F1."
        )

    best_row = usable.sort_values(
        [
            "macro_f1",
            "weighted_f1",
            "accuracy",
        ],
        ascending=False,
    ).iloc[0]

    return {
        "selected_model": best_row["model"],
        "selection_metric": "macro_f1",
        "macro_f1": float(
            best_row["macro_f1"]
        ),
        "weighted_f1": (
            float(best_row["weighted_f1"])
            if pd.notna(
                best_row["weighted_f1"]
            )
            else None
        ),
        "accuracy": (
            float(best_row["accuracy"])
            if pd.notna(
                best_row["accuracy"]
            )
            else None
        ),
    }


def clean_classification_report(
    report: pd.DataFrame,
) -> pd.DataFrame:
    """
    Keep only real class rows.
    """

    df = report.copy()

    df["support"] = pd.to_numeric(
        df["support"],
        errors="coerce",
    )

    df = df[
        df["support"].notna()
    ].copy()

    df = df[
        ~df.index.isin(
            [
                "accuracy",
                "macro avg",
                "weighted avg",
            ]
        )
    ]

    return df


def build_minority_comparison(
    reports: dict[str, pd.DataFrame],
    support_threshold: int = 50,
) -> pd.DataFrame:
    """
    Compare model performance on minority classes.

    Minority status is determined using the baseline
    report support so the same classes are compared.
    """

    if not reports:
        return pd.DataFrame()

    first_name = next(
        iter(reports)
    )

    reference = clean_classification_report(
        reports[first_name]
    )

    minority_labels = set(
        reference[
            reference["support"]
            <= support_threshold
        ].index
    )

    rows = []

    for model_name, report in reports.items():

        cleaned = (
            clean_classification_report(
                report
            )
        )

        available = cleaned[
            cleaned.index.isin(
                minority_labels
            )
        ]

        for clause_label, row in (
            available.iterrows()
        ):

            rows.append(
                {
                    "model": model_name,
                    "clause_label": clause_label,
                    "precision": float(
                        row["precision"]
                    ),
                    "recall": float(
                        row["recall"]
                    ),
                    "f1_score": float(
                        row["f1-score"]
                    ),
                    "support": int(
                        row["support"]
                    ),
                }
            )

    return pd.DataFrame(
        rows
    )