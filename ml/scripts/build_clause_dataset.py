from pathlib import Path
import json

import pandas as pd

from ml.src.preprocessing.parse_cuad import parse_cuad


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = PROJECT_ROOT / "data" / "CUADv1.json"

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

CSV_OUTPUT = OUTPUT_DIR / "cuad_clauses.csv"

JSONL_OUTPUT = OUTPUT_DIR / "cuad_clauses.jsonl"


def print_header(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def save_jsonl(records, path: Path) -> None:
    """
    Save records in JSON Lines format.
    """

    with path.open("w", encoding="utf-8") as file:

        for record in records:
            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                )
                + "\n"
            )


def validate_dataset(df: pd.DataFrame) -> None:

    print_header("DATASET VALIDATION")

    required_columns = [
        "contract_id",
        "contract_title",
        "paragraph_id",
        "qa_id",
        "clause_type",
        "clause_text",
        "answer_start",
        "answer_end",
        "has_answer",
        "context_length",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    print("All expected columns are present.")

    invalid_spans = df[
        (df["has_answer"] == True)
        &
        (
            (df["answer_start"] < 0)
            |
            (df["answer_end"] <= df["answer_start"])
        )
    ]

    print(
        f"Invalid positive answer spans: "
        f"{len(invalid_spans)}"
    )


def print_statistics(df: pd.DataFrame) -> None:

    print_header("CUAD FLAT DATASET STATISTICS")

    print(f"Total records        : {len(df):,}")

    print(
        f"Contracts            : "
        f"{df['contract_id'].nunique():,}"
    )

    print(
        f"Unique clause types  : "
        f"{df['clause_type'].nunique():,}"
    )

    positive = int(
        df["has_answer"].sum()
    )

    negative = len(df) - positive

    print(f"Positive examples    : {positive:,}")
    print(f"Negative examples    : {negative:,}")

    if len(df):

        positive_percent = (
            positive / len(df)
        ) * 100

        print(
            f"Positive percentage  : "
            f"{positive_percent:.2f}%"
        )

    print("\nTop 10 clause types:")

    print(
        df["clause_type"]
        .value_counts()
        .head(10)
        .to_string()
    )


def print_examples(df: pd.DataFrame) -> None:

    print_header("POSITIVE EXAMPLES")

    positive_df = df[
        df["has_answer"] == True
    ]

    columns = [
        "contract_title",
        "clause_type",
        "clause_text",
        "answer_start",
    ]

    if positive_df.empty:
        print("No positive examples found.")
        return

    print(
        positive_df[columns]
        .head(5)
        .to_string(index=False)
    )


def main() -> None:

    print_header("BUILDING CUAD ML DATASET")

    print(f"Input:\n{INPUT_PATH}")

    if not INPUT_PATH.exists():

        raise FileNotFoundError(
            f"CUAD dataset not found at: {INPUT_PATH}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    records = parse_cuad(
        INPUT_PATH,
        include_negative_examples=True,
    )

    if not records:

        raise RuntimeError(
            "Parser returned zero records."
        )

    df = pd.DataFrame(records)

    validate_dataset(df)

    print_statistics(df)

    print_examples(df)

    print_header("SAVING DATASET")

    df.to_csv(
        CSV_OUTPUT,
        index=False,
        encoding="utf-8"
    )

    save_jsonl(
        records,
        JSONL_OUTPUT
    )

    print(f"CSV saved to:\n{CSV_OUTPUT}")

    print(f"\nJSONL saved to:\n{JSONL_OUTPUT}")

    print("\nDay 2 dataset build completed successfully.")


if __name__ == "__main__":
    main()