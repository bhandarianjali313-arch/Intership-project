from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np


class ClauseClassifier:
    """
    Reusable inference service for the selected
    TF-IDF + Logistic Regression clause classifier.

    The classifier loads model artifacts once and can
    then make repeated predictions efficiently.
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


    def _validate_paths(self) -> None:
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


    def _load_artifacts(self) -> None:
        """
        Load serialized model artifacts.
        """

        self.vectorizer = joblib.load(
            self.vectorizer_path
        )

        self.model = joblib.load(
            self.model_path
        )


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

        cleaned_text = (
            " ".join(
                text.split()
            )
        )

        if not cleaned_text:
            raise ValueError(
                "Clause text cannot be empty."
            )

        return cleaned_text


    def predict(
        self,
        text: str,
        top_k: int = 3,
    ) -> dict[str, Any]:
        """
        Predict the most likely clause category.

        Returns:
            predicted_label
            confidence
            top_predictions
        """

        cleaned_text = (
            self._validate_text(
                text
            )
        )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than 0."
            )

        features = (
            self.vectorizer.transform(
                [cleaned_text]
            )
        )

        probabilities = (
            self.model.predict_proba(
                features
            )[0]
        )

        classes = np.asarray(
            self.model.classes_
        )

        top_k = min(
            top_k,
            len(classes),
        )

        ranked_indices = (
            np.argsort(
                probabilities
            )[::-1][:top_k]
        )

        top_predictions = []

        for rank, index in enumerate(
            ranked_indices,
            start=1,
        ):

            top_predictions.append(
                {
                    "rank": rank,

                    "label": str(
                        classes[index]
                    ),

                    "confidence": float(
                        probabilities[index]
                    ),
                }
            )

        best = top_predictions[0]

        return {
            "text": cleaned_text,

            "predicted_label":
                best["label"],

            "confidence":
                best["confidence"],

            "top_predictions":
                top_predictions,
        }


    def predict_batch(
        self,
        texts: list[str],
        top_k: int = 3,
    ) -> list[dict[str, Any]]:
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

        return [
            self.predict(
                text,
                top_k=top_k,
            )
            for text in texts
        ]


    def get_model_info(
        self,
    ) -> dict[str, Any]:
        """
        Return basic model metadata useful for
        API responses and debugging.
        """

        return {
            "model_type":
                type(self.model).__name__,

            "vectorizer_type":
                type(
                    self.vectorizer
                ).__name__,

            "number_of_classes":
                len(
                    self.model.classes_
                ),

            "classes":
                [
                    str(label)
                    for label
                    in self.model.classes_
                ],
        }