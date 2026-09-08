import pytest

from ml.src.risk.risk_scorer import (
    ContractRiskScorer,
    RiskLevel,
)


def test_high_risk_clause():

    scorer = ContractRiskScorer()

    result = scorer.score_clause(
        "UNCAPPED_LIABILITY",
        confidence=0.90,
    )

    assert result[
        "risk_level"
    ] == "HIGH"

    assert result[
        "risk_score"
    ] == 3


def test_medium_risk_clause():

    scorer = ContractRiskScorer()

    result = scorer.score_clause(
        "ANTI_ASSIGNMENT",
        confidence=0.80,
    )

    assert result[
        "risk_level"
    ] == "MEDIUM"

    assert result[
        "risk_score"
    ] == 2


def test_low_risk_clause():

    scorer = ContractRiskScorer()

    result = scorer.score_clause(
        "GOVERNING_LAW",
        confidence=0.90,
    )

    assert result[
        "risk_level"
    ] == "LOW"

    assert result[
        "risk_score"
    ] == 1


def test_unknown_clause_defaults_to_medium():

    scorer = ContractRiskScorer()

    result = scorer.score_clause(
        "UNKNOWN_CLAUSE"
    )

    assert result[
        "risk_level"
    ] == "MEDIUM"


def test_low_confidence_requires_review():

    scorer = ContractRiskScorer()

    result = scorer.score_clause(
        "GOVERNING_LAW",
        confidence=0.30,
    )

    assert result[
        "requires_human_review"
    ] is True


def test_low_confidence_does_not_change_risk():

    scorer = ContractRiskScorer()

    result = scorer.score_clause(
        "GOVERNING_LAW",
        confidence=0.20,
    )

    assert result[
        "risk_level"
    ] == "LOW"

    assert result[
        "requires_human_review"
    ] is True


def test_invalid_confidence():

    scorer = ContractRiskScorer()

    with pytest.raises(
        ValueError
    ):
        scorer.score_clause(
            "GOVERNING_LAW",
            confidence=1.5,
        )


def test_empty_label():

    scorer = ContractRiskScorer()

    with pytest.raises(
        ValueError
    ):
        scorer.score_clause(
            "   "
        )


def test_score_prediction():

    scorer = ContractRiskScorer()

    prediction = {
        "predicted_label":
            "UNCAPPED_LIABILITY",

        "confidence":
            0.85,

        "requires_human_review":
            False,
    }

    result = (
        scorer.score_prediction(
            prediction
        )
    )

    assert result[
        "risk_level"
    ] == "HIGH"

    assert result[
        "predicted_label"
    ] == "UNCAPPED_LIABILITY"


def test_contract_summary():

    scorer = ContractRiskScorer()

    clauses = [
        scorer.score_clause(
            "GOVERNING_LAW",
            0.90,
        ),

        scorer.score_clause(
            "ANTI_ASSIGNMENT",
            0.80,
        ),

        scorer.score_clause(
            "UNCAPPED_LIABILITY",
            0.90,
        ),
    ]

    summary = (
        scorer.summarize_contract(
            clauses
        )
    )

    assert summary[
        "total_clauses"
    ] == 3

    assert summary[
        "low_risk_clauses"
    ] == 1

    assert summary[
        "medium_risk_clauses"
    ] == 1

    assert summary[
        "high_risk_clauses"
    ] == 1

    assert summary[
        "overall_risk_level"
    ] == "HIGH"


def test_custom_unknown_risk():

    scorer = ContractRiskScorer(
        unknown_clause_risk=(
            RiskLevel.LOW
        )
    )

    result = scorer.score_clause(
        "SOME_NEW_CLAUSE"
    )

    assert result[
        "risk_level"
    ] == "LOW"