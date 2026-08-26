"""
Postprocessing rules for NER output on legal text.
"""
import re
from typing import Dict, List, Optional


LEGAL_ROLES = {
    "Licensee", "Licensor", "Seller", "Buyer",
    "Lessor", "Lessee", "Borrower", "Lender",
    "Vendor", "Customer", "Tenant", "Landlord",
    "Assignor", "Assignee", "Guarantor", "Indemnitor",
    "Indemnitee", "Trustee", "Beneficiary", "Agent",
    "Principal", "Partner", "Party", "Parties",
}

# spaCy labels that are not meaningful for legal NER
UNWANTED_LABELS = {
    "WORK_OF_ART",
    "LANGUAGE",
    "EVENT",
    "PRODUCT",
    "LAW",
}

_WHITESPACE_RE = re.compile(r"\s+")


def normalize_entity_text(text: str) -> str:
    """Collapse internal whitespace and trim."""
    return _WHITESPACE_RE.sub(" ", text).strip()


def is_legal_role(text: str) -> bool:
    """Return True if the entity text is a recognized legal role."""
    return text.strip() in LEGAL_ROLES


def postprocess_entity(entity: Dict) -> Optional[Dict]:
    """
    Apply domain-specific cleanup to a single entity.
    Returns None when the entity should be discarded.
    """
    text = entity.get("text", "")
    label = entity.get("label", "")

    normalized = normalize_entity_text(text)

    # Drop entities with unwanted labels (e.g. generic PRODUCT/LANGUAGE)
    if label in UNWANTED_LABELS:
        return None

    # Promote legal roles to a dedicated label
    if is_legal_role(normalized):
        normalized_label = "LEGAL_ROLE"
    else:
        normalized_label = label

    return {
        "text": normalized,
        "label": label,
        "normalized_label": normalized_label,
        "start_char": entity.get("start_char"),
        "end_char": entity.get("end_char"),
    }


def postprocess_entities(entities: List[Dict]) -> List[Dict]:
    """Apply postprocess_entity to every entity and discard Nones."""
    result: List[Dict] = []
    for entity in entities:
        processed = postprocess_entity(entity)
        if processed is not None:
            result.append(processed)
    return result
