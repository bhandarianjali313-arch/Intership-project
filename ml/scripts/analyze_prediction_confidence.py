from __future__ import annotations

from pathlib import Path

import pandas as pd

from ml.src.classification.inference import (
    ClauseClassifier,
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

MODEL_DIR = (
    PROJECT_ROOT
    / "models"
    / "classification"
)

VECTORIZER_PATH = (
    MODEL_DIR
    / "tfidf_vectorizer.joblib"
)

MODEL_PATH = (
    MODEL_DIR
    / "logistic_regression.joblib"
)

TEST_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "classification"
    / "test.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "classification"
    / "confidence_analysis"
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


def main() -> None:

    print_header(
        "DAY 16 - CONFIDENCE AND REVIEW ANALYSIS"
    )

    if not TEST_PATH.exists():

        raise FileNotFoundError(
            f"Test dataset not found:\n{TEST_PATH}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    classifier = ClauseClassifier(
        vectorizer_path=VECTORIZER_PATH,
        model_path=MODEL_PATH,
    )

    test_df = pd.read_csv(
        TEST_PATH
    )

    print(
        f"Test examples: {len(test_df):,}"
    )

    results = []

    for index, row in (
        test_df.iterrows()
    ):

        text = str(
            row["cleaned_clause_text"]
        )

        prediction = (
            classifier.predict_with_review(
                text=text,
                top_k=3,
            )
        )

        true_label = str(
            row["clause_label"]
        )

        predicted_label = (
            prediction[
                "predicted_label"
            ]
        )

        results.append(
            {
                "true_label":
                    true_label,

                "predicted_label":
                    predicted_label,

                "correct":
                    true_label
                    == predicted_label,

                "confidence":
                    prediction[
                        "confidence"
                    ],

                "confidence_level":
                    prediction[
                        "confidence_level"
                    ],

                "recommended_action":
                    prediction[
                        "recommended_action"
                    ],

                "requires_human_review":
                    prediction[
                        "requires_human_review"
                    ],

                "prediction_margin":
                    prediction[
                        "prediction_margin"
                    ],

                "ambiguous_prediction":
                    prediction[
                        "ambiguous_prediction"
                    ],
            }
        )

        if (
            (index + 1) % 500
            == 0
        ):

            print(
                f"Processed "
                f"{index + 1:,}/"
                f"{len(test_df):,}"
            )

    result_df = pd.DataFrame(
        results
    )

    print_header(
        "CONFIDENCE DISTRIBUTION"
    )

    confidence_distribution = (
        result_df[
            "confidence_level"
        ]
        .value_counts()
    )

    print(
        confidence_distribution.to_string()
    )


    print_header(
        "REVIEW ANALYSIS"
    )

    review_count = int(
        result_df[
            "requires_human_review"
        ].sum()
    )

    total = len(
        result_df
    )

    review_percentage = (
        100.0
        * review_count
        / total
    )

    print(
        f"Predictions requiring review : "
        f"{review_count:,}"
    )

    print(
        f"Review percentage            : "
        f"{review_percentage:.2f}%"
    )


    print_header(
        "ACCURACY BY CONFIDENCE LEVEL"
    )

    accuracy_by_confidence = (
        result_df
        .groupby(
            "confidence_level"
        )["correct"]
        .agg(
            [
                "count",
                "mean",
            ]
        )
        .rename(
            columns={
                "count": "examples",
                "mean": "accuracy",
            }
        )
    )

    print(
        accuracy_by_confidence.to_string()
    )


    print_header(
        "AMBIGUITY ANALYSIS"
    )

    ambiguous_count = int(
        result_df[
            "ambiguous_prediction"
        ].sum()
    )

    print(
        f"Ambiguous predictions : "
        f"{ambiguous_count:,}"
    )

    print(
        f"Ambiguous percentage  : "
        f"{100 * ambiguous_count / total:.2f}%"
    )


    print_header(
        "ERROR CONFIDENCE ANALYSIS"
    )

    errors = result_df[
        ~result_df["correct"]
    ]

    if errors.empty:

        print(
            "No classification errors found."
        )

    else:

        print(
            f"Total errors          : "
            f"{len(errors):,}"
        )

        print(
            f"Mean error confidence : "
            f"{errors['confidence'].mean():.4f}"
        )

        high_confidence_errors = (
            errors[
                errors[
                    "confidence_level"
                ]
                == "HIGH"
            ]
        )

        print(
            f"High-confidence errors: "
            f"{len(high_confidence_errors):,}"
        )


    # Save full analysis

    result_df.to_csv(
        OUTPUT_DIR
        / "confidence_predictions.csv",
        index=False,
    )

    accuracy_by_confidence.to_csv(
        OUTPUT_DIR
        / "accuracy_by_confidence.csv"
    )

    summary = pd.DataFrame(
        [
            {
                "total_predictions":
                    total,

                "requires_review":
                    review_count,

                "review_percentage":
                    review_percentage,

                "ambiguous_predictions":
                    ambiguous_count,

                "mean_confidence":
                    result_df[
                        "confidence"
                    ].mean(),

                "overall_accuracy":
                    result_df[
                        "correct"
                    ].mean(),
            }
        ]
    )

    summary.to_csv(
        OUTPUT_DIR
        / "confidence_summary.csv",
        index=False,
    )


    print_header(
        "DAY 16 COMPLETE"
    )

    print(
        "Confidence-aware review analysis "
        "completed successfully."
    )

    print(
        f"\nResults saved to:\n"
        f"{OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()