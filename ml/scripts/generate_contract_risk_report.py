from __future__ import annotations

import json
from pathlib import Path

from ml.src.classification.inference import (
    ClauseClassifier,
)

from ml.src.risk.contract_report import (
    ContractRiskReportGenerator,
)

from ml.src.risk.risk_scorer import (
    ContractRiskScorer,
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
    / "risk"
)


SAMPLE_CONTRACT_CLAUSES = [
    (
        "This Agreement shall be governed by "
        "and construed in accordance with the "
        "laws of the State of New York."
    ),

    (
        "Neither party may assign this Agreement "
        "without the prior written consent of "
        "the other party."
    ),

    (
        "The liability of the Company under this "
        "Agreement shall be unlimited."
    ),

    (
        "Either party may terminate this Agreement "
        "for convenience upon thirty days prior "
        "written notice."
    ),

    (
        "The Licensee shall not compete with the "
        "Licensor during the term of this Agreement."
    ),
]


def main() -> None:

    print(
        "\n"
        + "=" * 80
    )

    print(
        "DAY 18 - CONTRACT RISK REPORT GENERATOR"
    )

    print(
        "=" * 80
    )

    classifier = ClauseClassifier(
        vectorizer_path=VECTORIZER_PATH,
        model_path=MODEL_PATH,
    )

    risk_scorer = (
        ContractRiskScorer()
    )

    report_generator = (
        ContractRiskReportGenerator()
    )

    scored_clauses = []

    print(
        f"\nProcessing "
        f"{len(SAMPLE_CONTRACT_CLAUSES)} clauses..."
    )

    for number, text in enumerate(
        SAMPLE_CONTRACT_CLAUSES,
        start=1,
    ):

        prediction = (
            classifier.predict_with_review(
                text=text,
                top_k=3,
            )
        )

        scored = (
            risk_scorer.score_prediction(
                prediction
            )
        )

        # Keep original text in the final report.
        scored["clause_text"] = text

        scored_clauses.append(
            scored
        )

        print(
            f"\nClause {number}: "
            f"{scored['predicted_label']}"
        )

        print(
            f"  Confidence : "
            f"{scored['confidence']:.4f}"
        )

        print(
            f"  Risk       : "
            f"{scored['risk_level']}"
        )

        print(
            f"  Review     : "
            f"{scored['requires_human_review']}"
        )


    report = (
        report_generator.generate_report(
            scored_clauses=scored_clauses,
            contract_id="sample_contract_001",
        )
    )


    print(
        "\n"
        + "=" * 80
    )

    print(
        "CONTRACT SUMMARY"
    )

    print(
        "=" * 80
    )

    summary = report[
        "summary"
    ]

    print(
        f"Total clauses           : "
        f"{summary['total_clauses']}"
    )

    print(
        f"Low-risk clauses        : "
        f"{summary['low_risk_clauses']}"
    )

    print(
        f"Medium-risk clauses     : "
        f"{summary['medium_risk_clauses']}"
    )

    print(
        f"High-risk clauses       : "
        f"{summary['high_risk_clauses']}"
    )

    print(
        f"Require human review    : "
        f"{summary['clauses_requiring_review']}"
    )

    print(
        f"Ambiguous predictions   : "
        f"{summary['ambiguous_predictions']}"
    )

    print(
        f"Risk score              : "
        f"{summary['risk_score_0_to_100']}/100"
    )

    print(
        f"Overall risk            : "
        f"{summary['overall_risk_level']}"
    )


    print(
        "\n"
        + "=" * 80
    )

    print(
        "TOP RISKY CLAUSES"
    )

    print(
        "=" * 80
    )

    for number, clause in enumerate(
        report["top_risky_clauses"],
        start=1,
    ):

        print(
            f"\n{number}. "
            f"{clause['clause_label']}"
        )

        print(
            f"   Risk       : "
            f"{clause['risk_level']}"
        )

        confidence = clause.get(
            "confidence"
        )

        if confidence is not None:

            print(
                f"   Confidence : "
                f"{confidence:.4f}"
            )

        print(
            f"   Review     : "
            f"{clause['requires_human_review']}"
        )


    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        OUTPUT_DIR
        / "sample_contract_risk_report.json"
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
        )


    print(
        "\n"
        + "=" * 80
    )

    print(
        "DAY 18 COMPLETE"
    )

    print(
        "=" * 80
    )

    print(
        f"\nReport saved to:\n"
        f"{output_path}"
    )


if __name__ == "__main__":
    main()