from __future__ import annotations

from operator import index
from typing import Any


# ============================================================================
# CUAD CLASSIFICATION LABELS
# ============================================================================
#
# The classification dataset creates label IDs by sorting
# the unique CUAD clause labels alphabetically.
#
# These labels therefore preserve the same deterministic
# ordering used during model training.
# ============================================================================


CUAD_CLAUSE_LABELS = (
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


CUAD_ID_TO_LABEL = {
    label_id: label
    for label_id, label
    in enumerate(
        CUAD_CLAUSE_LABELS
    )
}


CUAD_LABEL_TO_ID = {
    label: label_id
    for label_id, label
    in CUAD_ID_TO_LABEL.items()
}


def decode_clause_label(
    raw_label: Any,
) -> str:
    """
    Convert a model class value into its semantic
    CUAD clause label.

    Examples:

        13   -> GOVERNING_LAW
        "22" -> NON_COMPETE

    Labels that are already semantic strings are
    returned unchanged.
    """

    # ------------------------------------------------------------------------
    # String labels
    # ------------------------------------------------------------------------

    if isinstance(
        raw_label,
        str,
    ):

        cleaned = (
            raw_label.strip()
        )

        if not cleaned:
            return cleaned

        # Already a semantic label.
        if cleaned in CUAD_LABEL_TO_ID:
            return cleaned

        # Serialized numeric class such as "22".
        numeric_candidate = (
            cleaned.lstrip("-")
        )

        if numeric_candidate.isdigit():

            label_id = int(
                cleaned
            )

            return CUAD_ID_TO_LABEL.get(
                label_id,
                cleaned,
            )

        return cleaned

    # ------------------------------------------------------------------------
    # Integer-like values
    #
    # operator.index supports normal Python integers
    # and NumPy integer scalar types without treating
    # arbitrary floating-point values as IDs.
    # ------------------------------------------------------------------------

    try:

        label_id = index(
            raw_label
        )

    except TypeError:

        return str(
            raw_label
        )

    return CUAD_ID_TO_LABEL.get(
        label_id,
        str(raw_label),
    )


def is_known_clause_label(
    label: str,
) -> bool:
    """
    Return True when label belongs to the
    41-category CUAD classification vocabulary.
    """

    return (
        label
        in CUAD_LABEL_TO_ID
    )


def number_of_clause_labels() -> int:
    """
    Return the total number of CUAD clause classes.
    """

    return len(
        CUAD_CLAUSE_LABELS
    )