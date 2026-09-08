from __future__ import annotations

from collections import Counter
from typing import Any


class ClauseIntelligenceAnalyzer:
    """
    Combine clause classification/risk information
    with named entities extracted from legal text.

    The NER extractor is injected so this component
    remains independent of the specific NER model.
    """

    def __init__(
        self,
        entity_extractor: Any,
    ) -> None:

        if entity_extractor is None:
            raise ValueError(
                "entity_extractor cannot be None."
            )

        self.entity_extractor = (
            entity_extractor
        )

    @staticmethod
    def _validate_text(
        text: str,
    ) -> str:

        if not isinstance(text, str):
            raise TypeError(
                "text must be a string."
            )

        text = text.strip()

        if not text:
            raise ValueError(
                "text cannot be empty."
            )

        return text

    @staticmethod
    def _normalize_entity(
        entity: Any,
    ) -> dict[str, Any]:
        """
        Normalize common entity output formats.

        Supports:
            {"text": ..., "label": ...}

        and:

            {"text": ..., "label_": ...}
        """

        if isinstance(entity, dict):

            text = entity.get(
                "text",
                "",
            )

            label = (
                entity.get("label")
                or entity.get("label_")
                or entity.get("entity_type")
                or "UNKNOWN"
            )

            result = {
                "text": str(text),
                "label": str(label),
            }

            if "start" in entity:
                result["start"] = (
                    entity["start"]
                )

            if "end" in entity:
                result["end"] = (
                    entity["end"]
                )

            return result

        # Support spaCy-like entity objects.
        if hasattr(entity, "text"):

            return {
                "text": str(
                    entity.text
                ),

                "label": str(
                    getattr(
                        entity,
                        "label_",
                        "UNKNOWN",
                    )
                ),

                "start": getattr(
                    entity,
                    "start_char",
                    None,
                ),

                "end": getattr(
                    entity,
                    "end_char",
                    None,
                ),
            }

        raise TypeError(
            "Unsupported entity format."
        )

    def extract_entities(
        self,
        text: str,
    ) -> list[dict[str, Any]]:

        text = self._validate_text(
            text
        )

        extractor = (
            self.entity_extractor
        )

        # Support either:
        # extractor.extract(text)
        # or extractor.extract_entities(text)

        if hasattr(
            extractor,
            "extract_entities",
        ):

            raw_entities = (
                extractor.extract_entities(
                    text
                )
            )

        elif hasattr(
            extractor,
            "extract",
        ):

            raw_entities = (
                extractor.extract(
                    text
                )
            )

        else:

            raise AttributeError(
                "Entity extractor must provide "
                "extract() or extract_entities()."
            )

        if raw_entities is None:
            return []

        return [
            self._normalize_entity(
                entity
            )
            for entity in raw_entities
        ]

    def enrich_clause(
        self,
        clause: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Add NER information to an already classified
        and risk-scored clause.
        """

        if not isinstance(
            clause,
            dict,
        ):
            raise TypeError(
                "clause must be a dictionary."
            )

        if "clause_text" not in clause:
            raise ValueError(
                "clause must contain 'clause_text'."
            )

        text = self._validate_text(
            clause["clause_text"]
        )

        entities = (
            self.extract_entities(
                text
            )
        )

        entity_distribution = Counter(
            entity["label"]
            for entity in entities
        )

        return {
            **clause,

            "entities":
                entities,

            "entity_count":
                len(entities),

            "entity_type_distribution":
                dict(
                    entity_distribution
                ),
        }

    def enrich_clauses(
        self,
        clauses: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        if not isinstance(
            clauses,
            list,
        ):
            raise TypeError(
                "clauses must be a list."
            )

        return [
            self.enrich_clause(
                clause
            )
            for clause in clauses
        ]

    @staticmethod
    def summarize_entities(
        clauses: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Create contract-level entity statistics.
        """

        total_entities = 0

        type_counter = Counter()

        unique_entities = set()

        for clause in clauses:

            for entity in clause.get(
                "entities",
                [],
            ):

                total_entities += 1

                label = str(
                    entity.get(
                        "label",
                        "UNKNOWN",
                    )
                )

                text = str(
                    entity.get(
                        "text",
                        "",
                    )
                ).strip()

                type_counter[
                    label
                ] += 1

                if text:
                    unique_entities.add(
                        (
                            text.lower(),
                            label,
                        )
                    )

        return {
            "total_entities":
                total_entities,

            "unique_entities":
                len(
                    unique_entities
                ),

            "entity_type_distribution":
                dict(
                    type_counter
                ),
        }

    def enrich_report(
        self,
        report: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Add entity intelligence to a complete
        Day 19 contract report.
        """

        if not isinstance(
            report,
            dict,
        ):
            raise TypeError(
                "report must be a dictionary."
            )

        if "analyzed_clauses" not in report:
            raise ValueError(
                "report must contain "
                "'analyzed_clauses'."
            )

        enriched_clauses = (
            self.enrich_clauses(
                report[
                    "analyzed_clauses"
                ]
            )
        )

        entity_summary = (
            self.summarize_entities(
                enriched_clauses
            )
        )

        return {
            **report,

            "analyzed_clauses":
                enriched_clauses,

            "entity_summary":
                entity_summary,
        }