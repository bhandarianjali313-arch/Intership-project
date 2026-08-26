"""
Baseline clause classifier using TF-IDF + Logistic Regression.
"""
from typing import Protocol, Tuple

# pyright: reportMissingImports=false
import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from scipy.sparse import spmatrix


class ClassifierProtocol(Protocol):
    """Minimal sklearn-like classifier interface used by this module."""

    def fit(self, X, y, sample_weight=None) -> "ClassifierProtocol":
        ...

    def predict(self, X) -> np.ndarray:
        ...

    def predict_proba(self, X) -> np.ndarray:
        ...


def create_vectorizer() -> TfidfVectorizer:
    """Create the project's standard TF-IDF vectorizer."""
    return TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=10_000,
        min_df=1,
    )


def fit_vectorizer(
    vectorizer: TfidfVectorizer,
    texts,
) -> spmatrix:
    """Fit the vectorizer on training texts and return the feature matrix."""
    return vectorizer.fit_transform(texts)


def transform_texts(
    vectorizer: TfidfVectorizer,
    texts,
) -> spmatrix:
    """Transform unseen texts using an already-fit vectorizer (no refit)."""
    return vectorizer.transform(texts)


def create_classifier() -> ClassifierProtocol:
    """Create the project's standard classifier."""
    return LogisticRegression(max_iter=1000, random_state=42)


def train_classifier(
    classifier: ClassifierProtocol,
    features,
    labels,
) -> ClassifierProtocol:
    """Fit the classifier and return it."""
    classifier.fit(features, labels)
    return classifier


def predict_with_confidence(
    classifier: ClassifierProtocol,
    features,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Predict labels and return the maximum predicted probability for each row
    as a confidence score in [0, 1].
    """
    predictions = classifier.predict(features)

    if hasattr(classifier, "predict_proba"):
        proba = classifier.predict_proba(features)
        confidence = np.asarray(proba).max(axis=1)
    else:
        # Fallback: no probability available -> uniform confidence
        confidence = np.ones(predictions.shape[0], dtype=float)

    return predictions, confidence
