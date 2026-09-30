import numpy as np

from ml.src.classification.inference import (
    ClauseClassifier,
)

from ml.src.classification.label_mapping import (
    CUAD_CLAUSE_LABELS,
    CUAD_ID_TO_LABEL,
    CUAD_LABEL_TO_ID,
    decode_clause_label,
    number_of_clause_labels,
)

from ml.src.risk.risk_scorer import (
    ContractRiskScorer,
)


# ============================================================================
# FAKE NUMERIC MODEL
# ============================================================================


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


class FakeNumericModel:

    # These match actual training behaviour:
    # the classifier was trained using label_id.
    classes_ = np.array(
        [
            13,
            22,
            35,
        ]
    )

    def predict_proba(
        self,
        features,
    ):

        return np.array(
            [
                [
                    0.05,
                    0.90,
                    0.05,
                ]
                for _ in range(
                    len(features)
                )
            ]
        )


def build_numeric_classifier():

    classifier = (
        ClauseClassifier.__new__(
            ClauseClassifier
        )
    )

    classifier.vectorizer = (
        FakeVectorizer()
    )

    classifier.model = (
        FakeNumericModel()
    )

    return classifier


# ============================================================================
# MAPPING TESTS
# ============================================================================


def test_number_of_labels():

    assert (
        number_of_clause_labels()
        == 41
    )

    assert (
        len(
            CUAD_CLAUSE_LABELS
        )
        == 41
    )


def test_mapping_is_bidirectional():

    for (
        label_id,
        label,
    ) in CUAD_ID_TO_LABEL.items():

        assert (
            CUAD_LABEL_TO_ID[
                label
            ]
            == label_id
        )


def test_decode_integer_label():

    assert (
        decode_clause_label(
            13
        )
        == "GOVERNING_LAW"
    )


def test_decode_numeric_string():

    assert (
        decode_clause_label(
            "22"
        )
        == "NON_COMPETE"
    )


def test_semantic_label_unchanged():

    assert (
        decode_clause_label(
            "CAP_ON_LIABILITY"
        )
        == "CAP_ON_LIABILITY"
    )


def test_unknown_numeric_label_preserved():

    assert (
        decode_clause_label(
            999
        )
        == "999"
    )


# ============================================================================
# INFERENCE TESTS
# ============================================================================


def test_numeric_model_returns_semantic_label():

    classifier = (
        build_numeric_classifier()
    )

    result = classifier.predict(
        (
            "The employee shall not compete "
            "with the company."
        )
    )

    assert (
        result[
            "predicted_label"
        ]
        == "NON_COMPETE"
    )


def test_top_predictions_are_decoded():

    classifier = (
        build_numeric_classifier()
    )

    result = classifier.predict(
        "Example contract clause.",
        top_k=3,
    )

    labels = [
        item["label"]
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
        "TERMINATION_FOR_CONVENIENCE"
        in labels
    )


def test_decoded_label_reaches_risk_scorer():

    classifier = (
        build_numeric_classifier()
    )

    prediction = (
        classifier.predict_with_review(
            (
                "The employee shall not compete "
                "with the company."
            )
        )
    )

    scorer = (
        ContractRiskScorer()
    )

    scored = (
        scorer.score_prediction(
            prediction
        )
    )

    assert (
        scored[
            "clause_label"
        ]
        == "NON_COMPETE"
    )

    assert (
        scored[
            "risk_level"
        ]
        == "HIGH"
    )

    assert (
        scored[
            "risk_score"
        ]
        == 3
    )


def test_model_info_uses_semantic_labels():

    classifier = (
        build_numeric_classifier()
    )

    info = (
        classifier.get_model_info()
    )

    assert (
        info[
            "classes"
        ]
        == [
            "GOVERNING_LAW",
            "NON_COMPETE",
            "TERMINATION_FOR_CONVENIENCE",
        ]
    )

    assert (
        info[
            "semantic_label_decoding"
        ]
        is True
    )