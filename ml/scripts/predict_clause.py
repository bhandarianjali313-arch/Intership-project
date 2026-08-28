from __future__ import annotations

from pathlib import Path
import argparse
import json

from ml.src.classification.inference import (
    ClauseClassifier,
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)


# IMPORTANT:
# Change these two filenames only if your
# Day 10 artifacts use different names.

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


def build_parser():
    """
    Build command-line arguments.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Predict CUAD legal clause "
            "categories using the selected "
            "TF-IDF classifier."
        )
    )

    parser.add_argument(
        "--text",
        type=str,
        help=(
            "Legal clause text to classify."
        ),
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help=(
            "Number of predictions to return."
        ),
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help=(
            "Print result as JSON."
        ),
    )

    return parser


def print_result(
    result: dict,
) -> None:

    print_header(
        "CLAUSE CLASSIFICATION RESULT"
    )

    print(
        f"Predicted label : "
        f"{result['predicted_label']}"
    )

    print(
        f"Confidence      : "
        f"{result['confidence']:.4f}"
    )

    print(
        "\nTop predictions:"
    )

    for prediction in (
        result[
            "top_predictions"
        ]
    ):

        print(
            f"{prediction['rank']}. "
            f"{prediction['label']:<35} "
            f"{prediction['confidence']:.4f}"
        )


def main() -> None:

    parser = build_parser()

    args = parser.parse_args()

    print_header(
        "DAY 15 - CLAUSE CLASSIFICATION INFERENCE"
    )

    classifier = ClauseClassifier(
        vectorizer_path=(
            VECTORIZER_PATH
        ),
        model_path=(
            MODEL_PATH
        ),
    )

    if args.text:

        text = args.text

    else:

        print(
            "Enter a legal clause:"
        )

        text = input(
            "> "
        )

    result = classifier.predict(
        text=text,
        top_k=args.top_k,
    )

    if args.json:

        print(
            json.dumps(
                result,
                indent=2,
            )
        )

    else:

        print_result(
            result
        )


if __name__ == "__main__":
    main()