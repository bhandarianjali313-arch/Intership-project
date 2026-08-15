import re


def extract_clause_name(question: str) -> str:
    """
    Extract the CUAD clause/category name from the full question.

    Example:
    Highlight ... related to "Anti-Assignment" ...
        ->
    Anti-Assignment
    """

    if not question:
        return ""

    match = re.search(
        r'related to\s+"([^"]+)"',
        question,
        flags=re.IGNORECASE,
    )

    if match:
        return match.group(1).strip()

    return question.strip()


def normalize_clause_label(clause_name: str) -> str:
    """
    Convert a clause name into a machine-friendly label.

    Examples:
    Anti-Assignment      -> ANTI_ASSIGNMENT
    Cap On Liability    -> CAP_ON_LIABILITY
    Rofr/Rofo/Rofn      -> ROFR_ROFO_ROFN
    """

    if not clause_name:
        return ""

    label = clause_name.upper()

    label = re.sub(
        r"[^A-Z0-9]+",
        "_",
        label,
    )

    label = re.sub(
        r"_+",
        "_",
        label,
    )

    return label.strip("_")


def get_normalized_label(question: str) -> tuple[str, str]:
    """
    Return both:
    - human-readable clause name
    - normalized ML label
    """

    clause_name = extract_clause_name(question)

    clause_label = normalize_clause_label(
        clause_name
    )

    return clause_name, clause_label