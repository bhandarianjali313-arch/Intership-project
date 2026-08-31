from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ml.src.classification.inference import (
    ClauseClassifier,
)

from ml.src.evaluation.pipeline_evaluator import (
    PipelineEvaluator,
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
    / "evaluation"
)


def find_column(
    dataframe: pd.DataFrame,
    candidates: list[str],
) -> str:
    """
    Find the first matching column name.

    This keeps the script compatible with small
    differences in earlier preprocessing versions.
    """

    for candidate in candidates:

        if candidate in dataframe.columns:
            return candidate

    raise ValueError(
        "Could not find any of these columns: "
        f"{candidates}\n\n"
        "Available columns:\n"
        f"{dataframe.columns.tolist()}"
    )


def main() -> None:

    print()
    print("=" * 80)
    print("DAY 20 - PIPELINE EVALUATION")
    print("=" * 80)

    if not TEST_PATH.exists():

        raise FileNotFoundError(
            "Test dataset not found:\n"
            f"{TEST_PATH}"
        )

    print(
        f"\nLoading test data:\n{TEST_PATH}"
    )

    dataframe = pd.read_csv(
        TEST_PATH
    )

    print(
        f"\nTest examples: {len(dataframe):,}"
    )

    text_column = find_column(
        dataframe,
        [
            "cleaned_clause_text",
            "clause_text",
            "text",
            "cleaned_text",
        ],
    )

    label_column = find_column(
        dataframe,
        [
            "clause_label",
            "label",
            "normalized_label",
            "clause_type",
        ],
    )

    print(
        f"Text column : {text_column}"
    )

    print(
        f"Label column: {label_column}"
    )

    classifier = ClauseClassifier(
        vectorizer_path=VECTORIZER_PATH,
        model_path=MODEL_PATH,
    )

    predictions = []

    print(
        "\nRunning confidence-aware predictions..."
    )

    for row_number, row in dataframe.iterrows():

        text = str(
            row[text_column]
        )

        true_label = str(
            row[label_column]
        )

        prediction = (
            classifier.predict_with_review(
                text=text,
                top_k=3,
            )
        )

        predictions.append(
            {
                "row_number":
                    int(row_number),

                "text":
                    text,

                "true_label":
                    true_label,

                "predicted_label":
                    str(
                        prediction[
                            "predicted_label"
                        ]
                    ),

                "confidence":
                    float(
                        prediction[
                            "confidence"
                        ]
                    ),

                "confidence_level":
                    prediction[
                        "confidence_level"
                    ],

                "requires_human_review":
                    bool(
                        prediction[
                            "requires_human_review"
                        ]
                    ),

                "ambiguous_prediction":
                    bool(
                        prediction.get(
                            "ambiguous_prediction",
                            False,
                        )
                    ),

                "prediction_margin":
                    prediction.get(
                        "prediction_margin"
                    ),
            }
        )

        if (
            (row_number + 1)
            % 500
            == 0
        ):

            print(
                f"Processed "
                f"{row_number + 1:,}/"
                f"{len(dataframe):,}"
            )

    evaluator = (
        PipelineEvaluator()
    )

    results = evaluator.evaluate(
        predictions
    )

    overall = results[
        "overall_metrics"
    ]

    print()
    print("=" * 80)
    print("OVERALL PERFORMANCE")
    print("=" * 80)

    print(
        f"Accuracy        : "
        f"{overall['accuracy']:.4f}"
    )

    print(
        f"Macro Precision : "
        f"{overall['macro_precision']:.4f}"
    )

    print(
        f"Macro Recall    : "
        f"{overall['macro_recall']:.4f}"
    )

    print(
        f"Macro F1        : "
        f"{overall['macro_f1']:.4f}"
    )

    print(
        f"Weighted F1     : "
        f"{overall['weighted_f1']:.4f}"
    )

    print()
    print("=" * 80)
    print("CONFIDENCE PERFORMANCE")
    print("=" * 80)

    for level, metrics in results[
        "confidence_metrics"
    ].items():

        accuracy = metrics[
            "accuracy"
        ]

        accuracy_text = (
            f"{accuracy:.4f}"
            if accuracy is not None
            else "N/A"
        )

        print(
            f"{level:<8} "
            f"Count: {metrics['count']:<5} "
            f"Accuracy: {accuracy_text}"
        )

    review = results[
        "review_metrics"
    ]

    print()
    print("=" * 80)
    print("HUMAN REVIEW ANALYSIS")
    print("=" * 80)

    print(
        f"Total predictions : "
        f"{review['total_predictions']}"
    )

    print(
        f"Require review    : "
        f"{review['review_count']}"
    )

    print(
        f"Review rate       : "
        f"{review['review_rate']:.2%}"
    )

    print(
        f"Auto accepted     : "
        f"{review['accepted_count']}"
    )

    accepted_accuracy = (
        review[
            "accepted_accuracy"
        ]
    )

    if accepted_accuracy is not None:

        print(
            f"Accepted accuracy : "
            f"{accepted_accuracy:.4f}"
        )

    print()
    print("=" * 80)
    print("WORST PERFORMING CLAUSE TYPES")
    print("=" * 80)

    for item in results[
        "worst_classes"
    ]:

        print(
            f"{item['label']:<40} "
            f"support={item['support']:<4} "
            f"F1={item['f1']:.4f}"
        )

    print()
    print("=" * 80)
    print("TOP CONFUSION PAIRS")
    print("=" * 80)

    for item in results[
        "top_confusion_pairs"
    ]:

        print(
            f"{item['true_label']} "
            f"→ {item['predicted_label']} "
            f"({item['count']})"
        )

    print()
    print("=" * 80)
    print("HIGH-CONFIDENCE ERRORS")
    print("=" * 80)

    high_errors = results[
        "high_confidence_errors"
    ]

    print(
        f"High-confidence errors shown: "
        f"{len(high_errors)}"
    )

    for item in high_errors[:5]:

        print(
            f"\nTrue       : "
            f"{item['true_label']}"
        )

        print(
            f"Predicted  : "
            f"{item['predicted_label']}"
        )

        print(
            f"Confidence : "
            f"{item['confidence']:.4f}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    results_path = (
        OUTPUT_DIR
        / "pipeline_evaluation.json"
    )

    predictions_path = (
        OUTPUT_DIR
        / "pipeline_predictions.csv"
    )

    with results_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False,
        )

    pd.DataFrame(
        predictions
    ).to_csv(
        predictions_path,
        index=False,
    )

    print()
    print("=" * 80)
    print("DAY 20 COMPLETE")
    print("=" * 80)

    print(
        f"\nEvaluation:\n{results_path}"
    )

    print(
        f"\nPredictions:\n{predictions_path}"
    )


if __name__ == "__main__":
    main()