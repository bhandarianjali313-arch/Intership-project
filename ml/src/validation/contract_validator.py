from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ValidationConfig:
    """
    Configuration for contract input validation.

    These limits are operational safeguards for the
    ML pipeline and are not legal rules.
    """

    minimum_contract_length: int = 20
    minimum_clause_length: int = 10
    maximum_clause_length: int = 10000
    maximum_contract_length: int = 2_000_000


class ContractValidator:
    """
    Validate and clean contract text before it enters
    the ML contract intelligence pipeline.

    Responsibilities:
    - reject invalid input
    - normalize whitespace
    - detect suspicious input
    - remove duplicate clauses
    - validate segmented clauses
    - produce validation statistics
    """

    def __init__(
        self,
        config: ValidationConfig | None = None,
    ) -> None:

        self.config = (
            config
            if config is not None
            else ValidationConfig()
        )

        self._validate_config()

    def _validate_config(self) -> None:

        values = {
            "minimum_contract_length":
                self.config.minimum_contract_length,

            "minimum_clause_length":
                self.config.minimum_clause_length,

            "maximum_clause_length":
                self.config.maximum_clause_length,

            "maximum_contract_length":
                self.config.maximum_contract_length,
        }

        for name, value in values.items():

            if not isinstance(value, int):
                raise TypeError(
                    f"{name} must be an integer."
                )

            if value <= 0:
                raise ValueError(
                    f"{name} must be greater than 0."
                )

        if (
            self.config.minimum_clause_length
            >= self.config.maximum_clause_length
        ):
            raise ValueError(
                "minimum_clause_length must be smaller "
                "than maximum_clause_length."
            )

        if (
            self.config.minimum_contract_length
            >= self.config.maximum_contract_length
        ):
            raise ValueError(
                "minimum_contract_length must be smaller "
                "than maximum_contract_length."
            )

    @staticmethod
    def normalize_whitespace(
        text: str,
    ) -> str:
        """
        Normalize line endings and repeated spaces while
        preserving paragraph boundaries.
        """

        if not isinstance(text, str):
            raise TypeError(
                "text must be a string."
            )

        text = text.replace(
            "\r\n",
            "\n",
        )

        text = text.replace(
            "\r",
            "\n",
        )

        cleaned_lines = []

        for line in text.split("\n"):

            cleaned_line = re.sub(
                r"[ \t]+",
                " ",
                line,
            ).strip()

            cleaned_lines.append(
                cleaned_line
            )

        text = "\n".join(
            cleaned_lines
        )

        # Prevent excessive blank lines.
        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        return text.strip()

    def validate_contract_text(
        self,
        text: str,
    ) -> dict[str, Any]:

        if not isinstance(text, str):
            raise TypeError(
                "Contract text must be a string."
            )

        cleaned_text = (
            self.normalize_whitespace(
                text
            )
        )

        if not cleaned_text:
            raise ValueError(
                "Contract text cannot be empty."
            )

        text_length = len(
            cleaned_text
        )

        if (
            text_length
            < self.config.minimum_contract_length
        ):
            raise ValueError(
                "Contract text is too short for analysis."
            )

        if (
            text_length
            > self.config.maximum_contract_length
        ):
            raise ValueError(
                "Contract text exceeds the maximum "
                "supported length."
            )

        warnings = []

        word_count = len(
            cleaned_text.split()
        )

        if word_count < 10:

            warnings.append(
                "Contract contains very few words."
            )

        if "\x00" in cleaned_text:

            warnings.append(
                "Contract contains null characters."
            )

            cleaned_text = (
                cleaned_text.replace(
                    "\x00",
                    ""
                )
            )

        return {
            "valid":
                True,

            "cleaned_text":
                cleaned_text,

            "character_count":
                len(cleaned_text),

            "word_count":
                len(
                    cleaned_text.split()
                ),

            "warnings":
                warnings,
        }

    @staticmethod
    def _duplicate_key(
        text: str,
    ) -> str:

        text = text.lower()

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    def validate_clauses(
        self,
        clauses: list[str],
    ) -> dict[str, Any]:

        if not isinstance(
            clauses,
            list,
        ):
            raise TypeError(
                "clauses must be a list."
            )

        if not clauses:
            raise ValueError(
                "clauses cannot be empty."
            )

        valid_clauses = []
        rejected_clauses = []

        seen = set()

        duplicate_count = 0

        for index, clause in enumerate(
            clauses,
            start=1,
        ):

            if not isinstance(
                clause,
                str,
            ):

                rejected_clauses.append(
                    {
                        "clause_index":
                            index,

                        "reason":
                            "Clause is not a string.",
                    }
                )

                continue

            cleaned_clause = (
                self.normalize_whitespace(
                    clause
                )
            )

            if not cleaned_clause:

                rejected_clauses.append(
                    {
                        "clause_index":
                            index,

                        "reason":
                            "Clause is empty.",
                    }
                )

                continue

            if (
                len(cleaned_clause)
                < self.config.minimum_clause_length
            ):

                rejected_clauses.append(
                    {
                        "clause_index":
                            index,

                        "reason":
                            "Clause is too short.",
                    }
                )

                continue

            if (
                len(cleaned_clause)
                > self.config.maximum_clause_length
            ):

                rejected_clauses.append(
                    {
                        "clause_index":
                            index,

                        "reason":
                            "Clause exceeds maximum length.",
                    }
                )

                continue

            duplicate_key = (
                self._duplicate_key(
                    cleaned_clause
                )
            )

            if duplicate_key in seen:

                duplicate_count += 1

                rejected_clauses.append(
                    {
                        "clause_index":
                            index,

                        "reason":
                            "Duplicate clause.",
                    }
                )

                continue

            seen.add(
                duplicate_key
            )

            valid_clauses.append(
                cleaned_clause
            )

        if not valid_clauses:
            raise ValueError(
                "No valid clauses remain after validation."
            )

        return {
            "valid_clauses":
                valid_clauses,

            "rejected_clauses":
                rejected_clauses,

            "valid_count":
                len(valid_clauses),

            "rejected_count":
                len(rejected_clauses),

            "duplicate_count":
                duplicate_count,
        }

    def validate_pipeline_input(
        self,
        contract_text: str,
        clauses: list[str],
    ) -> dict[str, Any]:
        """
        Produce one combined validation result.
        """

        contract_result = (
            self.validate_contract_text(
                contract_text
            )
        )

        clause_result = (
            self.validate_clauses(
                clauses
            )
        )

        return {
            "contract":
                contract_result,

            "clauses":
                clause_result,

            "ready_for_analysis":
                (
                    contract_result["valid"]
                    and clause_result[
                        "valid_count"
                    ] > 0
                ),
        }