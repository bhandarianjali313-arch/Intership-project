import pytest

from ml.src.evaluation.pipeline_evaluator import (
    PipelineEvaluator,
)


def record(
    true_label,
    predicted_label,
    confidence,
    confidence_level,
    review,
):

    return {
        "true_label":
            true_label,

        "predicted_label":
            predicted_label,

        "confidence":
            confidence,

        "confidence_level":
            confidence_level,

        "requires_human_review":
            review,
    }


def sample_predictions():

    return [
        record(
            "A",
            "A",
            0.90,
            "HIGH",
            False,
        ),

        record(
            "A",
            "A",
            0.80,
            "HIGH",
            False,
        ),

        record(
            "B",
            "B",
            0.60,
            "MEDIUM",
            True,
        ),

        record(
            "B",
            "A",
            0.30,
            "LOW",
            True,
        ),
    ]


def test_overall_accuracy():

    evaluator = (
        PipelineEvaluator()
    )

    metrics = evaluator.overall_metrics(
        sample_predictions()
    )

    assert (
        metrics["accuracy"]
        == 0.75
    )


def test_high_confidence_accuracy():

    evaluator = (
        PipelineEvaluator()
    )

    metrics = evaluator.confidence_metrics(
        sample_predictions()
    )

    assert (
        metrics["HIGH"]["count"]
        == 2
    )

    assert (
        metrics["HIGH"]["accuracy"]
        == 1.0
    )


def test_low_confidence_accuracy():

    evaluator = (
        PipelineEvaluator()
    )

    metrics = evaluator.confidence_metrics(
        sample_predictions()
    )

    assert (
        metrics["LOW"]["accuracy"]
        == 0.0
    )


def test_review_rate():

    evaluator = (
        PipelineEvaluator()
    )

    metrics = evaluator.review_metrics(
        sample_predictions()
    )

    assert (
        metrics["review_count"]
        == 2
    )

    assert (
        metrics["review_rate"]
        == 0.5
    )


def test_accepted_accuracy():

    evaluator = (
        PipelineEvaluator()
    )

    metrics = evaluator.review_metrics(
        sample_predictions()
    )

    assert (
        metrics["accepted_accuracy"]
        == 1.0
    )


def test_confusion_pairs():

    evaluator = (
        PipelineEvaluator()
    )

    pairs = evaluator.confusion_pairs(
        sample_predictions()
    )

    assert len(pairs) == 1

    assert (
        pairs[0]["true_label"]
        == "B"
    )

    assert (
        pairs[0]["predicted_label"]
        == "A"
    )

    assert (
        pairs[0]["count"]
        == 1
    )


def test_per_class_metrics():

    evaluator = (
        PipelineEvaluator()
    )

    metrics = evaluator.per_class_metrics(
        sample_predictions()
    )

    labels = {
        item["label"]
        for item in metrics
    }

    assert labels == {
        "A",
        "B",
    }


def test_empty_predictions():

    evaluator = (
        PipelineEvaluator()
    )

    with pytest.raises(
        ValueError
    ):
        evaluator.evaluate(
            []
        )


def test_missing_fields():

    evaluator = (
        PipelineEvaluator()
    )

    with pytest.raises(
        ValueError
    ):
        evaluator.evaluate(
            [
                {
                    "true_label":
                        "A"
                }
            ]
        )


def test_high_confidence_error_detection():

    evaluator = (
        PipelineEvaluator()
    )

    predictions = [
        record(
            "A",
            "B",
            0.95,
            "HIGH",
            False,
        )
    ]

    errors = (
        evaluator.high_confidence_errors(
            predictions
        )
    )

    assert len(errors) == 1

    assert (
        errors[0]["confidence"]
        == 0.95
    )