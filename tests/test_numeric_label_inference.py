import numpy as np

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
                [
                    1.0,
                    0.0,
                ]
                for _ in texts
            ]
        )


class NumericClassModel:

    # Simulates the class representation used by a
    # model trained with integer-encoded labels.
    classes_ = np.array(
        [
            3,
            13,
            22,
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
                    0.15,
                    0.75,
                ]
                for _ in range(
                    len(
                        features
                    )
                )
            ]
        )


def build_classifier():

    classifier = (
        ClauseClassifier.__new__(
            ClauseClassifier
        )
    )

    classifier.vectorizer = (
        FakeVectorizer()
    )

    classifier.model = (
        NumericClassModel()
    )

    return classifier


def test_numeric_class_is_decoded():

    classifier = (
        build_classifier()
    )

    result = classifier.predict(
        (
            "The employee shall not "
            "compete with the company."
        )
    )

    assert (
        result[
            "raw_predicted_label"
        ]
        == "22"
    )

    assert (
        result[
            "predicted_label"
        ]
        == "NON_COMPETE"
    )


def test_all_top_predictions_are_decoded():

    classifier = (
        build_classifier()
    )

    result = classifier.predict(
        "Sample legal clause",
        top_k=3,
    )

    labels = [
        item[
            "label"
        ]
        for item
        in result[
            "top_predictions"
        ]
    ]

    assert (
        "NON_COMPETE"
        in labels
    )

    assert (
        "GOVERNING_LAW"
        in labels
    )

    assert (
        "ANTI_ASSIGNMENT"
        in labels
    )


def test_model_info_decodes_classes():

    classifier = (
        build_classifier()
    )

    info = (
        classifier.get_model_info()
    )

    assert (
        info[
            "raw_classes"
        ]
        == [
            "3",
            "13",
            "22",
        ]
    )

    assert (
        info[
            "classes"
        ]
        == [
            "ANTI_ASSIGNMENT",
            "GOVERNING_LAW",
            "NON_COMPETE",
        ]
    )

    assert (
        info[
            "label_decoding_enabled"
        ]
        is True
    )