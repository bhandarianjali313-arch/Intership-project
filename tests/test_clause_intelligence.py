import pytest

from ml.src.intelligence.clause_intelligence import (
    ClauseIntelligenceAnalyzer,
)


class FakeEntityExtractor:

    def extract_entities(
        self,
        text,
    ):

        entities = []

        if "Microsoft" in text:

            entities.append(
                {
                    "text":
                        "Microsoft",

                    "label":
                        "ORG",
                }
            )

        if "New York" in text:

            entities.append(
                {
                    "text":
                        "New York",

                    "label":
                        "GPE",
                }
            )

        if "January 15, 2025" in text:

            entities.append(
                {
                    "text":
                        "January 15, 2025",

                    "label":
                        "DATE",
                }
            )

        return entities


def build_analyzer():

    return ClauseIntelligenceAnalyzer(
        entity_extractor=(
            FakeEntityExtractor()
        )
    )


def test_extract_entities():

    analyzer = build_analyzer()

    entities = (
        analyzer.extract_entities(
            (
                "Microsoft signed the "
                "agreement in New York."
            )
        )
    )

    assert len(entities) == 2

    assert (
        entities[0]["label"]
        == "ORG"
    )


def test_no_entities():

    analyzer = build_analyzer()

    entities = (
        analyzer.extract_entities(
            "This clause has no named entity."
        )
    )

    assert entities == []


def test_empty_text():

    analyzer = build_analyzer()

    with pytest.raises(
        ValueError
    ):
        analyzer.extract_entities(
            "   "
        )


def test_enrich_clause():

    analyzer = build_analyzer()

    clause = {
        "clause_text":
            (
                "Microsoft signed the "
                "agreement in New York."
            ),

        "predicted_label":
            "PARTIES",

        "risk_level":
            "LOW",
    }

    result = (
        analyzer.enrich_clause(
            clause
        )
    )

    assert (
        result["entity_count"]
        == 2
    )

    assert (
        result[
            "entity_type_distribution"
        ][
            "ORG"
        ]
        == 1
    )

    assert (
        result[
            "predicted_label"
        ]
        == "PARTIES"
    )


def test_missing_clause_text():

    analyzer = build_analyzer()

    with pytest.raises(
        ValueError
    ):
        analyzer.enrich_clause(
            {
                "risk_level":
                    "LOW"
            }
        )


def test_multiple_clause_enrichment():

    analyzer = build_analyzer()

    clauses = [
        {
            "clause_text":
                "Microsoft signed the agreement."
        },

        {
            "clause_text":
                "The agreement is governed in New York."
        },
    ]

    results = (
        analyzer.enrich_clauses(
            clauses
        )
    )

    assert len(results) == 2

    assert (
        results[0]["entity_count"]
        == 1
    )

    assert (
        results[1]["entity_count"]
        == 1
    )


def test_entity_summary():

    analyzer = build_analyzer()

    clauses = [
        analyzer.enrich_clause(
            {
                "clause_text":
                    (
                        "Microsoft signed the "
                        "agreement in New York."
                    )
            }
        ),

        analyzer.enrich_clause(
            {
                "clause_text":
                    (
                        "Microsoft executed it "
                        "on January 15, 2025."
                    )
            }
        ),
    ]

    summary = (
        analyzer.summarize_entities(
            clauses
        )
    )

    assert (
        summary["total_entities"]
        == 4
    )

    assert (
        summary["unique_entities"]
        == 3
    )

    assert (
        summary[
            "entity_type_distribution"
        ][
            "ORG"
        ]
        == 2
    )


def test_enrich_report():

    analyzer = build_analyzer()

    report = {
        "contract_id":
            "contract_001",

        "analyzed_clauses": [
            {
                "clause_text":
                    (
                        "Microsoft signed the "
                        "agreement in New York."
                    ),

                "predicted_label":
                    "PARTIES",
            }
        ],
    }

    result = (
        analyzer.enrich_report(
            report
        )
    )

    assert (
        result["contract_id"]
        == "contract_001"
    )

    assert (
        result[
            "entity_summary"
        ][
            "total_entities"
        ]
        == 2
    )


def test_missing_analyzed_clauses():

    analyzer = build_analyzer()

    with pytest.raises(
        ValueError
    ):
        analyzer.enrich_report(
            {
                "contract_id":
                    "test"
            }
        )


def test_missing_extractor():

    with pytest.raises(
        ValueError
    ):
        ClauseIntelligenceAnalyzer(
            entity_extractor=None
        )