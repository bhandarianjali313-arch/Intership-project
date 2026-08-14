from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    """
    Load a JSON dataset from disk.
    """

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def clean_question(question: str) -> str:
    """
    Normalize whitespace in CUAD questions.
    """

    return " ".join(
        question.split()
    ).strip()


def validate_answer_span(
    context: str,
    answer_text: str,
    answer_start: int,
) -> bool:
    """
    Check whether the annotated answer matches
    the text at answer_start.
    """

    if not answer_text:
        return False

    if answer_start < 0:
        return False

    answer_end = (
        answer_start
        + len(answer_text)
    )

    extracted_text = context[
        answer_start:answer_end
    ]

    return extracted_text == answer_text


def create_record(
    *,
    contract_index: int,
    contract_title: str,
    paragraph_index: int,
    context: str,
    qa: dict[str, Any],
    answer: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Convert one CUAD annotation into a flat record.
    """

    question = clean_question(
        qa.get("question", "")
    )

    qa_id = qa.get(
        "id",
        ""
    )

    if answer is None:

        answer_text = ""
        answer_start = -1
        answer_end = -1
        has_answer = False
        span_valid = False

    else:

        answer_text = answer.get(
            "text",
            ""
        )

        answer_start = answer.get(
            "answer_start",
            -1
        )

        if answer_start >= 0:

            answer_end = (
                answer_start
                + len(answer_text)
            )

        else:

            answer_end = -1

        has_answer = bool(
            answer_text
        )

        span_valid = validate_answer_span(
            context=context,
            answer_text=answer_text,
            answer_start=answer_start,
        )

    return {
        "contract_id": contract_index,
        "contract_title": contract_title,
        "paragraph_id": paragraph_index,
        "qa_id": qa_id,
        "clause_type": question,
        "clause_text": answer_text,
        "answer_start": answer_start,
        "answer_end": answer_end,
        "has_answer": has_answer,
        "span_valid": span_valid,
        "context_length": len(context),
    }


def parse_cuad(
    json_path: Path,
    include_negative_examples: bool = True,
) -> list[dict[str, Any]]:
    """
    Parse CUADv1.json into a flat list
    of clause annotation records.
    """

    dataset = load_json(
        json_path
    )

    documents = dataset.get(
        "data",
        []
    )

    records: list[
        dict[str, Any]
    ] = []

    for contract_index, document in enumerate(
        documents
    ):

        contract_title = document.get(
            "title",
            f"contract_{contract_index}",
        )

        paragraphs = document.get(
            "paragraphs",
            []
        )

        for paragraph_index, paragraph in enumerate(
            paragraphs
        ):

            context = paragraph.get(
                "context",
                ""
            )

            qas = paragraph.get(
                "qas",
                []
            )

            for qa in qas:

                answers = qa.get(
                    "answers",
                    []
                )

                # Positive annotations
                if answers:

                    for answer in answers:

                        record = create_record(
                            contract_index=contract_index,
                            contract_title=contract_title,
                            paragraph_index=paragraph_index,
                            context=context,
                            qa=qa,
                            answer=answer,
                        )

                        records.append(
                            record
                        )

                # Negative example:
                # clause queried but not present
                elif include_negative_examples:

                    record = create_record(
                        contract_index=contract_index,
                        contract_title=contract_title,
                        paragraph_index=paragraph_index,
                        context=context,
                        qa=qa,
                        answer=None,
                    )

                    records.append(
                        record
                    )

    return records