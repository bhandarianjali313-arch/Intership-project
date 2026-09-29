from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np

from ml.src.classification.confidence import (
    ConfidenceConfig,
    assess_prediction,
)

from ml.src.classification.labels import (
    decode_clause_label,
)


class ClauseClassifier:
    """
    Reusable inference service for the selected
    TF-IDF + Logistic Regression clause classifier.

    The classifier loads model artifacts once and can
    then make repeated predictions efficiently.

    Predictions are converted from raw model class IDs
    into canonical CUAD clause labels before being
    returned to downstream confidence and risk layers.
    """

    def __init__(
        self,
        vectorizer_path: str | Path,
        model_path: str | Path,
    ) -> None:

        self.vectorizer_path = Path(
            vectorizer_path
        )

        self.model_path = Path(
            model_path
        )

        self.vectorizer = None
        self.model = None

        self._validate_paths()
        self._load_artifacts()


    # =========================================================================
    # MODEL LOADING
    # =========================================================================

    def _validate_paths(
        self,
    ) -> None:
        """
        Ensure required model artifacts exist.
        """

        if not self.vectorizer_path.exists():

            raise FileNotFoundError(
                "TF-IDF vectorizer not found: "
                f"{self.vectorizer_path}"
            )

        if not self.model_path.exists():

            raise FileNotFoundError(
                "Classification model not found: "
                f"{self.model_path}"
            )


    def _load_artifacts(
        self,
    ) -> None:
        """
        Load serialized model artifacts.
        """

        self.vectorizer = joblib.load(
            self.vectorizer_path
        )

        self.model = joblib.load(
            self.model_path
        )


    # =========================================================================
    # INPUT VALIDATION
    # =========================================================================

    @staticmethod
    def _validate_text(
        text: str,
    ) -> str:
        """
        Validate and normalize raw inference input.
        """

        if not isinstance(
            text,
            str,
        ):

            raise TypeError(
                "Clause text must be a string."
            )

        cleaned_text = " ".join(
            text.split()
        )

        if not cleaned_text:

            raise ValueError(
                "Clause text cannot be empty."
            )

        return cleaned_text


    @staticmethod
    def _validate_top_k(
        top_k: int,
    ) -> None:
        """
        Validate number of requested predictions.
        """

        if not isinstance(
            top_k,
            int,
        ):

            raise TypeError(
                "top_k must be an integer."
            )

        if top_k <= 0:

            raise ValueError(
                "top_k must be greater than 0."
            )


    # =========================================================================
    # STANDARD PREDICTION
    # =========================================================================

    def predict(
        self,
        text: str,
        top_k: int = 3,
    ) -> dict[str, Any]:
        """
        Predict the most likely clause category.

        Raw model class IDs are converted into
        canonical legal clause labels before the
        result is returned.

        Returns:

            text
            predicted_label
            confidence
            top_predictions
        """

        cleaned_text = (
            self._validate_text(
                text
            )
        )

        self._validate_top_k(
            top_k
        )

        # ---------------------------------------------------------------------
        # TF-IDF TRANSFORMATION
        # ---------------------------------------------------------------------

        features = (
            self.vectorizer.transform(
                [cleaned_text]
            )
        )

        # ---------------------------------------------------------------------
        # CLASS PROBABILITIES
        # ---------------------------------------------------------------------

        probabilities = (
            self.model.predict_proba(
                features
            )[0]
        )

        raw_classes = np.asarray(
            self.model.classes_
        )

        top_k = min(
            top_k,
            len(
                raw_classes
            ),
        )

        ranked_indices = (
            np.argsort(
                probabilities
            )[::-1][
                :top_k
            ]
        )

        top_predictions = []

        for rank, index in enumerate(
            ranked_indices,
            start=1,
        ):

            raw_label = (
                raw_classes[
                    index
                ]
            )

            decoded_label = (
                decode_clause_label(
                    raw_label
                )
            )

            top_predictions.append(
                {
                    "rank":
                        rank,

                    "label":
                        decoded_label,

                    "raw_label":
                        str(
                            raw_label
                        ),

                    "confidence":
                        float(
                            probabilities[
                                index
                            ]
                        ),
                }
            )

        best = (
            top_predictions[
                0
            ]
        )

        return {
            "text":
                cleaned_text,

            "predicted_label":
                best[
                    "label"
                ],

            "raw_predicted_label":
                best[
                    "raw_label"
                ],

            "confidence":
                best[
                    "confidence"
                ],

            "top_predictions":
                top_predictions,
        }


    # =========================================================================
    # CONFIDENCE-AWARE PREDICTION
    # =========================================================================

    def predict_with_review(
        self,
        text: str,
        top_k: int = 3,
        confidence_config: (
            ConfidenceConfig
            | None
        ) = None,
        ambiguity_margin: float = 0.10,
    ) -> dict[str, Any]:
        """
        Predict a clause category and attach
        confidence-aware review information.

        At least two predictions are requested
        internally because ambiguity detection requires
        comparison between the two strongest classes.
        """

        self._validate_top_k(
            top_k
        )

        if ambiguity_margin < 0:

            raise ValueError(
                "ambiguity_margin cannot be negative."
            )

        internal_top_k = max(
            top_k,
            2,
        )

        prediction = self.predict(
            text=text,
            top_k=internal_top_k,
        )

        assessed_prediction = (
            assess_prediction(
                prediction,
                config=confidence_config,
                ambiguity_margin=(
                    ambiguity_margin
                ),
            )
        )

        assessed_prediction[
            "top_predictions"
        ] = (
            assessed_prediction[
                "top_predictions"
            ][
                :top_k
            ]
        )

        return (
            assessed_prediction
        )


    # =========================================================================
    # BATCH PREDICTION
    # =========================================================================

    def predict_batch(
        self,
        texts: list[str],
        top_k: int = 3,
    ) -> list[
        dict[str, Any]
    ]:
        """
        Predict multiple clauses.
        """

        if not isinstance(
            texts,
            list,
        ):

            raise TypeError(
                "texts must be a list."
            )

        if not texts:

            raise ValueError(
                "texts cannot be empty."
            )

        self._validate_top_k(
            top_k
        )

        return [
            self.predict(
                text,
                top_k=top_k,
            )
            for text
            in texts
        ]


    # =========================================================================
    # CONFIDENCE-AWARE BATCH PREDICTION
    # =========================================================================

    def predict_batch_with_review(
        self,
        texts: list[str],
        top_k: int = 3,
        confidence_config: (
            ConfidenceConfig
            | None
        ) = None,
        ambiguity_margin: float = 0.10,
    ) -> list[
        dict[str, Any]
    ]:
        """
        Predict multiple clauses with confidence-aware
        human-review recommendations.
        """

        if not isinstance(
            texts,
            list,
        ):

            raise TypeError(
                "texts must be a list."
            )

        if not texts:

            raise ValueError(
                "texts cannot be empty."
            )

        self._validate_top_k(
            top_k
        )

        return [
            self.predict_with_review(
                text=text,
                top_k=top_k,
                confidence_config=(
                    confidence_config
                ),
                ambiguity_margin=(
                    ambiguity_margin
                ),
            )
            for text
            in texts
        ]


    # =========================================================================
    # MODEL INFORMATION
    # =========================================================================

    def get_model_info(
        self,
    ) -> dict[str, Any]:
        """
        Return useful model metadata.

        Both raw model classes and decoded legal labels
        are included for transparency.
        """

        raw_classes = [
            str(
                label
            )
            for label
            in self.model.classes_
        ]

        decoded_classes = [
            decode_clause_label(
                label
            )
            for label
            in self.model.classes_
        ]

        return {
            "model_type":
                type(
                    self.model
                ).__name__,

            "vectorizer_type":
                type(
                    self.vectorizer
                ).__name__,

            "number_of_classes":
                len(
                    self.model.classes_
                ),

            "raw_classes":
                raw_classes,

            "classes":
                decoded_classes,

            "supports_probability":
                hasattr(
                    self.model,
                    "predict_proba",
                ),

            "confidence_review_enabled":
                True,

            "label_decoding_enabled":
                True,
        }