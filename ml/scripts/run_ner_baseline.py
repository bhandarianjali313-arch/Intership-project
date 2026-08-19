from pathlib import Path
import json

import pandas as pd

from ml.src.ner.spacy_ner import (
    extract_entities,
    load_ner_model,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "splits"
    / "train.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ner"
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "ner_baseline_sample.jsonl"
)


SAMPLE_SIZE = 200


def print_header(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def load_dataset() -> pd.DataFrame:

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            "Train split not found.\n"
            "Run Day 5 first:\n"
            "python -m ml.scripts.create_dataset_splits"
        )

    return pd.read_csv(
        INPUT_PATH
    )


def prepare_sample(
    df: pd.DataFrame
) -> pd.DataFrame:

    positive_df = df[
        df["has_answer"] == True
    ].copy()

    positive_df = positive_df[
        positive_df[
            "cleaned_clause_text"
        ]
        .fillna("")
        .str.strip()
        != ""
    ]

    sample_size = min(
        SAMPLE_SIZE,
        len(positive_df),
    )

    return positive_df.sample(
        n=sample_size,
        random_state=42,
    )


def run_ner(
    df: pd.DataFrame
) -> list[dict]:

    print_header(
        "LOADING SPACY MODEL"
    )

    nlp = load_ner_model()

    print(
        "spaCy model loaded successfully."
    )

    results = []

    for _, row in df.iterrows():

        text = row[
            "cleaned_clause_text"
        ]

        entities = extract_entities(
            text=text,
            nlp=nlp,
        )

        results.append(
            {
                "contract_id": int(
                    row["contract_id"]
                ),
                "qa_id": row["qa_id"],
                "clause_label": row[
                    "clause_label"
                ],
                "text": text,
                "entities": entities,
            }
        )

    return results


def save_results(
    results: list[dict]
) -> None:

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:

        for record in results:

            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
                + "\n"
            )


def print_statistics(
    results: list[dict]
) -> None:

    print_header(
        "NER BASELINE STATISTICS"
    )

    total_entities = 0

    label_counts = {}

    texts_without_entities = 0

    for record in results:

        entities = record[
            "entities"
        ]

        if not entities:
            texts_without_entities += 1

        total_entities += len(
            entities
        )

        for entity in entities:

            label = entity[
                "label"
            ]

            label_counts[label] = (
                label_counts.get(
                    label,
                    0,
                )
                + 1
            )

    print(
        f"Texts processed       : "
        f"{len(results):,}"
    )

    print(
        f"Total entities found  : "
        f"{total_entities:,}"
    )

    print(
        f"Texts without entities: "
        f"{texts_without_entities:,}"
    )

    print(
        "\nEntity label counts:"
    )

    for (
        label,
        count,
    ) in sorted(
        label_counts.items(),
        key=lambda item: item[1],
        reverse=True,
    ):

        print(
            f"{label:<12}: "
            f"{count:,}"
        )


def show_examples(
    results: list[dict]
) -> None:

    print_header(
        "NER EXAMPLES"
    )

    shown = 0

    for record in results:

        if not record[
            "entities"
        ]:
            continue

        print(
            f"\nClause label: "
            f"{record['clause_label']}"
        )

        print(
            f"Text:\n"
            f"{record['text'][:400]}"
        )

        print(
            "\nEntities:"
        )

        for entity in (
            record["entities"][:10]
        ):

            print(
                f"  {entity['text']} "
                f"-> {entity['label']}"
            )

        shown += 1

        if shown >= 5:
            break


def main() -> None:

    print_header(
        "DAY 7 - SPACY NER BASELINE"
    )

    df = load_dataset()

    print(
        f"Loaded training records: "
        f"{len(df):,}"
    )

    sample_df = prepare_sample(
        df
    )

    print(
        f"Sample records: "
        f"{len(sample_df):,}"
    )

    results = run_ner(
        sample_df
    )

    print_statistics(
        results
    )

    show_examples(
        results
    )

    save_results(
        results
    )

    print_header(
        "NER BASELINE COMPLETE"
    )

    print(
        f"Results saved to:\n"
        f"{OUTPUT_PATH}"
    )

    print(
        "\nDay 7 completed successfully."
    )


if __name__ == "__main__":
    main()