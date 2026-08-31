from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)


class PipelineEvaluator:
    """
    Evaluate confidence-aware clause classification.

    The evaluator measures:
    - overall classification performance
    - confidence-level performance
    - human-review behaviour
    - per-class performance
    - common classification errors
    """

    REQUIRED_FIELDS = {
        "true_label",
        "predicted_label",
        "confidence",
        "confidence_level",
        "requires_human_review",
    }

    @classmethod
    def _validate_predictions(
        cls,
        predictions: list[dict[str, Any]],
    ) -> None:

        if not isinstance(predictions, list):
            raise TypeError(
                "predictions must be a list."
            )

        if not predictions:
            raise ValueError(
                "predictions cannot be empty."
            )

        for index, prediction in enumerate(
            predictions
        ):

            if not isinstance(
                prediction,
                dict,
            ):
                raise TypeError(
                    f"Prediction {index} must be a dictionary."
                )

            missing = (
                cls.REQUIRED_FIELDS
                - set(prediction)
            )

            if missing:
                raise ValueError(
                    f"Prediction {index} is missing "
                    f"fields: {sorted(missing)}"
                )

    @staticmethod
    def _safe_accuracy(
        records: list[dict[str, Any]],
    ) -> float | None:

        if not records:
            return None

        correct = sum(
            record["true_label"]
            == record["predicted_label"]
            for record in records
        )

        return round(
            correct / len(records),
            6,
        )

    def overall_metrics(
        self,
        predictions: list[dict[str, Any]],
    ) -> dict[str, float]:

        self._validate_predictions(
            predictions
        )

        y_true = [
            item["true_label"]
            for item in predictions
        ]

        y_pred = [
            item["predicted_label"]
            for item in predictions
        ]

        return {
            "accuracy": round(
                accuracy_score(
                    y_true,
                    y_pred,
                ),
                6,
            ),

            "macro_precision": round(
                precision_score(
                    y_true,
                    y_pred,
                    average="macro",
                    zero_division=0,
                ),
                6,
            ),

            "macro_recall": round(
                recall_score(
                    y_true,
                    y_pred,
                    average="macro",
                    zero_division=0,
                ),
                6,
            ),

            "macro_f1": round(
                f1_score(
                    y_true,
                    y_pred,
                    average="macro",
                    zero_division=0,
                ),
                6,
            ),

            "weighted_f1": round(
                f1_score(
                    y_true,
                    y_pred,
                    average="weighted",
                    zero_division=0,
                ),
                6,
            ),
        }

    def confidence_metrics(
        self,
        predictions: list[dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:

        self._validate_predictions(
            predictions
        )

        grouped = defaultdict(list)

        for prediction in predictions:

            grouped[
                prediction["confidence_level"]
            ].append(
                prediction
            )

        output = {}

        for level in [
            "HIGH",
            "MEDIUM",
            "LOW",
        ]:

            records = grouped.get(
                level,
                [],
            )

            output[level] = {
                "count":
                    len(records),

                "accuracy":
                    self._safe_accuracy(
                        records
                    ),
            }

        return output

    def review_metrics(
        self,
        predictions: list[dict[str, Any]],
    ) -> dict[str, Any]:

        self._validate_predictions(
            predictions
        )

        total = len(
            predictions
        )

        review_records = [
            item
            for item in predictions
            if item[
                "requires_human_review"
            ]
        ]

        accepted_records = [
            item
            for item in predictions
            if not item[
                "requires_human_review"
            ]
        ]

        return {
            "total_predictions":
                total,

            "review_count":
                len(review_records),

            "review_rate":
                round(
                    len(review_records)
                    / total,
                    6,
                ),

            "accepted_count":
                len(accepted_records),

            "accepted_rate":
                round(
                    len(accepted_records)
                    / total,
                    6,
                ),

            "accepted_accuracy":
                self._safe_accuracy(
                    accepted_records
                ),

            "review_group_accuracy":
                self._safe_accuracy(
                    review_records
                ),
        }

    def per_class_metrics(
        self,
        predictions: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        self._validate_predictions(
            predictions
        )

        labels = sorted(
            {
                item["true_label"]
                for item in predictions
            }
            |
            {
                item["predicted_label"]
                for item in predictions
            }
        )

        results = []

        for label in labels:

            true_positive = sum(
                item["true_label"] == label
                and item["predicted_label"] == label
                for item in predictions
            )

            false_positive = sum(
                item["true_label"] != label
                and item["predicted_label"] == label
                for item in predictions
            )

            false_negative = sum(
                item["true_label"] == label
                and item["predicted_label"] != label
                for item in predictions
            )

            support = sum(
                item["true_label"] == label
                for item in predictions
            )

            precision_denominator = (
                true_positive
                + false_positive
            )

            recall_denominator = (
                true_positive
                + false_negative
            )

            precision = (
                true_positive
                / precision_denominator
                if precision_denominator
                else 0.0
            )

            recall = (
                true_positive
                / recall_denominator
                if recall_denominator
                else 0.0
            )

            if precision + recall:

                f1 = (
                    2
                    * precision
                    * recall
                    / (
                        precision
                        + recall
                    )
                )

            else:
                f1 = 0.0

            results.append(
                {
                    "label":
                        label,

                    "support":
                        support,

                    "precision":
                        round(
                            precision,
                            6,
                        ),

                    "recall":
                        round(
                            recall,
                            6,
                        ),

                    "f1":
                        round(
                            f1,
                            6,
                        ),
                }
            )

        return results

    def confusion_pairs(
        self,
        predictions: list[dict[str, Any]],
        limit: int = 10,
    ) -> list[dict[str, Any]]:

        self._validate_predictions(
            predictions
        )

        errors = Counter(
            (
                item["true_label"],
                item["predicted_label"],
            )
            for item in predictions
            if (
                item["true_label"]
                != item["predicted_label"]
            )
        )

        return [
            {
                "true_label":
                    true_label,

                "predicted_label":
                    predicted_label,

                "count":
                    count,
            }
            for (
                true_label,
                predicted_label,
            ), count
            in errors.most_common(
                limit
            )
        ]

    def high_confidence_errors(
        self,
        predictions: list[dict[str, Any]],
        limit: int = 20,
    ) -> list[dict[str, Any]]:

        self._validate_predictions(
            predictions
        )

        errors = [
            item
            for item in predictions
            if (
                item["true_label"]
                != item["predicted_label"]
                and item["confidence_level"]
                == "HIGH"
            )
        ]

        errors.sort(
            key=lambda item: float(
                item["confidence"]
            ),
            reverse=True,
        )

        return errors[:limit]

    def evaluate(
        self,
        predictions: list[dict[str, Any]],
    ) -> dict[str, Any]:

        self._validate_predictions(
            predictions
        )

        per_class = (
            self.per_class_metrics(
                predictions
            )
        )

        worst_classes = sorted(
            per_class,
            key=lambda item: (
                item["f1"],
                item["support"],
            ),
        )[:10]

        return {
            "overall_metrics":
                self.overall_metrics(
                    predictions
                ),

            "confidence_metrics":
                self.confidence_metrics(
                    predictions
                ),

            "review_metrics":
                self.review_metrics(
                    predictions
                ),

            "worst_classes":
                worst_classes,

            "top_confusion_pairs":
                self.confusion_pairs(
                    predictions
                ),

            "high_confidence_errors":
                self.high_confidence_errors(
                    predictions
                ),
        }