from __future__ import annotations

from dataclasses import dataclass
from typing import Any


DEFAULT_HIGH_THRESHOLD = 0.70
DEFAULT_MEDIUM_THRESHOLD = 0.45


@dataclass(frozen=True)
class ConfidenceConfig:
    """
    Threshold configuration for classification confidence.

    These thresholds are operational heuristics.
    They should not be interpreted as calibrated
    probabilities of legal correctness.
    """

    high_threshold: float = DEFAULT_HIGH_THRESHOLD
    medium_threshold: float = DEFAULT_MEDIUM_THRESHOLD

    def __post_init__(self) -> None:

        if not 0.0 <= self.medium_threshold <= 1.0:
            raise ValueError(
                "medium_threshold must be between 0 and 1."
            )

        if not 0.0 <= self.high_threshold <= 1.0:
            raise ValueError(
                "high_threshold must be between 0 and 1."
            )

        if self.medium_threshold >= self.high_threshold:
            raise ValueError(
                "medium_threshold must be smaller "
                "than high_threshold."
            )


def assess_confidence(
    confidence: float,
    config: ConfidenceConfig | None = None,
) -> dict[str, Any]:
    """
    Convert a model confidence score into an
    operational review recommendation.
    """

    if config is None:
        config = ConfidenceConfig()

    confidence = float(confidence)

    if not 0.0 <= confidence <= 1.0:
        raise ValueError(
            "confidence must be between 0 and 1."
        )

    if confidence >= config.high_threshold:

        level = "HIGH"
        action = "ACCEPT"
        requires_human_review = False

    elif confidence >= config.medium_threshold:

        level = "MEDIUM"
        action = "REVIEW_RECOMMENDED"
        requires_human_review = True

    else:

        level = "LOW"
        action = "HUMAN_REVIEW_REQUIRED"
        requires_human_review = True

    return {
        "confidence_level": level,
        "recommended_action": action,
        "requires_human_review": requires_human_review,
    }


def prediction_margin(
    top_predictions: list[dict],
) -> float | None:
    """
    Difference between the highest and second-highest
    class confidence.

    A small margin indicates that the classifier is
    uncertain between multiple clause categories.
    """

    if len(top_predictions) < 2:
        return None

    first = float(
        top_predictions[0]["confidence"]
    )

    second = float(
        top_predictions[1]["confidence"]
    )

    return first - second


def assess_prediction(
    prediction: dict,
    config: ConfidenceConfig | None = None,
    ambiguity_margin: float = 0.10,
) -> dict[str, Any]:
    """
    Add confidence and ambiguity information to a
    classifier prediction.
    """

    if ambiguity_margin < 0:
        raise ValueError(
            "ambiguity_margin cannot be negative."
        )

    confidence = float(
        prediction["confidence"]
    )

    assessment = assess_confidence(
        confidence,
        config=config,
    )

    margin = prediction_margin(
        prediction.get(
            "top_predictions",
            [],
        )
    )

    ambiguous = (
        margin is not None
        and margin < ambiguity_margin
    )

    # Even a reasonably confident prediction should
    # be reviewed if two classes are very close.
    if ambiguous:

        assessment[
            "requires_human_review"
        ] = True

        if (
            assessment["confidence_level"]
            == "HIGH"
        ):
            assessment[
                "recommended_action"
            ] = "REVIEW_RECOMMENDED"

    return {
        **prediction,
        **assessment,
        "prediction_margin": margin,
        "ambiguous_prediction": ambiguous,
    }