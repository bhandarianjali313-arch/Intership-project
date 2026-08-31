from __future__ import annotations

import re
from typing import Any

from ml.src.classification.inference import ClauseClassifier
from ml.src.risk.contract_report import ContractRiskReportGenerator
from ml.src.risk.risk_scorer import ContractRiskScorer


class ContractAnalyzer:
    """
    End-to-end contract analysis pipeline.

    Raw contract text
        -> clause segmentation
        -> classification
        -> confidence assessment
        -> risk scoring
        -> contract-level report
    """

    def __init__(
        self,
        classifier: ClauseClassifier,
        risk_scorer: ContractRiskScorer | None = None,
        report_generator: ContractRiskReportGenerator | None = None,
        minimum_clause_length: int = 20,
    ) -> None:

        if not isinstance(minimum_clause_length, int):
            raise TypeError(
                "minimum_clause_length must be an integer."
            )

        if minimum_clause_length <= 0:
            raise ValueError(
                "minimum_clause_length must be greater than 0."
            )

        self.classifier = classifier

        self.risk_scorer = (
            risk_scorer
            if risk_scorer is not None
            else ContractRiskScorer()
        )

        self.report_generator = (
            report_generator
            if report_generator is not None
            else ContractRiskReportGenerator()
        )

        self.minimum_clause_length = minimum_clause_length

    # ---------------------------------------------------------
    # Validate contract text
    # ---------------------------------------------------------

    @staticmethod
    def _validate_contract_text(text: str) -> str:

        if not isinstance(text, str):
            raise TypeError(
                "Contract text must be a string."
            )

        text = text.strip()

        if not text:
            raise ValueError(
                "Contract text cannot be empty."
            )

        return text

    # ---------------------------------------------------------
    # Normalize text
    # ---------------------------------------------------------

    @staticmethod
    def normalize_text(text: str) -> str:

        text = text.replace(
            "\r\n",
            "\n",
        )

        text = text.replace(
            "\r",
            "\n",
        )

        lines = []

        for line in text.split("\n"):

            cleaned = re.sub(
                r"[ \t]+",
                " ",
                line,
            ).strip()

            lines.append(cleaned)

        return "\n".join(lines)

    # ---------------------------------------------------------
    # Split raw contract into candidate clauses
    # ---------------------------------------------------------

    def split_into_clauses(
        self,
        text: str,
    ) -> list[str]:

        text = self._validate_contract_text(
            text
        )

        text = self.normalize_text(
            text
        )

        # First split on blank lines.
        blocks = re.split(
            r"\n\s*\n+",
            text,
        )

        candidates = []

        for block in blocks:

            block = block.strip()

            if not block:
                continue

            # Try to recognize numbered legal sections.
            sections = re.split(
                r"(?=\n?\s*\d+(?:\.\d+)*[\.\)]\s+)",
                block,
            )

            for section in sections:

                section = section.strip()

                if section:
                    candidates.append(
                        section
                    )

        # If the contract is one very large block,
        # use conservative sentence segmentation.
        if (
            len(candidates) == 1
            and len(candidates[0]) > 500
        ):

            candidates = re.split(
                r"(?<=[.;!?])\s+(?=[A-Z])",
                candidates[0],
            )

        clauses = []

        for candidate in candidates:

            candidate = " ".join(
                candidate.split()
            )

            if (
                len(candidate)
                < self.minimum_clause_length
            ):
                continue

            clauses.append(
                candidate
            )

        if not clauses:
            raise ValueError(
                "No usable clauses were found "
                "in the contract text."
            )

        return clauses

    # ---------------------------------------------------------
    # Analyze one clause
    # ---------------------------------------------------------

    def analyze_clause(
        self,
        text: str,
        clause_index: int,
        top_k: int = 3,
    ) -> dict[str, Any]:

        prediction = (
            self.classifier.predict_with_review(
                text=text,
                top_k=top_k,
            )
        )

        scored = (
            self.risk_scorer.score_prediction(
                prediction
            )
        )

        scored["clause_index"] = (
            clause_index
        )

        scored["clause_text"] = text

        return scored

    # ---------------------------------------------------------
    # Analyze complete contract
    # ---------------------------------------------------------

    def analyze(
        self,
        contract_text: str,
        contract_id: str = "unknown_contract",
        top_k: int = 3,
    ) -> dict[str, Any]:

        clauses = self.split_into_clauses(
            contract_text
        )

        scored_clauses = []

        for index, clause in enumerate(
            clauses,
            start=1,
        ):

            result = self.analyze_clause(
                text=clause,
                clause_index=index,
                top_k=top_k,
            )

            scored_clauses.append(
                result
            )

        report = (
            self.report_generator.generate_report(
                scored_clauses=scored_clauses,
                contract_id=contract_id,
            )
        )

        report["analyzed_clauses"] = (
            scored_clauses
        )

        return report