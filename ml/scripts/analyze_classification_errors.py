from pathlib import Path
import json

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

BASELINE_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "classification"
    / "baseline"
)

OUTPUT_DIR = (
    BASELINE_DIR
    / "error_analysis"
)

REPORT_PATH = (
    BASELINE_DIR
    / "test_classification_report.csv"
)

PREDICTIONS_PATH = (
    BASELINE_DIR
    / "test_predictions.csv"
)

CONFUSION_MATRIX_PATH = (
    BASELINE_DIR
    / "confusion_matrix.csv"
)


def print_header(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def load_report() -> pd.DataFrame:

    if not REPORT_PATH.exists():
        raise FileNotFoundError(
            "Test classification report not found.\n"
            "Run Day 10 first."
        )

    return pd.read_csv(
        REPORT_PATH,
        index_col=0,
    )


def load_predictions() -> pd.DataFrame:

    if not PREDICTIONS_PATH.exists():
        raise FileNotFoundError(
            "Test predictions not found.\n"
            "Run Day 10 first."
        )

    return pd.read_csv(
        PREDICTIONS_PATH
    )


def load_confusion_matrix() -> pd.DataFrame:

    if not CONFUSION_MATRIX_PATH.exists():
        raise FileNotFoundError(
            "Confusion matrix not found.\n"
            "Run Day 10 first."
        )

    return pd.read_csv(
        CONFUSION_MATRIX_PATH,
        index_col=0,
    )


def clean_report(
    report: pd.DataFrame,
) -> pd.DataFrame:
    """
    Keep only actual class rows.
    """

    report = report.copy()

    report["support"] = pd.to_numeric(
        report["support"],
        errors="coerce",
    )

    report = report[
        report["support"].notna()
    ].copy()

    report = report[
        ~report.index.isin(
            [
                "accuracy",
                "macro avg",
                "weighted avg",
            ]
        )
    ]

    return report


def get_worst_classes(
    report: pd.DataFrame,
    top_n: int = 10,
) -> pd.DataFrame:

    return (
        report.sort_values(
            "f1-score",
            ascending=True,
        )
        .head(top_n)
        .copy()
    )


def get_best_classes(
    report: pd.DataFrame,
    top_n: int = 10,
) -> pd.DataFrame:

    return (
        report.sort_values(
            "f1-score",
            ascending=False,
        )
        .head(top_n)
        .copy()
    )


def build_top_confusions(
    matrix: pd.DataFrame,
    top_n: int = 20,
) -> pd.DataFrame:

    rows = []

    for actual_label in matrix.index:

        for predicted_label in matrix.columns:

            if actual_label == predicted_label:
                continue

            count = int(
                matrix.loc[
                    actual_label,
                    predicted_label,
                ]
            )

            if count <= 0:
                continue

            rows.append(
                {
                    "actual_label": actual_label,
                    "predicted_label": predicted_label,
                    "count": count,
                }
            )

    result = pd.DataFrame(rows)

    if result.empty:
        return result

    return (
        result.sort_values(
            "count",
            ascending=False,
        )
        .head(top_n)
        .reset_index(drop=True)
    )


def get_high_confidence_errors(
    predictions: pd.DataFrame,
    top_n: int = 25,
) -> pd.DataFrame:

    errors = predictions[
        predictions["label_id"]
        != predictions["predicted_label_id"]
    ].copy()

    if errors.empty:
        return errors

    return (
        errors.sort_values(
            "confidence",
            ascending=False,
        )
        .head(top_n)
        .copy()
    )


def add_support_bucket(
    report: pd.DataFrame,
) -> pd.DataFrame:

    result = report.copy()

    result["support_bucket"] = pd.cut(
        result["support"],
        bins=[
            0,
            10,
            25,
            50,
            100,
            250,
            500,
            float("inf"),
        ],
        labels=[
            "1-10",
            "11-25",
            "26-50",
            "51-100",
            "101-250",
            "251-500",
            "500+",
        ],
        include_lowest=True,
    )

    return result


def build_support_summary(
    report: pd.DataFrame,
) -> pd.DataFrame:

    bucketed = add_support_bucket(
        report
    )

    summary = (
        bucketed.groupby(
            "support_bucket",
            observed=False,
        )
        .agg(
            classes=(
                "f1-score",
                "count",
            ),
            mean_precision=(
                "precision",
                "mean",
            ),
            mean_recall=(
                "recall",
                "mean",
            ),
            mean_f1=(
                "f1-score",
                "mean",
            ),
            total_support=(
                "support",
                "sum",
            ),
        )
        .reset_index()
    )

    return summary


def print_class_table(
    title: str,
    df: pd.DataFrame,
) -> None:

    print_header(title)

    if df.empty:
        print("No data found.")
        return

    columns = [
        "precision",
        "recall",
        "f1-score",
        "support",
    ]

    print(
        df[columns]
        .to_string()
    )


def main() -> None:

    print_header(
        "DAY 11 - CLASSIFICATION ERROR ANALYSIS"
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = clean_report(
        load_report()
    )

    predictions = (
        load_predictions()
    )

    confusion_matrix = (
        load_confusion_matrix()
    )

    print(
        f"Classes analyzed     : "
        f"{len(report)}"
    )

    print(
        f"Test predictions     : "
        f"{len(predictions):,}"
    )

    wrong_predictions = (
        predictions[
            predictions["label_id"]
            != predictions["predicted_label_id"]
        ]
    )

    print(
        f"Wrong predictions    : "
        f"{len(wrong_predictions):,}"
    )

    error_rate = (
        len(wrong_predictions)
        / len(predictions)
        if len(predictions)
        else 0
    )

    print(
        f"Error rate           : "
        f"{error_rate:.4f}"
    )

    worst_classes = (
        get_worst_classes(
            report
        )
    )

    best_classes = (
        get_best_classes(
            report
        )
    )

    top_confusions = (
        build_top_confusions(
            confusion_matrix
        )
    )

    high_confidence_errors = (
        get_high_confidence_errors(
            predictions
        )
    )

    support_summary = (
        build_support_summary(
            report
        )
    )

    print_class_table(
        "WORST 10 CLASSES",
        worst_classes,
    )

    print_class_table(
        "BEST 10 CLASSES",
        best_classes,
    )

    print_header(
        "TOP CLASS CONFUSIONS"
    )

    if top_confusions.empty:
        print(
            "No class confusions found."
        )
    else:
        print(
            top_confusions.to_string(
                index=False
            )
        )

    print_header(
        "HIGH-CONFIDENCE WRONG PREDICTIONS"
    )

    if high_confidence_errors.empty:
        print(
            "No incorrect predictions found."
        )
    else:

        columns = [
            "contract_id",
            "clause_label",
            "label_id",
            "predicted_label_id",
            "confidence",
            "cleaned_clause_text",
        ]

        available_columns = [
            column
            for column in columns
            if column
            in high_confidence_errors.columns
        ]

        print(
            high_confidence_errors[
                available_columns
            ]
            .head(10)
            .to_string(
                index=False
            )
        )

    print_header(
        "PERFORMANCE BY CLASS SUPPORT"
    )

    print(
        support_summary.to_string(
            index=False
        )
    )

    worst_classes.to_csv(
        OUTPUT_DIR
        / "worst_classes.csv"
    )

    best_classes.to_csv(
        OUTPUT_DIR
        / "best_classes.csv"
    )

    top_confusions.to_csv(
        OUTPUT_DIR
        / "top_confusions.csv",
        index=False,
    )

    high_confidence_errors.to_csv(
        OUTPUT_DIR
        / "high_confidence_errors.csv",
        index=False,
    )

    support_summary.to_csv(
        OUTPUT_DIR
        / "class_performance_by_support.csv",
        index=False,
    )

    summary = {
        "classes_analyzed": int(
            len(report)
        ),
        "test_examples": int(
            len(predictions)
        ),
        "wrong_predictions": int(
            len(wrong_predictions)
        ),
        "error_rate": float(
            error_rate
        ),
        "worst_class": (
            str(
                worst_classes.index[0]
            )
            if not worst_classes.empty
            else None
        ),
        "worst_class_f1": (
            float(
                worst_classes.iloc[0][
                    "f1-score"
                ]
            )
            if not worst_classes.empty
            else None
        ),
        "best_class": (
            str(
                best_classes.index[0]
            )
            if not best_classes.empty
            else None
        ),
        "best_class_f1": (
            float(
                best_classes.iloc[0][
                    "f1-score"
                ]
            )
            if not best_classes.empty
            else None
        ),
    }

    with (
        OUTPUT_DIR
        / "error_summary.json"
    ).open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            summary,
            file,
            indent=2,
        )

    print_header(
        "DAY 11 COMPLETE"
    )

    print(
        f"Error analysis saved to:\n"
        f"{OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()