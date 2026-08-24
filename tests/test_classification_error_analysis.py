import pandas as pd

from ml.scripts.analyze_classification_errors import (
    build_support_summary,
    build_top_confusions,
    clean_report,
    get_best_classes,
    get_high_confidence_errors,
    get_worst_classes,
)


def test_clean_report_removes_summary_rows():

    df = pd.DataFrame(
        {
            "precision": [
                0.5,
                0.6,
                0.7,
            ],
            "recall": [
                0.5,
                0.6,
                0.7,
            ],
            "f1-score": [
                0.5,
                0.6,
                0.7,
            ],
            "support": [
                10,
                20,
                30,
            ],
        },
        index=[
            "CLASS_A",
            "macro avg",
            "weighted avg",
        ],
    )

    result = clean_report(df)

    assert list(
        result.index
    ) == [
        "CLASS_A"
    ]


def test_get_worst_classes():

    df = pd.DataFrame(
        {
            "f1-score": [
                0.9,
                0.2,
                0.6,
            ]
        },
        index=[
            "A",
            "B",
            "C",
        ],
    )

    result = (
        get_worst_classes(
            df,
            top_n=1,
        )
    )

    assert (
        result.index[0]
        == "B"
    )


def test_get_best_classes():

    df = pd.DataFrame(
        {
            "f1-score": [
                0.9,
                0.2,
                0.6,
            ]
        },
        index=[
            "A",
            "B",
            "C",
        ],
    )

    result = (
        get_best_classes(
            df,
            top_n=1,
        )
    )

    assert (
        result.index[0]
        == "A"
    )


def test_confusion_diagonal_is_ignored():

    matrix = pd.DataFrame(
        [
            [10, 2],
            [3, 8],
        ],
        index=[
            "A",
            "B",
        ],
        columns=[
            "A",
            "B",
        ],
    )

    result = (
        build_top_confusions(
            matrix,
            top_n=10,
        )
    )

    assert len(result) == 2

    assert (
        result.iloc[0]["count"]
        == 3
    )


def test_high_confidence_errors():

    df = pd.DataFrame(
        {
            "label_id": [
                0,
                1,
                2,
            ],
            "predicted_label_id": [
                0,
                2,
                0,
            ],
            "confidence": [
                0.90,
                0.70,
                0.95,
            ],
        }
    )

    result = (
        get_high_confidence_errors(
            df,
            top_n=1,
        )
    )

    assert len(result) == 1

    assert (
        result.iloc[0][
            "confidence"
        ]
        == 0.95
    )


def test_support_summary():

    df = pd.DataFrame(
        {
            "precision": [
                0.4,
                0.8,
            ],
            "recall": [
                0.5,
                0.9,
            ],
            "f1-score": [
                0.44,
                0.85,
            ],
            "support": [
                8,
                150,
            ],
        },
        index=[
            "A",
            "B",
        ],
    )

    result = (
        build_support_summary(
            df
        )
    )

    assert (
        "mean_f1"
        in result.columns
    )

    assert (
        "total_support"
        in result.columns
    )