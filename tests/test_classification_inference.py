import numpy as np
import pytest

from ml.src.classification.inference import (
    ClauseClassifier,
)


class FakeVectorizer:

    def transform(
        self,
        texts,
    ):
        return np.array(
            [
                [1.0, 0.0]
                for _ in texts
            ]
        )


class FakeModel:

    classes_ = np.array(
        [
            "ANTI_ASSIGNMENT",
            "GOVERNING_LAW",
            "TERMINATION_FOR_CONVENIENCE",
        ]
    )

    def predict_proba(
        self,
        features,
    ):

        return np.array(
            [
                [
                    0.10,
                    0.75,
                    0.15,
                ]
                for _ in range(
                    len(features)
                )
            ]
        )


def build_fake_classifier():

    classifier = (
        ClauseClassifier.__new__(
            ClauseClassifier
        )
    )

    classifier.vectorizer = (
        FakeVectorizer()
    )

    classifier.model = (
        FakeModel()
    )

    return classifier


def test_prediction_returns_best_label():

    classifier = (
        build_fake_classifier()
    )

    result = classifier.predict(
        "This agreement shall be governed "
        "by the laws of New York."
    )

    assert (
        result[
            "predicted_label"
        ]
        == "GOVERNING_LAW"
    )


def test_prediction_confidence():

    classifier = (
        build_fake_classifier()
    )

    result = classifier.predict(
        "Test legal clause"
    )

    assert (
        result["confidence"]
        == pytest.approx(
            0.75
        )
    )


def test_top_k_predictions():

    classifier = (
        build_fake_classifier()
    )

    result = classifier.predict(
        "Test clause",
        top_k=2,
    )

    assert len(
        result[
            "top_predictions"
        ]
    ) == 2

    assert (
        result[
            "top_predictions"
        ][0]["confidence"]
        >=
        result[
            "top_predictions"
        ][1]["confidence"]
    )


def test_top_k_larger_than_classes():

    classifier = (
        build_fake_classifier()
    )

    result = classifier.predict(
        "Test clause",
        top_k=100,
    )

    assert len(
        result[
            "top_predictions"
        ]
    ) == 3


def test_empty_text_rejected():

    classifier = (
        build_fake_classifier()
    )

    with pytest.raises(
        ValueError
    ):
        classifier.predict(
            "     "
        )


def test_non_string_rejected():

    classifier = (
        build_fake_classifier()
    )

    with pytest.raises(
        TypeError
    ):
        classifier.predict(
            123
        )


def test_invalid_top_k_rejected():

    classifier = (
        build_fake_classifier()
    )

    with pytest.raises(
        ValueError
    ):
        classifier.predict(
            "Test clause",
            top_k=0,
        )


def test_batch_prediction():

    classifier = (
        build_fake_classifier()
    )

    results = (
        classifier.predict_batch(
            [
                "Clause one",
                "Clause two",
            ]
        )
    )

    assert len(
        results
    ) == 2


def test_model_info():

    classifier = (
        build_fake_classifier()
    )

    info = (
        classifier.get_model_info()
    )

    assert (
        info[
            "number_of_classes"
        ]
        == 3
    )