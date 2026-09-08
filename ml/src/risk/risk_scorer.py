from __future__ import annotations

from enum import Enum
from typing import Any


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


# -------------------------------------------------------------------------
# Initial clause-level risk knowledge.
#
# These are operational project heuristics, not legal conclusions.
# -------------------------------------------------------------------------

HIGH_RISK_CLAUSES = {
    "UNCAPPED_LIABILITY",
    "NON_COMPETE",
    "EXCLUSIVITY",
    "IP_OWNERSHIP_ASSIGNMENT",
    "LIQUIDATED_DAMAGES",
    "MINIMUM_COMMITMENT",
    "PRICE_RESTRICTIONS",
    "REVENUE_PROFIT_SHARING",
}

MEDIUM_RISK_CLAUSES = {
    "ANTI_ASSIGNMENT",
    "CHANGE_OF_CONTROL",
    "CAP_ON_LIABILITY",
    "TERMINATION_FOR_CONVENIENCE",
    "NO_SOLICIT_OF_CUSTOMERS",
    "NO_SOLICIT_OF_EMPLOYEES",
    "AUDIT_RIGHTS",
    "MOST_FAVORED_NATION",
    "ROFR_ROFO_ROFN",
    "POST_TERMINATION_SERVICES",
    "SOURCE_CODE_ESCROW",
}

LOW_RISK_CLAUSES = {
    "AGREEMENT_DATE",
    "DOCUMENT_NAME",
    "EFFECTIVE_DATE",
    "EXPIRATION_DATE",
    "GOVERNING_LAW",
    "PARTIES",
    "RENEWAL_TERM",
    "WARRANTY_DURATION",
}


RISK_SCORE = {
    RiskLevel.LOW: 1,
    RiskLevel.MEDIUM: 2,
    RiskLevel.HIGH: 3,
}


class ContractRiskScorer:
    """
    Rule-based risk scoring layer for classified
    legal clauses.

    Risk levels are project heuristics and should
    not be interpreted as legal advice.
    """

    def __init__(
        self,
        unknown_clause_risk: RiskLevel = RiskLevel.MEDIUM,
    ) -> None:

        self.unknown_clause_risk = unknown_clause_risk


    @staticmethod
    def _validate_label(
        clause_label: str,
    ) -> str:

        if not isinstance(
            clause_label,
            str,
        ):
            raise TypeError(
                "clause_label must be a string."
            )

        normalized = (
            clause_label
            .strip()
            .upper()
        )

        if not normalized:
            raise ValueError(
                "clause_label cannot be empty."
            )

        return normalized


    def get_base_risk(
        self,
        clause_label: str,
    ) -> RiskLevel:
        """
        Return the base risk associated with a
        predicted clause category.
        """

        label = self._validate_label(
            clause_label
        )

        if label in HIGH_RISK_CLAUSES:
            return RiskLevel.HIGH

        if label in MEDIUM_RISK_CLAUSES:
            return RiskLevel.MEDIUM

        if label in LOW_RISK_CLAUSES:
            return RiskLevel.LOW

        return self.unknown_clause_risk


    @staticmethod
    def _risk_reason(
        clause_label: str,
        risk_level: RiskLevel,
    ) -> str:
        """
        Produce a short human-readable explanation.
        """

        readable_label = (
            clause_label
            .replace("_", " ")
            .title()
        )

        if risk_level == RiskLevel.HIGH:

            return (
                f"{readable_label} is mapped to the "
                "high-risk category because this type "
                "of clause may create significant "
                "contractual obligations or exposure."
            )

        if risk_level == RiskLevel.MEDIUM:

            return (
                f"{readable_label} is mapped to the "
                "medium-risk category and should be "
                "reviewed for its specific terms."
            )

        return (
            f"{readable_label} is mapped to the "
            "low-risk category because it is mainly "
            "treated as informational or lower-risk "
            "metadata in the current project rules."
        )


    def score_clause(
        self,
        clause_label: str,
        confidence: float | None = None,
        requires_human_review: bool = False,
    ) -> dict[str, Any]:
        """
        Score one classified legal clause.
        """

        label = self._validate_label(
            clause_label
        )

        base_risk = self.get_base_risk(
            label
        )

        if confidence is not None:

            confidence = float(
                confidence
            )

            if not 0.0 <= confidence <= 1.0:
                raise ValueError(
                    "confidence must be between 0 and 1."
                )

        # Risk level describes the clause category.
        # Prediction uncertainty is kept separate.
        # We do not automatically turn a low-confidence
        # prediction into a high legal risk.

        review_required = bool(
            requires_human_review
        )

        if confidence is not None and confidence < 0.45:
            review_required = True

        return {
            "clause_label":
                label,

            "risk_level":
                base_risk.value,

            "risk_score":
                RISK_SCORE[base_risk],

            "model_confidence":
                confidence,

            "requires_human_review":
                review_required,

            "risk_reason":
                self._risk_reason(
                    label,
                    base_risk,
                ),
        }


    def score_prediction(
        self,
        prediction: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Score the output produced by the
        confidence-aware clause classifier.
        """

        if not isinstance(
            prediction,
            dict,
        ):
            raise TypeError(
                "prediction must be a dictionary."
            )

        if "predicted_label" not in prediction:
            raise ValueError(
                "prediction does not contain "
                "'predicted_label'."
            )

        risk = self.score_clause(
            clause_label=prediction[
                "predicted_label"
            ],
            confidence=prediction.get(
                "confidence"
            ),
            requires_human_review=prediction.get(
                "requires_human_review",
                False,
            ),
        )

        return {
            **prediction,
            **risk,
        }


    def summarize_contract(
        self,
        scored_clauses: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Create a simple contract-level summary from
        multiple scored clauses.
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

        counts = {
            RiskLevel.LOW.value: 0,
            RiskLevel.MEDIUM.value: 0,
            RiskLevel.HIGH.value: 0,
        }

        review_count = 0

        highest_score = 1

        for clause in scored_clauses:

            level = clause.get(
                "risk_level"
            )

            if level not in counts:
                raise ValueError(
                    f"Invalid risk level: {level}"
                )

            counts[level] += 1

            highest_score = max(
                highest_score,
                int(
                    clause["risk_score"]
                ),
            )

            if clause.get(
                "requires_human_review",
                False,
            ):
                review_count += 1

        score_to_level = {
            1: RiskLevel.LOW.value,
            2: RiskLevel.MEDIUM.value,
            3: RiskLevel.HIGH.value,
        }

        return {
            "total_clauses":
                len(scored_clauses),

            "low_risk_clauses":
                counts["LOW"],

            "medium_risk_clauses":
                counts["MEDIUM"],

            "high_risk_clauses":
                counts["HIGH"],

            "clauses_requiring_review":
                review_count,

            "overall_risk_level":
                score_to_level[
                    highest_score
                ],
        }