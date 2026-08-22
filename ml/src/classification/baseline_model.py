from __future__ import annotations

import numpy as np
from scipy.sparse import spmatrix

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


def create_vectorizer() -> TfidfVectorizer:
    """
    Create TF-IDF vectorizer for legal clause text.

    We use both unigrams and bigrams so phrases such as
    'governing law' and 'audit rights' can be represented.
    """

    return TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.98,
        max_features=50000,
        sublinear_tf=True,
        strip_accents="unicode",
    )


def create_classifier() -> LogisticRegression:
    """
    Create multiclass Logistic Regression baseline.

    class_weight='balanced' helps compensate for the
    strong class imbalance observed in Day 9.
    """

    return LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        solver="lbfgs",
        random_state=42,
    )


def fit_vectorizer(
    vectorizer: TfidfVectorizer,
    train_texts,
) -> spmatrix:
    """
    Fit TF-IDF ONLY on training text.

    Validation and test text must never be used to fit
    the vocabulary or IDF statistics.
    """

    return vectorizer.fit_transform(
        train_texts
    )


def transform_texts(
    vectorizer: TfidfVectorizer,
    texts,
) -> spmatrix:

    return vectorizer.transform(
        texts
    )


def train_classifier(
    classifier: LogisticRegression,
    features: spmatrix,
    labels,
) -> LogisticRegression:

    classifier.fit(
        features,
        labels,
    )

    return classifier


def predict_with_confidence(
    classifier: LogisticRegression,
    features: spmatrix,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Return predicted class IDs and maximum probability.
    """

    probabilities = (
        classifier.predict_proba(
            features
        )
    )

    predictions = (
        classifier.classes_[
            np.argmax(
                probabilities,
                axis=1,
            )
        ]
    )

    confidence = np.max(
        probabilities,
        axis=1,
    )

    return (
        predictions,
        confidence,
    )