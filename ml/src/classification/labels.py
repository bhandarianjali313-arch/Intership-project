from __future__ import annotations

import re
from typing import Any


# =============================================================================
# CUAD CLAUSE LABELS
# =============================================================================
#
# The order below must remain consistent with the label encoding used when
# the clause-classification dataset and trained model were created.
#
# Model class ID:
#
#     0  -> AFFILIATE_LICENSE_LICENSEE
#     1  -> AFFILIATE_LICENSE_LICENSOR
#     ...
#     40 -> WARRANTY_DURATION
#
# Keeping this mapping in one module prevents inference, evaluation, and risk
# scoring from using different representations of the same class.
# =============================================================================


CLAUSE_LABELS: tuple[str, ...] = (
    "AFFILIATE_LICENSE_LICENSEE",
    "AFFILIATE_LICENSE_LICENSOR",
    "AGREEMENT_DATE",
    "ANTI_ASSIGNMENT",
    "AUDIT_RIGHTS",
    "CAP_ON_LIABILITY",
    "CHANGE_OF_CONTROL",
    "COMPETITIVE_RESTRICTION_EXCEPTION",
    "COVENANT_NOT_TO_SUE",
    "DOCUMENT_NAME",
    "EFFECTIVE_DATE",
    "EXCLUSIVITY",
    "EXPIRATION_DATE",
    "GOVERNING_LAW",
    "INSURANCE",
    "IP_OWNERSHIP_ASSIGNMENT",
    "IRREVOCABLE_OR_PERPETUAL_LICENSE",
    "JOINT_IP_OWNERSHIP",
    "LICENSE_GRANT",
    "LIQUIDATED_DAMAGES",
    "MINIMUM_COMMITMENT",
    "MOST_FAVORED_NATION",
    "NON_COMPETE",
    "NON_DISPARAGEMENT",
    "NON_TRANSFERABLE_LICENSE",
    "NOTICE_PERIOD_TO_TERMINATE_RENEWAL",
    "NO_SOLICIT_OF_CUSTOMERS",
    "NO_SOLICIT_OF_EMPLOYEES",
    "PARTIES",
    "POST_TERMINATION_SERVICES",
    "PRICE_RESTRICTIONS",
    "RENEWAL_TERM",
    "REVENUE_PROFIT_SHARING",
    "ROFR_ROFO_ROFN",
    "SOURCE_CODE_ESCROW",
    "TERMINATION_FOR_CONVENIENCE",
    "THIRD_PARTY_BENEFICIARY",
    "UNCAPPED_LIABILITY",
    "UNLIMITED_ALL_YOU_CAN_EAT_LICENSE",
    "VOLUME_RESTRICTION",
    "WARRANTY_DURATION",
)


ID_TO_LABEL: dict[int, str] = {
    index: label
    for index, label in enumerate(
        CLAUSE_LABELS
    )
}


LABEL_TO_ID: dict[str, int] = {
    label: index
    for index, label in ID_TO_LABEL.items()
}


_NUMERIC_CLASS_PATTERN = re.compile(
    r"^[+-]?\d+$"
)


def decode_clause_label(
    label: Any,
) -> str:
    """
    Convert a model class value into the canonical
    CUAD clause label.

    Supported inputs include:

        13
        "13"
        "GOVERNING_LAW"

    Numeric class IDs are decoded using ID_TO_LABEL.

    Textual labels are normalized to uppercase.

    Unknown numeric IDs raise ValueError instead of
    silently entering the risk pipeline as an unknown
    legal class.
    """

    if label is None:
        raise TypeError(
            "Clause label cannot be None."
        )

    raw_label = str(
        label
    ).strip()

    if not raw_label:
        raise ValueError(
            "Clause label cannot be empty."
        )

    normalized = (
        raw_label.upper()
    )

    # Already a canonical CUAD label.
    if normalized in LABEL_TO_ID:
        return normalized

    # Numeric model class such as:
    #
    #   13
    #   "13"
    #
    if _NUMERIC_CLASS_PATTERN.fullmatch(
        normalized
    ):

        class_id = int(
            normalized
        )

        if class_id not in ID_TO_LABEL:
            raise ValueError(
                "Unknown clause class ID: "
                f"{class_id}"
            )

        return ID_TO_LABEL[
            class_id
        ]

    # Preserve compatibility with textual labels that
    # may come from future models.
    return normalized


def encode_clause_label(
    label: str,
) -> int:
    """
    Convert a canonical CUAD clause label into its
    numeric class ID.
    """

    decoded = decode_clause_label(
        label
    )

    if decoded not in LABEL_TO_ID:
        raise ValueError(
            "Unknown CUAD clause label: "
            f"{decoded}"
        )

    return LABEL_TO_ID[
        decoded
    ]