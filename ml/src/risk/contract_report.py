from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any


class ContractRiskReportGenerator:
    """
    Generate a structured contract-level risk report
    from individually classified and scored clauses.

    This report is an ML-assisted screening output,
    not a legal conclusion.
    """

    def __init__(
        self,
        high_risk_weight: int = 3,
        medium_risk_weight: int = 2,
        low_risk_weight: int = 1,
    ) -> None:

        self.risk_weights = {
            "HIGH": high_risk_weight,
            "MEDIUM": medium_risk_weight,
            "LOW": low_risk_weight,
        }

        for level, weight in self.risk_weights.items():

            if weight <= 0:
                raise ValueError(
                    f"{level} risk weight must be positive."
                )


    @staticmethod
    def _validate_clauses(
        scored_clauses: list[dict[str, Any]],
    ) -> None:
        """
        Validate scored clause input.
        """

        if not isinstance(
            scored_clauses,
            list,
        ):
            raise TypeError(
                "scored_clauses must be a list."
            )

        if not scored_clauses:
            raise ValueError(
                "scored_clauses cannot be empty."
            )

        required_fields = {
            "clause_label",
            "risk_level",
            "risk_score",
        }

        for index, clause in enumerate(
            scored_clauses
        ):

            if not isinstance(
                clause,
                dict,
            ):
                raise TypeError(
                    f"Clause {index} must be a dictionary."
                )

            missing = (
                required_fields
                - set(clause)
            )

            if missing:
                raise ValueError(
                    f"Clause {index} is missing fields: "
                    f"{sorted(missing)}"
                )

            if clause["risk_level"] not in {
                "LOW",
                "MEDIUM",
                "HIGH",
            }:
                raise ValueError(
                    f"Invalid risk level in clause {index}: "
                    f"{clause['risk_level']}"
                )


    def _calculate_weighted_score(
        self,
        scored_clauses: list[dict[str, Any]],
    ) -> float:
        """
        Calculate normalized contract risk score
        on a 0-100 scale.

        LOW    contributes 1
        MEDIUM contributes 2
        HIGH   contributes 3 by default.
        """

        total_weight = sum(
            self.risk_weights[
                clause["risk_level"]
            ]
            for clause in scored_clauses
        )

        minimum_possible = (
            len(scored_clauses)
            * self.risk_weights["LOW"]
        )

        maximum_possible = (
            len(scored_clauses)
            * self.risk_weights["HIGH"]
        )

        if maximum_possible == minimum_possible:
            return 0.0

        normalized = (
            (
                total_weight
                - minimum_possible
            )
            /
            (
                maximum_possible
                - minimum_possible
            )
        )

        return round(
            normalized * 100.0,
            2,
        )


    @staticmethod
    def _overall_risk_level(
        scored_clauses: list[dict[str, Any]],
        weighted_score: float,
    ) -> str:
        """
        Determine overall screening risk.

        Any HIGH-risk clause keeps the contract
        from being classified as LOW overall.
        """

        has_high_risk = any(
            clause["risk_level"] == "HIGH"
            for clause in scored_clauses
        )

        if has_high_risk:
            return "HIGH"

        if weighted_score >= 30.0:
            return "MEDIUM"

        return "LOW"


    @staticmethod
    def _top_risky_clauses(
        scored_clauses: list[dict[str, Any]],
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Return the highest-risk clauses for review.
        """

        risk_order = {
            "HIGH": 3,
            "MEDIUM": 2,
            "LOW": 1,
        }

        ranked = sorted(
            scored_clauses,
            key=lambda clause: (
                risk_order[
                    clause["risk_level"]
                ],
                float(
                    clause.get(
                        "confidence",
                        clause.get(
                            "model_confidence",
                            0.0,
                        ),
                    )
                    or 0.0
                ),
            ),
            reverse=True,
        )

        output = []

        for clause in ranked[:limit]:

            output.append(
                {
                    "clause_label":
                        clause["clause_label"],

                    "risk_level":
                        clause["risk_level"],

                    "risk_score":
                        clause["risk_score"],

                    "confidence":
                        clause.get(
                            "confidence",
                            clause.get(
                                "model_confidence"
                            ),
                        ),

                    "requires_human_review":
                        clause.get(
                            "requires_human_review",
                            False,
                        ),

                    "risk_reason":
                        clause.get(
                            "risk_reason",
                            "",
                        ),
                }
            )

        return output


    def generate_report(
        self,
        scored_clauses: list[dict[str, Any]],
        contract_id: str = "unknown_contract",
    ) -> dict[str, Any]:
        """
        Generate the complete contract-level report.
        """

        self._validate_clauses(
            scored_clauses
        )

        risk_counts = Counter(
            clause["risk_level"]
            for clause in scored_clauses
        )

        clause_counts = Counter(
            clause["clause_label"]
            for clause in scored_clauses
        )

        total_clauses = len(
            scored_clauses
        )

        review_count = sum(
            bool(
                clause.get(
                    "requires_human_review",
                    False,
                )
            )
            for clause in scored_clauses
        )

        ambiguous_count = sum(
            bool(
                clause.get(
                    "ambiguous_prediction",
                    False,
                )
            )
            for clause in scored_clauses
        )

        weighted_score = (
            self._calculate_weighted_score(
                scored_clauses
            )
        )

        overall_risk = (
            self._overall_risk_level(
                scored_clauses,
                weighted_score,
            )
        )

        return {
            "contract_id":
                contract_id,

            "generated_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "summary": {
                "total_clauses":
                    total_clauses,

                "low_risk_clauses":
                    risk_counts.get(
                        "LOW",
                        0,
                    ),

                "medium_risk_clauses":
                    risk_counts.get(
                        "MEDIUM",
                        0,
                    ),

                "high_risk_clauses":
                    risk_counts.get(
                        "HIGH",
                        0,
                    ),

                "clauses_requiring_review":
                    review_count,

                "ambiguous_predictions":
                    ambiguous_count,

                "risk_score_0_to_100":
                    weighted_score,

                "overall_risk_level":
                    overall_risk,
            },

            "clause_type_distribution":
                dict(
                    clause_counts
                ),

            "top_risky_clauses":
                self._top_risky_clauses(
                    scored_clauses
                ),

            "review_recommended":
                (
                    review_count > 0
                    or risk_counts.get(
                        "HIGH",
                        0,
                    ) > 0
                ),

            "disclaimer": (
                "This report is an automated "
                "ML-assisted contract screening result "
                "and is not legal advice."
            ),
        }