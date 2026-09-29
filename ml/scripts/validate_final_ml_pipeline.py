from __future__ import annotations

from pathlib import Path

from ml.src.classification.inference import (
    ClauseClassifier,
)

from ml.src.classification.labels import (
    CLAUSE_LABELS,
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


def print_header(
    title: str,
) -> None:

    print(
        "\n"
        + "=" * 80
    )

    print(
        title
    )

    print(
        "=" * 80
    )


def main() -> None:

    print_header(
        "DAY 25 - FINAL ML PIPELINE VALIDATION"
    )

    # -------------------------------------------------------------------------
    # ARTIFACT CHECK
    # -------------------------------------------------------------------------

    print_header(
        "MODEL ARTIFACTS"
    )

    print(
        f"Vectorizer : "
        f"{VECTORIZER_PATH}"
    )

    print(
        f"Model      : "
        f"{MODEL_PATH}"
    )

    if not VECTORIZER_PATH.exists():

        raise FileNotFoundError(
            "TF-IDF vectorizer is missing."
        )

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            "Logistic Regression model is missing."
        )

    print(
        "Artifacts   : OK"
    )

    # -------------------------------------------------------------------------
    # LOAD CLASSIFIER
    # -------------------------------------------------------------------------

    classifier = (
        ClauseClassifier(
            vectorizer_path=(
                VECTORIZER_PATH
            ),
            model_path=(
                MODEL_PATH
            ),
        )
    )

    risk_scorer = (
        ContractRiskScorer()
    )

    # -------------------------------------------------------------------------
    # MODEL INFORMATION
    # -------------------------------------------------------------------------

    info = (
        classifier.get_model_info()
    )

    print_header(
        "MODEL INFORMATION"
    )

    print(
        f"Model type        : "
        f"{info['model_type']}"
    )

    print(
        f"Vectorizer type   : "
        f"{info['vectorizer_type']}"
    )

    print(
        f"Number of classes : "
        f"{info['number_of_classes']}"
    )

    print(
        f"Label decoding    : "
        f"{info['label_decoding_enabled']}"
    )

    # -------------------------------------------------------------------------
    # CLASS-MAPPING VALIDATION
    # -------------------------------------------------------------------------

    decoded_classes = set(
        info[
            "classes"
        ]
    )

    canonical_classes = set(
        CLAUSE_LABELS
    )

    unexpected_classes = (
        decoded_classes
        - canonical_classes
    )

    if unexpected_classes:

        raise RuntimeError(
            "Unexpected classifier labels detected: "
            f"{sorted(unexpected_classes)}"
        )

    print(
        "Class mapping      : VALID"
    )

    # -------------------------------------------------------------------------
    # END-TO-END SAMPLE INFERENCE
    # -------------------------------------------------------------------------

    samples = [
        (
            "Neither party may assign this "
            "Agreement without prior written consent."
        ),
        (
            "This Agreement shall be governed "
            "by the laws of the State of Delaware."
        ),
        (
            "The employee shall not compete "
            "with the company for two years."
        ),
        (
            "Either party may terminate this "
            "Agreement for convenience upon "
            "thirty days written notice."
        ),
    ]

    print_header(
        "END-TO-END SAMPLE PREDICTIONS"
    )

    for index, text in enumerate(
        samples,
        start=1,
    ):

        prediction = (
            classifier.predict_with_review(
                text=text,
                top_k=3,
            )
        )

        risk = (
            risk_scorer.score_prediction(
                prediction
            )
        )

        print(
            f"\nClause {index}"
        )

        print(
            f"Text       : {text}"
        )

        print(
            "Raw label  : "
            f"{prediction.get('raw_predicted_label')}"
        )

        print(
            "Label      : "
            f"{prediction['predicted_label']}"
        )

        print(
            "Confidence : "
            f"{prediction['confidence']:.4f}"
        )

        print(
            "Conf level : "
            f"{prediction['confidence_level']}"
        )

        print(
            "Review     : "
            f"{prediction['requires_human_review']}"
        )

        print(
            "Risk       : "
            f"{risk['risk_level']}"
        )

        print(
            "Risk score : "
            f"{risk['risk_score']}"
        )

    print_header(
        "FINAL VALIDATION COMPLETE"
    )

    print(
        "Classifier labels are decoded before "
        "risk scoring."
    )

    print(
        "The ML inference pipeline is ready for "
        "backend/API integration."
    )


if __name__ == "__main__":
    main()