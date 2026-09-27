import pytest

from backend.app.services.ml_contract_service import MLContractService


class FakeClassifier:
    """Fake classifier used to test backend/ML integration."""

    def predict_with_review(self, text, top_k=3):
        return {
            "text": text,
            "predicted_label": "NON_COMPETE",
            "confidence": 0.91,
            "confidence_level": "HIGH",
            "prediction_margin": 0.70,
            "ambiguous": False,
            "requires_human_review": False,
            "top_predictions": [
                {
                    "label": "NON_COMPETE",
                    "confidence": 0.91,
                },
                {
                    "label": "EXCLUSIVITY",
                    "confidence": 0.12,
                },
            ],
        }


class FakeRiskScorer:
    """Fake risk scorer used to isolate the integration service."""

    def score_prediction(self, prediction):
        return {
            **prediction,
            "risk_level": "HIGH",
            "risk_score": 3,
        }


def build_service():
    return MLContractService(
        classifier=FakeClassifier(),
        risk_scorer=FakeRiskScorer(),
    )


def test_analyze_clause():
    service = build_service()

    result = service.analyze_clause(
        "The employee shall not compete with the company."
    )

    assert result["classification"]["predicted_label"] == "NON_COMPETE"
    assert result["classification"]["confidence"] == 0.91
    assert result["risk"]["risk_level"] == "HIGH"
    assert result["risk"]["risk_score"] == 3


def test_review_flag():
    service = build_service()

    result = service.analyze_clause(
        "This is a valid contract clause."
    )

    assert (
        result["classification"]["requires_human_review"]
        is False
    )


def test_top_predictions():
    service = build_service()

    result = service.analyze_clause(
        "This is a valid contract clause."
    )

    assert len(
        result["classification"]["top_predictions"]
    ) == 2


def test_empty_clause():
    service = build_service()

    with pytest.raises(ValueError):
        service.analyze_clause("   ")


def test_invalid_clause_type():
    service = build_service()

    with pytest.raises(TypeError):
        service.analyze_clause(123)


def test_batch_analysis():
    service = build_service()

    results = service.analyze_clauses(
        [
            "The employee shall not compete with the company.",
            "Neither party may assign this agreement.",
        ]
    )

    assert len(results) == 2


def test_empty_batch():
    service = build_service()

    with pytest.raises(ValueError):
        service.analyze_clauses([])


def test_invalid_batch():
    service = build_service()

    with pytest.raises(TypeError):
        service.analyze_clauses("not-a-list")