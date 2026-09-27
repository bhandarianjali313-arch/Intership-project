from __future__ import annotations

from pathlib import Path
from typing import Any

from ml.src.classification.inference import ClauseClassifier
from ml.src.risk.risk_scorer import ContractRiskScorer


PROJECT_ROOT = Path(__file__).resolve().parents[3]

MODEL_DIR = PROJECT_ROOT / "models" / "classification"

VECTORIZER_PATH = MODEL_DIR / "tfidf_vectorizer.joblib"
MODEL_PATH = MODEL_DIR / "logistic_regression.joblib"


class MLContractService:
    """
    Adapter between the backend application and the
    trained ML contract-analysis components.

    This service combines:
    - clause classification
    - confidence analysis
    - human-review recommendation
    - clause-level risk scoring
    """

    def __init__(
        self,
        classifier: Any | None = None,
        risk_scorer: Any | None = None,
    ) -> None:

        self.classifier = (
            classifier
            if classifier is not None
            else self._load_classifier()
        )

        self.risk_scorer = (
            risk_scorer
            if risk_scorer is not None
            else ContractRiskScorer()
        )

    @staticmethod
    def _load_classifier() -> ClauseClassifier:
        """
        Load the selected TF-IDF + Logistic Regression
        classification pipeline.
        """

        if not VECTORIZER_PATH.exists():
            raise FileNotFoundError(
                "TF-IDF vectorizer was not found at: "
                f"{VECTORIZER_PATH}"
            )

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                "Logistic Regression model was not found at: "
                f"{MODEL_PATH}"
            )

        return ClauseClassifier(
            vectorizer_path=VECTORIZER_PATH,
            model_path=MODEL_PATH,
        )

    @staticmethod
    def _validate_text(
        text: str,
    ) -> str:
        """
        Validate and normalize clause text.
        """

        if not isinstance(text, str):
            raise TypeError(
                "Clause text must be a string."
            )

        text = " ".join(
            text.split()
        )

        if not text:
            raise ValueError(
                "Clause text cannot be empty."
            )

        return text

    def analyze_clause(
        self,
        text: str,
        top_k: int = 3,
    ) -> dict[str, Any]:
        """
        Analyze a single contract clause.
        """

        text = self._validate_text(text)

        prediction = (
            self.classifier.predict_with_review(
                text=text,
                top_k=top_k,
            )
        )

        risk = (
            self.risk_scorer.score_prediction(
                prediction
            )
        )

        return {
            "text": text,

            "classification": {
                "predicted_label":
                    prediction["predicted_label"],

                "confidence":
                    prediction["confidence"],

                "confidence_level":
                    prediction["confidence_level"],

                "prediction_margin":
                    prediction.get(
                        "prediction_margin"
                    ),

                # Existing confidence pipeline may use
                # ambiguous_prediction rather than ambiguous.
                "ambiguous":
                    prediction.get(
                        "ambiguous_prediction",
                        prediction.get(
                            "ambiguous",
                            False,
                        ),
                    ),

                "requires_human_review":
                    prediction[
                        "requires_human_review"
                    ],

                "top_predictions":
                    prediction.get(
                        "top_predictions",
                        [],
                    ),
            },

            "risk": {
                "risk_level":
                    risk["risk_level"],

                "risk_score":
                    risk["risk_score"],

                "risk_reason":
                    risk.get(
                        "risk_reason"
                    ),
            },
        }

    def analyze_clauses(
        self,
        clauses: list[str],
        top_k: int = 3,
    ) -> list[dict[str, Any]]:
        """
        Analyze multiple clauses.
        """

        if not isinstance(
            clauses,
            list,
        ):
            raise TypeError(
                "clauses must be a list."
            )

        if not clauses:
            raise ValueError(
                "At least one clause is required."
            )

        return [
            self.analyze_clause(
                text=clause,
                top_k=top_k,
            )
            for clause in clauses
        ]

    def health(
        self,
    ) -> dict[str, Any]:
        """
        Return ML-service readiness information.
        """

        return {
            "status": "ready",

            "classifier":
                "TF-IDF + Logistic Regression",

            "risk_scorer":
                "ContractRiskScorer",

            "vectorizer_available":
                VECTORIZER_PATH.exists(),

            "model_available":
                MODEL_PATH.exists(),
        }