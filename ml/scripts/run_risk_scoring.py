from __future__ import annotations

from pathlib import Path
import json

from ml.src.classification.inference import (
    ClauseClassifier,
)

from ml.src.risk.risk_scorer import (
    ContractRiskScorer,
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


SAMPLE_CLAUSES = [
    (
        "This Agreement shall be governed by "
        "the laws of the State of New York."
    ),

    (
        "Neither party may assign this Agreement "
        "without the prior written consent of "
        "the other party."
    ),

    (
        "The liability of the Company under this "
        "Agreement shall be unlimited."
    ),

    (
        "Either party may terminate this Agreement "
        "for convenience upon thirty days prior "
        "written notice."
    ),
]


def main() -> None:

    print(
        "\n"
        + "=" * 80
    )

    print(
        "DAY 17 - LEGAL CLAUSE RISK SCORING"
    )

    print(
        "=" * 80
    )

    classifier = ClauseClassifier(
        vectorizer_path=VECTORIZER_PATH,
        model_path=MODEL_PATH,
    )

    risk_scorer = (
        ContractRiskScorer()
    )

    scored_clauses = []

    for number, text in enumerate(
        SAMPLE_CLAUSES,
        start=1,
    ):

        prediction = (
            classifier.predict_with_review(
                text=text,
                top_k=3,
            )
        )

        result = (
            risk_scorer.score_prediction(
                prediction
            )
        )

        scored_clauses.append(
            result
        )

        print(
            f"\nClause {number}"
        )

        print(
            "-" * 80
        )

        print(
            f"Text              : {text}"
        )

        print(
            f"Predicted label   : "
            f"{result['predicted_label']}"
        )

        print(
            f"Confidence        : "
            f"{result['confidence']:.4f}"
        )

        print(
            f"Confidence level  : "
            f"{result['confidence_level']}"
        )

        print(
            f"Risk level        : "
            f"{result['risk_level']}"
        )

        print(
            f"Risk score        : "
            f"{result['risk_score']}/3"
        )

        print(
            f"Human review      : "
            f"{result['requires_human_review']}"
        )

        print(
            f"Reason            : "
            f"{result['risk_reason']}"
        )


    summary = (
        risk_scorer.summarize_contract(
            scored_clauses
        )
    )

    print(
        "\n"
        + "=" * 80
    )

    print(
        "CONTRACT RISK SUMMARY"
    )

    print(
        "=" * 80
    )

    print(
        json.dumps(
            summary,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()