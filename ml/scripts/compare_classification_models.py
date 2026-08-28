from pathlib import Path
import json

import pandas as pd

from ml.src.classification.model_comparison import (
    build_minority_comparison,
    build_model_row,
    load_json,
    select_best_model,
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)


# =============================================================================
# EXPERIMENT DIRECTORIES
# =============================================================================

BASELINE_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "classification"
    / "baseline"
)

TRANSFORMER_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "classification"
    / "transformer"
)

WEIGHTED_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "classification"
    / "transformer_weighted"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "classification"
    / "comparison"
)


def print_header(
    title: str,
) -> None:

    print(
        "\n"
        + "=" * 80
    )

    print(title)

    print(
        "=" * 80
    )


def load_optional_json(
    path: Path,
) -> dict | None:

    if not path.exists():

        print(
            f"WARNING: Missing file:\n{path}"
        )

        return None

    return load_json(
        path
    )


def load_optional_report(
    path: Path,
) -> pd.DataFrame | None:

    if not path.exists():

        print(
            f"WARNING: Missing report:\n{path}"
        )

        return None

    return pd.read_csv(
        path,
        index_col=0,
    )


def load_run_summary(
    directory: Path,
) -> dict:

    path = (
        directory
        / "run_summary.json"
    )

    if path.exists():
        return load_json(path)

    return {}


def build_comparison() -> pd.DataFrame:

    rows = []

    # -------------------------------------------------------------------------
    # Day 10 TF-IDF
    # -------------------------------------------------------------------------

    baseline_metrics = (
        load_optional_json(
            BASELINE_DIR
            / "test_metrics.json"
        )
    )

    if baseline_metrics:

        baseline_summary = (
            load_run_summary(
                BASELINE_DIR
            )
        )

        rows.append(
            build_model_row(
                model_name=(
                    "TF-IDF + Logistic Regression"
                ),
                metrics=baseline_metrics,
                training_strategy=(
                    "balanced_logistic_regression"
                ),
                training_seconds=(
                    baseline_summary.get(
                        "training_seconds"
                    )
                ),
                max_length=None,
                epochs=None,
            )
        )

    # -------------------------------------------------------------------------
    # Day 12 Legal-BERT
    # -------------------------------------------------------------------------

    transformer_metrics = (
        load_optional_json(
            TRANSFORMER_DIR
            / "test_metrics.json"
        )
    )

    if transformer_metrics:

        transformer_summary = (
            load_run_summary(
                TRANSFORMER_DIR
            )
        )

        rows.append(
            build_model_row(
                model_name=(
                    "Legal-BERT"
                ),
                metrics=transformer_metrics,
                training_strategy=(
                    "standard_cross_entropy"
                ),
                training_seconds=(
                    transformer_summary.get(
                        "training_seconds"
                    )
                ),
                max_length=(
                    transformer_summary.get(
                        "max_length"
                    )
                ),
                epochs=(
                    transformer_summary.get(
                        "epochs"
                    )
                ),
            )
        )

    # -------------------------------------------------------------------------
    # Day 13 weighted Legal-BERT
    # -------------------------------------------------------------------------

    weighted_metrics = (
        load_optional_json(
            WEIGHTED_DIR
            / "test_metrics.json"
        )
    )

    if weighted_metrics:

        weighted_summary = (
            load_run_summary(
                WEIGHTED_DIR
            )
        )

        rows.append(
            build_model_row(
                model_name=(
                    "Class-Weighted Legal-BERT"
                ),
                metrics=weighted_metrics,
                training_strategy=(
                    "class_weighted_cross_entropy"
                ),
                training_seconds=(
                    weighted_summary.get(
                        "training_seconds"
                    )
                ),
                max_length=(
                    weighted_summary.get(
                        "max_length"
                    )
                ),
                epochs=(
                    weighted_summary.get(
                        "epochs"
                    )
                ),
            )
        )

    return pd.DataFrame(
        rows
    )


def build_reports():
    """
    Load available classification reports.
    """

    reports = {}

    baseline = load_optional_report(
        BASELINE_DIR
        / "test_classification_report.csv"
    )

    if baseline is not None:
        reports[
            "TF-IDF + Logistic Regression"
        ] = baseline


    transformer = load_optional_report(
        TRANSFORMER_DIR
        / "test_classification_report.csv"
    )

    if transformer is not None:
        reports[
            "Legal-BERT"
        ] = transformer


    weighted = load_optional_report(
        WEIGHTED_DIR
        / "test_classification_report.csv"
    )

    if weighted is not None:
        reports[
            "Class-Weighted Legal-BERT"
        ] = weighted

    return reports


def detect_experiment_difference(
    comparison_df: pd.DataFrame,
) -> list[str]:

    warnings = []

    transformer_rows = comparison_df[
        comparison_df[
            "model"
        ].isin(
            [
                "Legal-BERT",
                "Class-Weighted Legal-BERT",
            ]
        )
    ]

    if len(
        transformer_rows
    ) == 2:

        normal = transformer_rows[
            transformer_rows[
                "model"
            ] == "Legal-BERT"
        ].iloc[0]

        weighted = transformer_rows[
            transformer_rows[
                "model"
            ]
            == "Class-Weighted Legal-BERT"
        ].iloc[0]

        if (
            normal["max_length"]
            != weighted["max_length"]
        ):

            warnings.append(
                "Legal-BERT experiments used "
                "different max_length values."
            )

        if (
            normal["epochs"]
            != weighted["epochs"]
        ):

            warnings.append(
                "Legal-BERT experiments used "
                "different epoch counts."
            )

    return warnings


def save_text_summary(
    comparison_df: pd.DataFrame,
    selection: dict,
    warnings: list[str],
) -> None:

    path = (
        OUTPUT_DIR
        / "comparison_summary.txt"
    )

    lines = []

    lines.append(
        "Contract Intelligence Model Comparison"
    )

    lines.append(
        "=" * 60
    )

    lines.append("")

    for _, row in (
        comparison_df.iterrows()
    ):

        lines.append(
            f"Model: {row['model']}"
        )

        lines.append(
            f"Accuracy: {row['accuracy']}"
        )

        lines.append(
            f"Macro F1: {row['macro_f1']}"
        )

        lines.append(
            f"Weighted F1: "
            f"{row['weighted_f1']}"
        )

        lines.append("")

    lines.append(
        "Selected model:"
    )

    lines.append(
        selection[
            "selected_model"
        ]
    )

    lines.append(
        f"Selection metric: "
        f"{selection['selection_metric']}"
    )

    if warnings:

        lines.append("")

        lines.append(
            "Experiment limitations:"
        )

        for warning in warnings:

            lines.append(
                f"- {warning}"
            )

    path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> None:

    print_header(
        "DAY 14 - MODEL COMPARISON"
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    comparison_df = (
        build_comparison()
    )

    if comparison_df.empty:

        raise RuntimeError(
            "No model metrics were found."
        )

    print_header(
        "OVERALL MODEL PERFORMANCE"
    )

    display_columns = [
        "model",
        "accuracy",
        "macro_f1",
        "weighted_f1",
        "training_seconds",
        "max_length",
        "epochs",
    ]

    print(
        comparison_df[
            display_columns
        ]
        .sort_values(
            "macro_f1",
            ascending=False,
        )
        .to_string(
            index=False
        )
    )

    selection = (
        select_best_model(
            comparison_df
        )
    )

    print_header(
        "MODEL SELECTION"
    )

    print(
        f"Selected model : "
        f"{selection['selected_model']}"
    )

    print(
        f"Macro F1       : "
        f"{selection['macro_f1']:.4f}"
    )

    print(
        f"Weighted F1    : "
        f"{selection['weighted_f1']}"
    )

    print(
        f"Accuracy       : "
        f"{selection['accuracy']}"
    )

    # -------------------------------------------------------------------------
    # Minority-class comparison
    # -------------------------------------------------------------------------

    reports = build_reports()

    minority_df = (
        build_minority_comparison(
            reports,
            support_threshold=50,
        )
    )

    print_header(
        "MINORITY CLASS ANALYSIS"
    )

    if minority_df.empty:

        print(
            "No minority-class reports "
            "were available."
        )

    else:

        minority_summary = (
            minority_df.groupby(
                "model"
            )
            .agg(
                minority_classes=(
                    "clause_label",
                    "nunique",
                ),
                mean_minority_f1=(
                    "f1_score",
                    "mean",
                ),
                mean_minority_recall=(
                    "recall",
                    "mean",
                ),
            )
            .sort_values(
                "mean_minority_f1",
                ascending=False,
            )
        )

        print(
            minority_summary.to_string()
        )

    # -------------------------------------------------------------------------
    # Experiment-control warning
    # -------------------------------------------------------------------------

    warnings = (
        detect_experiment_difference(
            comparison_df
        )
    )

    print_header(
        "EXPERIMENT VALIDITY CHECK"
    )

    if warnings:

        for warning in warnings:

            print(
                f"WARNING: {warning}"
            )

        print(
            "\nThe transformer comparison "
            "is not perfectly controlled."
        )

    else:

        print(
            "No configuration differences "
            "detected between transformer runs."
        )

    # -------------------------------------------------------------------------
    # Save outputs
    # -------------------------------------------------------------------------

    comparison_df.to_csv(
        OUTPUT_DIR
        / "model_comparison.csv",
        index=False,
    )

    minority_df.to_csv(
        OUTPUT_DIR
        / "minority_class_comparison.csv",
        index=False,
    )

    with (
        OUTPUT_DIR
        / "model_selection.json"
    ).open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            {
                **selection,
                "experiment_warnings":
                    warnings,
            },
            file,
            indent=2,
        )

    save_text_summary(
        comparison_df,
        selection,
        warnings,
    )

    print_header(
        "DAY 14 COMPLETE"
    )

    print(
        f"Comparison outputs saved to:\n"
        f"{OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()