from __future__ import annotations

import re
from typing import Any


USEFUL_ENTITY_LABELS = {
    "ORG",
    "PERSON",
    "DATE",
    "TIME",
    "MONEY",
    "PERCENT",
    "GPE",
    "LOC",
    "LAW",
    "CARDINAL",
    "ORDINAL",
    "QUANTITY",
}


LEGAL_ROLE_TERMS = {
    "licensee",
    "licensor",
    "buyer",
    "seller",
    "customer",
    "supplier",
    "vendor",
    "distributor",
    "consultant",
    "contractor",
    "employer",
    "employee",
    "landlord",
    "tenant",
    "borrower",
    "lender",
    "franchisor",
    "franchisee",
    "company",
    "party",
    "parties",
}


DOMAIN_FALSE_POSITIVES = {
    "agreement",
    "territory",
    "services",
    "innovation",
    "product",
    "products",
    "term",
}


def normalize_entity_text(text: str) -> str:
    """
    Normalize whitespace around an entity.
    """

    if not isinstance(text, str):
        return ""

    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


def is_legal_role(text: str) -> bool:
    """
    Check whether an entity is a common legal-contract role.
    """

    normalized = normalize_entity_text(
        text
    ).lower()

    return normalized in LEGAL_ROLE_TERMS


def is_domain_false_positive(
    text: str,
    label: str,
) -> bool:
    """
    Detect obvious false positives produced by
    the general-purpose spaCy model.
    """

    normalized = normalize_entity_text(
        text
    ).lower()

    if normalized in DOMAIN_FALSE_POSITIVES:
        return True

    return False


def postprocess_entity(
    entity: dict[str, Any]
) -> dict[str, Any] | None:
    """
    Filter and normalize one entity.

    Returns None when the entity should be removed.
    """

    text = normalize_entity_text(
        entity.get("text", "")
    )

    label = entity.get(
        "label",
        ""
    )

    if not text:
        return None

    if is_legal_role(text):
        return {
            **entity,
            "text": text,
            "original_label": label,
            "normalized_label": "LEGAL_ROLE",
        }

    if label not in USEFUL_ENTITY_LABELS:
        return None

    if is_domain_false_positive(
        text=text,
        label=label,
    ):
        return None

    return {
        **entity,
        "text": text,
        "original_label": label,
        "normalized_label": label,
    }


def postprocess_entities(
    entities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Apply post-processing to a list of entities.
    """

    processed = []

    for entity in entities:

        result = postprocess_entity(
            entity
        )

        if result is not None:
            processed.append(
                result
            )

    return processed