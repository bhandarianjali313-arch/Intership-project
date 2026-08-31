from __future__ import annotations

import json
from pathlib import Path

from ml.src.classification.inference import (
    ClauseClassifier,
)

from ml.src.pipeline.contract_analyzer import (
    ContractAnalyzer,
)

from ml.src.validation.contract_validator import (
    ContractValidator,
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
    / "validation"
)


SAMPLE_CONTRACT = """
1. Governing Law

This Agreement shall be governed by and construed
in accordance with the laws of the State of New York.

2. Assignment

Neither party may assign this Agreement without
the prior written consent of the other party.

3. Assignment Duplicate

Neither party may assign this Agreement without
the prior written consent of the other party.

4. Liability

The liability of the Company under this Agreement
shall be unlimited.

5. Termination

Either party may terminate this Agreement for
convenience upon thirty days prior written notice.
"""


def main() -> None:

    print()
    print("=" * 80)
    print(
        "DAY 22 - CONTRACT PIPELINE VALIDATION"
    )
    print("=" * 80)

    validator = ContractValidator()

    print(
        "\n1. Validating raw contract..."
    )

    contract_validation = (
        validator.validate_contract_text(
            SAMPLE_CONTRACT
        )
    )

    print(
        f"Characters : "
        f"{contract_validation['character_count']}"
    )

    print(
        f"Words      : "
        f"{contract_validation['word_count']}"
    )

    print(
        f"Warnings   : "
        f"{len(contract_validation['warnings'])}"
    )

    print(
        "\n2. Loading classifier..."
    )

    classifier = ClauseClassifier(
        vectorizer_path=VECTORIZER_PATH,
        model_path=MODEL_PATH,
    )

    analyzer = ContractAnalyzer(
        classifier=classifier
    )

    print(
        "\n3. Segmenting contract..."
    )

    clauses = analyzer.split_into_clauses(
        contract_validation[
            "cleaned_text"
        ]
    )

    print(
        f"Candidate clauses: "
        f"{len(clauses)}"
    )

    print(
        "\n4. Validating clauses..."
    )

    clause_validation = (
        validator.validate_clauses(
            clauses
        )
    )

    print(
        f"Valid clauses    : "
        f"{clause_validation['valid_count']}"
    )

    print(
        f"Rejected clauses : "
        f"{clause_validation['rejected_count']}"
    )

    print(
        f"Duplicates       : "
        f"{clause_validation['duplicate_count']}"
    )

    if clause_validation[
        "rejected_clauses"
    ]:

        print(
            "\nRejected clause details:"
        )

        for rejected in clause_validation[
            "rejected_clauses"
        ]:

            print(
                f"  Clause "
                f"{rejected['clause_index']}: "
                f"{rejected['reason']}"
            )

    validated_text = "\n\n".join(
        clause_validation[
            "valid_clauses"
        ]
    )

    print(
        "\n5. Running validated contract "
        "through ML pipeline..."
    )

    report = analyzer.analyze(
        contract_text=validated_text,
        contract_id="day22_validated_contract",
        top_k=3,
    )

    summary = report.get(
        "summary",
        {}
    )

    print()
    print("=" * 80)
    print("VALIDATED PIPELINE RESULT")
    print("=" * 80)

    print(
        f"Analyzed clauses : "
        f"{len(report['analyzed_clauses'])}"
    )

    print(
        f"Overall risk     : "
        f"{report.get('overall_risk', 'N/A')}"
    )

    print(
        f"Risk score       : "
        f"{report.get('risk_score', 'N/A')}"
    )

    print(
        f"Review recommended: "
        f"{report.get('review_recommended', 'N/A')}"
    )

    if summary:

        print(
            f"Require review   : "
            f"{summary.get('requires_review', 'N/A')}"
        )

    output = {
        "validation": {
            "contract": {
                "character_count":
                    contract_validation[
                        "character_count"
                    ],

                "word_count":
                    contract_validation[
                        "word_count"
                    ],

                "warnings":
                    contract_validation[
                        "warnings"
                    ],
            },

            "clauses":
                clause_validation,
        },

        "analysis":
            report,
    }

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        OUTPUT_DIR
        / "day22_validation_report.json"
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print("=" * 80)
    print("DAY 22 COMPLETE")
    print("=" * 80)

    print(
        f"\nValidation report saved to:\n"
        f"{output_path}"
    )

    print(
        "\nNote: validation and risk scores are "
        "operational ML screening outputs, "
        "not legal conclusions."
    )


if __name__ == "__main__":
    main()