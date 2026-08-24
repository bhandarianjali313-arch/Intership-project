from pathlib import Path
import json
from collections import Counter

import pandas as pd

from ml.src.ner.entity_postprocessing import (
    postprocess_entities,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ner"
    / "ner_baseline_sample.jsonl"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ner"
)

FILTERED_OUTPUT = (
    OUTPUT_DIR
    / "ner_filtered_sample.jsonl"
)

SUMMARY_OUTPUT = (
    OUTPUT_DIR
    / "ner_quality_summary.csv"
)


def print_header(
    title: str
) -> None:

    print(
        "\n"
        + "=" * 80
    )

    print(title)

    print(
        "=" * 80
    )


def load_jsonl(
    path: Path
) -> list[dict]:

    if not path.exists():

        raise FileNotFoundError(
            "Day 7 NER output not found.\n"
            "Run:\n"
            "python -m ml.scripts.run_ner_baseline"
        )

    records = []

    with path.open(
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            line = line.strip()

            if line:
                records.append(
                    json.loads(line)
                )

    return records


def process_records(
    records: list[dict]
) -> list[dict]:

    processed_records = []

    for record in records:

        original_entities = record.get(
            "entities",
            []
        )

        filtered_entities = (
            postprocess_entities(
                original_entities
            )
        )

        processed_records.append(
            {
                **record,
                "original_entity_count": len(
                    original_entities
                ),
                "filtered_entity_count": len(
                    filtered_entities
                ),
                "entities": filtered_entities,
            }
        )

    return processed_records


def save_jsonl(
    records: list[dict],
    path: Path,
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8"
    ) as file:

        for record in records:

            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
                + "\n"
            )


def build_summary(
    original_records: list[dict],
    processed_records: list[dict],
) -> pd.DataFrame:

    original_counts = Counter()
    filtered_counts = Counter()

    total_original = 0
    total_filtered = 0

    texts_with_original = 0
    texts_with_filtered = 0

    for record in original_records:

        entities = record.get(
            "entities",
            []
        )

        if entities:
            texts_with_original += 1

        total_original += len(
            entities
        )

        for entity in entities:
            original_counts[
                entity.get(
                    "label",
                    "UNKNOWN"
                )
            ] += 1

    for record in processed_records:

        entities = record.get(
            "entities",
            []
        )

        if entities:
            texts_with_filtered += 1

        total_filtered += len(
            entities
        )

        for entity in entities:
            filtered_counts[
                entity.get(
                    "normalized_label",
                    "UNKNOWN"
                )
            ] += 1

    summary_rows = [
        {
            "metric": "texts_processed",
            "value": len(
                original_records
            ),
        },
        {
            "metric": "original_entities",
            "value": total_original,
        },
        {
            "metric": "filtered_entities",
            "value": total_filtered,
        },
        {
            "metric": "removed_entities",
            "value": (
                total_original
                - total_filtered
            ),
        },
        {
            "metric": "texts_with_original_entities",
            "value": texts_with_original,
        },
        {
            "metric": "texts_with_filtered_entities",
            "value": texts_with_filtered,
        },
    ]

    return pd.DataFrame(
        summary_rows
    )


def print_label_distribution(
    records: list[dict],
) -> None:

    print_header(
        "FILTERED ENTITY DISTRIBUTION"
    )

    counts = Counter()

    for record in records:

        for entity in record.get(
            "entities",
            []
        ):

            label = entity.get(
                "normalized_label",
                "UNKNOWN",
            )

            counts[
                label
            ] += 1

    for label, count in (
        counts.most_common()
    ):

        print(
            f"{label:<15}: "
            f"{count:,}"
        )


def print_removed_examples(
    original_records: list[dict],
    processed_records: list[dict],
) -> None:

    print_header(
        "POST-PROCESSING EXAMPLES"
    )

    shown = 0

    for original, processed in zip(
        original_records,
        processed_records,
    ):

        original_entities = (
            original.get(
                "entities",
                []
            )
        )

        processed_entities = (
            processed.get(
                "entities",
                []
            )
        )

        if (
            len(original_entities)
            == len(processed_entities)
        ):
            continue

        print(
            f"\nClause label: "
            f"{original.get('clause_label')}"
        )

        print(
            f"Original entities: "
            f"{len(original_entities)}"
        )

        print(
            f"Filtered entities: "
            f"{len(processed_entities)}"
        )

        print(
            "\nFiltered result:"
        )

        for entity in (
            processed_entities[:10]
        ):

            print(
                f"  {entity['text']} "
                f"-> "
                f"{entity['normalized_label']}"
            )

        shown += 1

        if shown >= 5:
            break


def main() -> None:

    print_header(
        "DAY 8 - NER POST-PROCESSING "
        "AND QUALITY ANALYSIS"
    )

    original_records = (
        load_jsonl(
            INPUT_PATH
        )
    )

    print(
        f"Loaded NER records: "
        f"{len(original_records):,}"
    )

    processed_records = (
        process_records(
            original_records
        )
    )

    summary = build_summary(
        original_records,
        processed_records,
    )

    print_header(
        "QUALITY SUMMARY"
    )

    print(
        summary.to_string(
            index=False
        )
    )

    print_label_distribution(
        processed_records
    )

    print_removed_examples(
        original_records,
        processed_records,
    )

    save_jsonl(
        processed_records,
        FILTERED_OUTPUT,
    )

    summary.to_csv(
        SUMMARY_OUTPUT,
        index=False,
    )

    print_header(
        "DAY 8 COMPLETE"
    )

    print(
        f"Filtered NER output:\n"
        f"{FILTERED_OUTPUT}"
    )

    print(
        f"\nSummary:\n"
        f"{SUMMARY_OUTPUT}"
    )


if __name__ == "__main__":
    main()