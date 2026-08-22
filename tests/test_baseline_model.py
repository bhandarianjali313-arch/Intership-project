import numpy as np

from ml.src.classification.baseline_model import (
    create_classifier,
    create_vectorizer,
    fit_vectorizer,
    predict_with_confidence,
    train_classifier,
    transform_texts,
)


def get_training_data():

    texts = [
        "agreement governed by California law",
        "laws of New York shall govern",
        "licensee may audit books and records",
        "company may inspect financial records",
        "either party may terminate agreement",
        "customer may terminate upon notice",
    ]

    labels = np.array(
        [
            0,
            0,
            1,
            1,
            2,
            2,
        ]
    )

    return texts, labels


def test_vectorizer_creates_features():

    texts, _ = (
        get_training_data()
    )

    vectorizer = (
        create_vectorizer()
    )

    features = fit_vectorizer(
        vectorizer,
        texts,
    )

    assert (
        features.shape[0]
        == len(texts)
    )

    assert (
        features.shape[1]
        > 0
    )


def test_transform_does_not_refit():

    texts, _ = (
        get_training_data()
    )

    vectorizer = (
        create_vectorizer()
    )

    fit_vectorizer(
        vectorizer,
        texts,
    )

    vocabulary_before = (
        vectorizer.vocabulary_
        .copy()
    )

    transform_texts(
        vectorizer,
        [
            "completely unseen phrase"
        ],
    )

    assert (
        vectorizer.vocabulary_
        == vocabulary_before
    )


def test_classifier_training():

    texts, labels = (
        get_training_data()
    )

    vectorizer = (
        create_vectorizer()
    )

    features = fit_vectorizer(
        vectorizer,
        texts,
    )

    classifier = (
        create_classifier()
    )

    train_classifier(
        classifier,
        features,
        labels,
    )

    assert hasattr(
        classifier,
        "classes_",
    )

    assert len(
        classifier.classes_
    ) == 3


def test_prediction_length():

    texts, labels = (
        get_training_data()
    )

    vectorizer = (
        create_vectorizer()
    )

    features = fit_vectorizer(
        vectorizer,
        texts,
    )

    classifier = (
        create_classifier()
    )

    train_classifier(
        classifier,
        features,
        labels,
    )

    predictions, confidence = (
        predict_with_confidence(
            classifier,
            features,
        )
    )

    assert (
        len(predictions)
        == len(texts)
    )

    assert (
        len(confidence)
        == len(texts)
    )


def test_confidence_range():

    texts, labels = (
        get_training_data()
    )

    vectorizer = (
        create_vectorizer()
    )

    features = fit_vectorizer(
        vectorizer,
        texts,
    )

    classifier = (
        create_classifier()
    )

    train_classifier(
        classifier,
        features,
        labels,
    )

    _, confidence = (
        predict_with_confidence(
            classifier,
            features,
        )
    )

    assert np.all(
        confidence >= 0
    )

    assert np.all(
        confidence <= 1
    )