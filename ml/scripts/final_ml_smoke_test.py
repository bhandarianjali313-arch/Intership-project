from __future__ import annotations

import json
from pathlib import Path

from backend.app.services.ml_contract_service import (
    MLContractService,
)

from ml.src.classification.label_mapping import (
    is_known_clause_label,
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "final_validation"
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "day25_smoke_test.json"
)


SAMPLE_CLAUSES = [
    (
        "Neither party may assign this Agreement "
        "without the prior written consent of "
        "the other party."
    ),
    (
        "The employee shall not compete with "
        "the company for a period of two years."
    ),
    (
        "This Agreement shall be governed by "
        "the laws of the State of Delaware."
    ),
]


def main() -> None:

    print(
        "\n"
        + "=" * 72
    )

    print(
        "DAY 25 - FINAL ML PRODUCTION SMOKE TEST"
    )

    print(
        "=" * 72
    )

    service = (
        MLContractService()
    )

    health = (
        service.health()
    )

    print(
        "\nML SERVICE HEALTH"
    )

    print(
        "-" * 72
    )

    for key, value in (
        health.items()
    ):

        print(
            f"{key:<25}: {value}"
        )

    results = []

    for index, text in enumerate(
        SAMPLE_CLAUSES,
        start=1,
    ):

        result = (
            service.analyze_clause(
                text=text,
                top_k=3,
            )
        )

        classification = (
            result[
                "classification"
            ]
        )

        risk = (
            result[
                "risk"
            ]
        )

        predicted_label = (
            classification[
                "predicted_label"
            ]
        )

        if predicted_label.lstrip(
            "-"
        ).isdigit():

            raise AssertionError(
                "Numeric prediction escaped semantic "
                "label decoding: "
                f"{predicted_label}"
            )

        if not is_known_clause_label(
            predicted_label
        ):

            raise AssertionError(
                "Unknown semantic clause label "
                "returned by classifier: "
                f"{predicted_label}"
            )

        print(
            "\n"
            f"CLAUSE {index}"
        )

        print(
            "-" * 72
        )

        print(
            f"Prediction : "
            f"{predicted_label}"
        )

        print(
            f"Confidence : "
            f"{classification['confidence']:.4f}"
        )

        print(
            f"Level      : "
            f"{classification['confidence_level']}"
        )

        print(
            f"Review     : "
            f"{classification['requires_human_review']}"
        )

        print(
            f"Risk       : "
            f"{risk['risk_level']}"
        )

        results.append(
            result
        )

    summary = {
        "status":
            "PASS",

        "semantic_label_decoding":
            True,

        "samples_tested":
            len(
                results
            ),

        "health":
            health,

        "results":
            results,
    }

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            summary,
            file,
            indent=2,
        )

    print(
        "\n"
        + "=" * 72
    )

    print(
        "FINAL ML SMOKE TEST PASSED"
    )

    print(
        "=" * 72
    )

    print(
        f"\nReport saved to:\n"
        f"{OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()