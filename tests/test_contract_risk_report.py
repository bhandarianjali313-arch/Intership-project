import pytest

from ml.src.risk.contract_report import (
    ContractRiskReportGenerator,
)


def build_clause(
    label,
    risk_level,
    risk_score,
    confidence=0.80,
    review=False,
    ambiguous=False,
):

    return {
        "clause_label":
            label,

        "risk_level":
            risk_level,

        "risk_score":
            risk_score,

        "confidence":
            confidence,

        "requires_human_review":
            review,

        "ambiguous_prediction":
            ambiguous,

        "risk_reason":
            "Test reason",
    }


def test_report_counts():

    generator = (
        ContractRiskReportGenerator()
    )

    clauses = [
        build_clause(
            "GOVERNING_LAW",
            "LOW",
            1,
        ),

        build_clause(
            "ANTI_ASSIGNMENT",
            "MEDIUM",
            2,
        ),

        build_clause(
            "UNCAPPED_LIABILITY",
            "HIGH",
            3,
        ),
    ]

    report = generator.generate_report(
        clauses,
        contract_id="test_contract",
    )

    summary = report["summary"]

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


def test_high_clause_makes_overall_high():

    generator = (
        ContractRiskReportGenerator()
    )

    clauses = [
        build_clause(
            "GOVERNING_LAW",
            "LOW",
            1,
        ),

        build_clause(
            "UNCAPPED_LIABILITY",
            "HIGH",
            3,
        ),
    ]

    report = generator.generate_report(
        clauses
    )

    assert (
        report["summary"][
            "overall_risk_level"
        ]
        == "HIGH"
    )


def test_all_low_contract():

    generator = (
        ContractRiskReportGenerator()
    )

    clauses = [
        build_clause(
            "GOVERNING_LAW",
            "LOW",
            1,
        ),

        build_clause(
            "PARTIES",
            "LOW",
            1,
        ),
    ]

    report = generator.generate_report(
        clauses
    )

    assert (
        report["summary"][
            "risk_score_0_to_100"
        ]
        == 0.0
    )

    assert (
        report["summary"][
            "overall_risk_level"
        ]
        == "LOW"
    )


def test_all_high_contract():

    generator = (
        ContractRiskReportGenerator()
    )

    clauses = [
        build_clause(
            "UNCAPPED_LIABILITY",
            "HIGH",
            3,
        ),

        build_clause(
            "NON_COMPETE",
            "HIGH",
            3,
        ),
    ]

    report = generator.generate_report(
        clauses
    )

    assert (
        report["summary"][
            "risk_score_0_to_100"
        ]
        == 100.0
    )

    assert (
        report["summary"][
            "overall_risk_level"
        ]
        == "HIGH"
    )


def test_review_count():

    generator = (
        ContractRiskReportGenerator()
    )

    clauses = [
        build_clause(
            "GOVERNING_LAW",
            "LOW",
            1,
            review=True,
        ),

        build_clause(
            "PARTIES",
            "LOW",
            1,
            review=False,
        ),
    ]

    report = generator.generate_report(
        clauses
    )

    assert (
        report["summary"][
            "clauses_requiring_review"
        ]
        == 1
    )

    assert (
        report[
            "review_recommended"
        ]
        is True
    )


def test_ambiguous_count():

    generator = (
        ContractRiskReportGenerator()
    )

    clauses = [
        build_clause(
            "ANTI_ASSIGNMENT",
            "MEDIUM",
            2,
            ambiguous=True,
        ),

        build_clause(
            "PARTIES",
            "LOW",
            1,
        ),
    ]

    report = generator.generate_report(
        clauses
    )

    assert (
        report["summary"][
            "ambiguous_predictions"
        ]
        == 1
    )


def test_clause_distribution():

    generator = (
        ContractRiskReportGenerator()
    )

    clauses = [
        build_clause(
            "GOVERNING_LAW",
            "LOW",
            1,
        ),

        build_clause(
            "GOVERNING_LAW",
            "LOW",
            1,
        ),

        build_clause(
            "NON_COMPETE",
            "HIGH",
            3,
        ),
    ]

    report = generator.generate_report(
        clauses
    )

    assert (
        report[
            "clause_type_distribution"
        ][
            "GOVERNING_LAW"
        ]
        == 2
    )


def test_top_risky_clause():

    generator = (
        ContractRiskReportGenerator()
    )

    clauses = [
        build_clause(
            "PARTIES",
            "LOW",
            1,
        ),

        build_clause(
            "ANTI_ASSIGNMENT",
            "MEDIUM",
            2,
        ),

        build_clause(
            "UNCAPPED_LIABILITY",
            "HIGH",
            3,
        ),
    ]

    report = generator.generate_report(
        clauses
    )

    assert (
        report[
            "top_risky_clauses"
        ][0][
            "clause_label"
        ]
        == "UNCAPPED_LIABILITY"
    )


def test_empty_clause_list_rejected():

    generator = (
        ContractRiskReportGenerator()
    )

    with pytest.raises(
        ValueError
    ):
        generator.generate_report(
            []
        )


def test_missing_required_field():

    generator = (
        ContractRiskReportGenerator()
    )

    clauses = [
        {
            "clause_label":
                "GOVERNING_LAW"
        }
    ]

    with pytest.raises(
        ValueError
    ):
        generator.generate_report(
            clauses
        )


def test_invalid_risk_level():

    generator = (
        ContractRiskReportGenerator()
    )

    clauses = [
        build_clause(
            "TEST",
            "CRITICAL",
            5,
        )
    ]

    with pytest.raises(
        ValueError
    ):
        generator.generate_report(
            clauses
        )