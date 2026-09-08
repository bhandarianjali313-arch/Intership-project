from __future__ import annotations

import json
from pathlib import Path

from ml.src.classification.inference import (
    ClauseClassifier,
)

from ml.src.intelligence.clause_intelligence import (
    ClauseIntelligenceAnalyzer,
)

from ml.src.ner.spacy_ner import (
    extract_entities,
    load_ner_model,
)

from ml.src.pipeline.contract_analyzer import (
    ContractAnalyzer,
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

MODEL_DIR = (
    PROJECT_ROOT
    / "models"
    / "classification"
)

VECTORIZER_PATH = (
    MODEL_DIR
    / "tfidf_vectorizer.joblib"
)

MODEL_PATH = (
    MODEL_DIR
    / "logistic_regression.joblib"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "intelligence"
)


SAMPLE_CONTRACT = """
1. Governing Law

This Agreement shall be governed by the laws
of the State of New York.

2. Parties

Microsoft Corporation entered into this Agreement
with Contoso Ltd. on January 15, 2025.

3. Assignment

Neither party may assign this Agreement without
the prior written consent of the other party.

4. Liability

The liability of the Company under this Agreement
shall be unlimited.

5. Termination

Either party may terminate this Agreement upon
thirty days prior written notice.
"""


class SpacyEntityExtractor:
    """
    Adapter around the existing function-based
    spaCy NER implementation.

    The spaCy model is loaded only once.
    """

    def __init__(self) -> None:

        self.nlp = load_ner_model()

    def extract_entities(
        self,
        text: str,
    ):

        return extract_entities(
            text=text,
            nlp=self.nlp,
        )


def main() -> None:

    print()
    print("=" * 80)
    print(
        "DAY 21 - CLAUSE + ENTITY INTELLIGENCE"
    )
    print("=" * 80)

    # ---------------------------------------------------------
    # Load clause classifier
    # ---------------------------------------------------------

    print(
        "\nLoading clause classifier..."
    )

    classifier = ClauseClassifier(
        vectorizer_path=VECTORIZER_PATH,
        model_path=MODEL_PATH,
    )

    # ---------------------------------------------------------
    # Build contract analyzer
    # ---------------------------------------------------------

    contract_analyzer = (
        ContractAnalyzer(
            classifier=classifier
        )
    )

    print(
        "\nRunning contract analysis..."
    )

    report = (
        contract_analyzer.analyze(
            contract_text=SAMPLE_CONTRACT,
            contract_id=(
                "day21_sample_contract"
            ),
        )
    )

    print(
        f"Clauses analyzed: "
        f"{len(report['analyzed_clauses'])}"
    )

    # ---------------------------------------------------------
    # Load NER once
    # ---------------------------------------------------------

    print(
        "\nLoading spaCy NER model..."
    )

    entity_extractor = (
        SpacyEntityExtractor()
    )

    intelligence = (
        ClauseIntelligenceAnalyzer(
            entity_extractor=(
                entity_extractor
            )
        )
    )

    # ---------------------------------------------------------
    # Enrich report
    # ---------------------------------------------------------

    print(
        "\nExtracting named entities..."
    )

    enriched_report = (
        intelligence.enrich_report(
            report
        )
    )

    # ---------------------------------------------------------
    # Print clause results
    # ---------------------------------------------------------

    for clause in enriched_report[
        "analyzed_clauses"
    ]:

        print()
        print("-" * 80)

        print(
            f"Clause "
            f"{clause['clause_index']}"
        )

        print("-" * 80)

        print(
            f"Text       : "
            f"{clause['clause_text']}"
        )

        print(
            f"Type       : "
            f"{clause['predicted_label']}"
        )

        print(
            f"Risk       : "
            f"{clause['risk_level']}"
        )

        print(
            f"Confidence : "
            f"{clause['confidence']:.4f}"
        )

        print(
            f"Review     : "
            f"{clause['requires_human_review']}"
        )

        print(
            f"Entities   : "
            f"{clause['entity_count']}"
        )

        if clause["entities"]:

            for entity in clause[
                "entities"
            ]:

                print(
                    f"  - "
                    f"{entity['text']} "
                    f"[{entity['label']}]"
                )

        else:

            print(
                "  No named entities found."
            )

    # ---------------------------------------------------------
    # Contract-level entity summary
    # ---------------------------------------------------------

    entity_summary = (
        enriched_report[
            "entity_summary"
        ]
    )

    print()
    print("=" * 80)
    print(
        "CONTRACT ENTITY SUMMARY"
    )
    print("=" * 80)

    print(
        f"Total entities  : "
        f"{entity_summary['total_entities']}"
    )

    print(
        f"Unique entities : "
        f"{entity_summary['unique_entities']}"
    )

    print(
        "\nEntity type distribution:"
    )

    for (
        entity_type,
        count,
    ) in sorted(
        entity_summary[
            "entity_type_distribution"
        ].items()
    ):

        print(
            f"  {entity_type:<20} "
            f"{count}"
        )

    # ---------------------------------------------------------
    # Save output
    # ---------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        OUTPUT_DIR
        / "day21_clause_intelligence.json"
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            enriched_report,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print("=" * 80)
    print(
        "DAY 21 COMPLETE"
    )
    print("=" * 80)

    print(
        f"\nOutput saved to:\n"
        f"{output_path}"
    )

    print(
        "\nNote: NER output is produced by a "
        "general-purpose spaCy baseline and may "
        "contain domain-specific extraction errors."
    )


if __name__ == "__main__":
    main()