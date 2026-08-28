import pytest

from ml.src.classification.confidence import (
    ConfidenceConfig,
    assess_confidence,
    assess_prediction,
    prediction_margin,
)


def test_high_confidence():

    result = assess_confidence(
        0.85
    )

    assert (
        result[
            "confidence_level"
        ]
        == "HIGH"
    )

    assert (
        result[
            "recommended_action"
        ]
        == "ACCEPT"
    )

    assert (
        result[
            "requires_human_review"
        ]
        is False
    )


def test_medium_confidence():

    result = assess_confidence(
        0.55
    )

    assert (
        result[
            "confidence_level"
        ]
        == "MEDIUM"
    )

    assert (
        result[
            "requires_human_review"
        ]
        is True
    )


def test_low_confidence():

    result = assess_confidence(
        0.20
    )

    assert (
        result[
            "confidence_level"
        ]
        == "LOW"
    )

    assert (
        result[
            "recommended_action"
        ]
        == "HUMAN_REVIEW_REQUIRED"
    )


def test_threshold_boundaries():

    assert (
        assess_confidence(
            0.70
        )[
            "confidence_level"
        ]
        == "HIGH"
    )

    assert (
        assess_confidence(
            0.45
        )[
            "confidence_level"
        ]
        == "MEDIUM"
    )


def test_invalid_confidence():

    with pytest.raises(
        ValueError
    ):
        assess_confidence(
            1.5
        )


def test_invalid_thresholds():

    with pytest.raises(
        ValueError
    ):
        ConfidenceConfig(
            medium_threshold=0.8,
            high_threshold=0.7,
        )


def test_prediction_margin():

    predictions = [
        {
            "confidence": 0.70
        },
        {
            "confidence": 0.55
        },
    ]

    margin = prediction_margin(
        predictions
    )

    assert margin == pytest.approx(
        0.15
    )


def test_prediction_margin_missing_second_class():

    predictions = [
        {
            "confidence": 0.80
        }
    ]

    assert (
        prediction_margin(
            predictions
        )
        is None
    )


def test_ambiguous_prediction_requires_review():

    prediction = {
        "predicted_label":
            "CAP_ON_LIABILITY",

        "confidence":
            0.80,

        "top_predictions": [
            {
                "label":
                    "CAP_ON_LIABILITY",
                "confidence":
                    0.80,
            },
            {
                "label":
                    "UNCAPPED_LIABILITY",
                "confidence":
                    0.75,
            },
        ],
    }

    result = assess_prediction(
        prediction
    )

    assert (
        result[
            "ambiguous_prediction"
        ]
        is True
    )

    assert (
        result[
            "requires_human_review"
        ]
        is True
    )

    assert (
        result[
            "recommended_action"
        ]
        == "REVIEW_RECOMMENDED"
    )


def test_clear_high_confidence_prediction():

    prediction = {
        "predicted_label":
            "GOVERNING_LAW",

        "confidence":
            0.90,

        "top_predictions": [
            {
                "label":
                    "GOVERNING_LAW",
                "confidence":
                    0.90,
            },
            {
                "label":
                    "AGREEMENT_DATE",
                "confidence":
                    0.03,
            },
        ],
    }

    result = assess_prediction(
        prediction
    )

    assert (
        result[
            "ambiguous_prediction"
        ]
        is False
    )

    assert (
        result[
            "requires_human_review"
        ]
        is False
    )