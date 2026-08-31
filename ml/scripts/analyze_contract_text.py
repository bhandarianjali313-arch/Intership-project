from __future__ import annotations

import argparse
import json
from pathlib import Path

from ml.src.classification.inference import ClauseClassifier
from ml.src.pipeline.contract_analyzer import ContractAnalyzer


# ---------------------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

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
    / "pipeline"
)


# ---------------------------------------------------------------------
# SAMPLE CONTRACT
# ---------------------------------------------------------------------

SAMPLE_CONTRACT = """
1. Governing Law

This Agreement shall be governed by and construed in accordance
with the laws of the State of New York.

2. Assignment

Neither party may assign this Agreement without the prior written
consent of the other party.

3. Liability

The liability of the Company under this Agreement shall be unlimited.

4. Termination

Either party may terminate this Agreement for convenience upon
thirty days prior written notice.

5. Non-Competition

The Licensee shall not compete with the Licensor during the term
of this Agreement.
"""


# ---------------------------------------------------------------------
# COMMAND-LINE ARGUMENTS
# ---------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """
    Create command-line arguments for the contract analyzer.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Run the end-to-end legal contract "
            "analysis pipeline."
        )
    )

    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help=(
            "Optional path to a plain-text contract file. "
            "If not provided, the built-in sample contract is used."
        ),
    )

    parser.add_argument(
        "--contract-id",
        type=str,
        default="sample_contract_001",
        help="Identifier for the analyzed contract.",
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help=(
            "Number of top clause classification "
            "predictions to keep."
        ),
    )

    return parser


# ---------------------------------------------------------------------
# CONTRACT LOADING
# ---------------------------------------------------------------------

def load_contract_text(
    file_path: str | None,
) -> str:
    """
    Load contract text from a .txt file.

    If no file is provided, use the built-in sample contract.
    """

    if file_path is None:
        return SAMPLE_CONTRACT

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Contract file not found: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Contract path is not a file: {path}"
        )

    text = path.read_text(
        encoding="utf-8"
    )

    if not text.strip():
        raise ValueError(
            f"Contract file is empty: {path}"
        )

    return text


# ---------------------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------------------

def main() -> None:
    """
    Run the complete Day 19 contract analysis pipeline.
    """

    args = build_parser().parse_args()

    print()
    print("=" * 80)
    print("DAY 19 - END-TO-END CONTRACT ANALYSIS")
    print("=" * 80)

    # -------------------------------------------------------------
    # Validate model artifacts
    # -------------------------------------------------------------

    if not VECTORIZER_PATH.exists():
        raise FileNotFoundError(
            "TF-IDF vectorizer was not found:\n"
            f"{VECTORIZER_PATH}"
        )

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "Logistic Regression model was not found:\n"
            f"{MODEL_PATH}"
        )

    print("\nModel artifacts:")
    print(
        f"Vectorizer : {VECTORIZER_PATH}"
    )
    print(
        f"Classifier : {MODEL_PATH}"
    )

    # -------------------------------------------------------------
    # Load contract
    # -------------------------------------------------------------

    contract_text = load_contract_text(
        args.file
    )

    if args.file is None:
        print(
            "\nUsing built-in sample contract."
        )
    else:
        print(
            f"\nLoaded contract from: {args.file}"
        )

    # -------------------------------------------------------------
    # Load classifier
    # -------------------------------------------------------------

    print(
        "\nLoading clause classifier..."
    )

    classifier = ClauseClassifier(
        vectorizer_path=VECTORIZER_PATH,
        model_path=MODEL_PATH,
    )

    # -------------------------------------------------------------
    # Create complete analyzer
    # -------------------------------------------------------------

    analyzer = ContractAnalyzer(
        classifier=classifier
    )

    # -------------------------------------------------------------
    # Segment contract
    # -------------------------------------------------------------

    print(
        "\nSegmenting contract..."
    )

    clauses = analyzer.split_into_clauses(
        contract_text
    )

    print(
        f"Candidate clauses found: {len(clauses)}"
    )

    # -------------------------------------------------------------
    # Analyze complete contract
    # -------------------------------------------------------------

    print(
        "\nAnalyzing clauses..."
    )

    report = analyzer.analyze(
        contract_text=contract_text,
        contract_id=args.contract_id,
        top_k=args.top_k,
    )

    # -------------------------------------------------------------
    # Print individual clause results
    # -------------------------------------------------------------

    for clause in report[
        "analyzed_clauses"
    ]:

        print()
        print("-" * 80)

        print(
            f"Clause {clause['clause_index']}"
        )

        print("-" * 80)

        clause_text = clause.get(
            "clause_text",
            "",
        )

        print(
            f"Text            : {clause_text}"
        )

        print(
            "Predicted label : "
            f"{clause['predicted_label']}"
        )

        print(
            "Confidence      : "
            f"{clause['confidence']:.4f}"
        )

        print(
            "Confidence level: "
            f"{clause.get('confidence_level', 'N/A')}"
        )

        print(
            "Risk level      : "
            f"{clause['risk_level']}"
        )

        print(
            "Risk score      : "
            f"{clause['risk_score']}/3"
        )

        print(
            "Human review    : "
            f"{clause['requires_human_review']}"
        )

        print(
            "Ambiguous       : "
            f"{clause.get('ambiguous_prediction', False)}"
        )

    # -------------------------------------------------------------
    # Print contract summary
    # -------------------------------------------------------------

    summary = report[
        "summary"
    ]

    print()
    print("=" * 80)
    print("FINAL CONTRACT SUMMARY")
    print("=" * 80)

    print(
        "Total clauses        : "
        f"{summary['total_clauses']}"
    )

    print(
        "Low-risk clauses     : "
        f"{summary['low_risk_clauses']}"
    )

    print(
        "Medium-risk clauses  : "
        f"{summary['medium_risk_clauses']}"
    )

    print(
        "High-risk clauses    : "
        f"{summary['high_risk_clauses']}"
    )

    print(
        "Require review       : "
        f"{summary['clauses_requiring_review']}"
    )

    print(
        "Ambiguous predictions: "
        f"{summary['ambiguous_predictions']}"
    )

    print(
        "Risk score           : "
        f"{summary['risk_score_0_to_100']}/100"
    )

    print(
        "Overall risk         : "
        f"{summary['overall_risk_level']}"
    )

    print(
        "Review recommended   : "
        f"{report['review_recommended']}"
    )

    # -------------------------------------------------------------
    # Print top risky clauses
    # -------------------------------------------------------------

    print()
    print("=" * 80)
    print("TOP RISKY CLAUSES")
    print("=" * 80)

    top_risky = report.get(
        "top_risky_clauses",
        [],
    )

    if not top_risky:
        print(
            "\nNo risky clauses were identified."
        )

    else:

        for index, clause in enumerate(
            top_risky,
            start=1,
        ):

            print(
                f"\n{index}. "
                f"{clause['clause_label']}"
            )

            print(
                "   Risk       : "
                f"{clause['risk_level']}"
            )

            confidence = clause.get(
                "confidence"
            )

            if confidence is not None:
                print(
                    "   Confidence : "
                    f"{confidence:.4f}"
                )

            print(
                "   Review     : "
                f"{clause.get('requires_human_review', False)}"
            )

    # -------------------------------------------------------------
    # Save JSON output
    # -------------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        OUTPUT_DIR
        / f"{args.contract_id}_analysis.json"
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

    # -------------------------------------------------------------
    # Complete
    # -------------------------------------------------------------

    print()
    print("=" * 80)
    print("DAY 19 COMPLETE")
    print("=" * 80)

    print(
        "\nAnalysis saved to:"
    )

    print(
        output_path
    )

    print(
        "\nNote: This is an ML-assisted screening "
        "result and not legal advice."
    )


if __name__ == "__main__":
    main()