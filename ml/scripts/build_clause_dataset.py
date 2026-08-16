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
                    ensure_ascii=False,
                )
                + "\n"
            )


def validate_dataset(df: pd.DataFrame) -> None:
    """
    Validate the structure and answer spans
    of the processed CUAD dataset.
    """

    print_header("DATASET VALIDATION")

    required_columns = [
        "contract_id",
        "contract_title",
        "paragraph_id",
        "qa_id",
        "question",
        "clause_name",
        "clause_label",
        "clause_text",
        "answer_start",
        "answer_end",
        "has_answer",
        "span_valid",
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
        f"{len(invalid_spans):,}"
    )

    positive_df = df[
        df["has_answer"] == True
    ]

    valid_text_spans = int(
        positive_df["span_valid"].sum()
    )

    invalid_text_spans = (
        len(positive_df)
        - valid_text_spans
    )

    print(
        f"Valid text spans             : "
        f"{valid_text_spans:,}"
    )

    print(
        f"Invalid text spans           : "
        f"{invalid_text_spans:,}"
    )


def print_statistics(df: pd.DataFrame) -> None:
    """
    Print basic statistics about the flattened CUAD dataset.
    """

    print_header("CUAD FLAT DATASET STATISTICS")

    print(
        f"Total records        : "
        f"{len(df):,}"
    )

    print(
        f"Contracts            : "
        f"{df['contract_id'].nunique():,}"
    )

    print(
        f"Unique clause types  : "
        f"{df['clause_label'].nunique():,}"
    )

    positive = int(
        df["has_answer"].sum()
    )

    negative = (
        len(df)
        - positive
    )

    print(
        f"Positive examples    : "
        f"{positive:,}"
    )

    print(
        f"Negative examples    : "
        f"{negative:,}"
    )

    if len(df) > 0:
        positive_percent = (
            positive / len(df)
        ) * 100

        print(
            f"Positive percentage  : "
            f"{positive_percent:.2f}%"
        )

    print("\nTop 10 clause labels:")

    print(
        df["clause_label"]
        .value_counts()
        .head(10)
        .to_string()
    )


def print_examples(df: pd.DataFrame) -> None:
    """
    Print a few positive clause examples.
    """

    print_header("POSITIVE EXAMPLES")

    positive_df = df[
        df["has_answer"] == True
    ]

    if positive_df.empty:
        print("No positive examples found.")
        return

    columns = [
        "contract_title",
        "clause_name",
        "clause_label",
        "clause_text",
        "answer_start",
    ]

    print(
        positive_df[columns]
        .head(5)
        .to_string(index=False)
    )


def main() -> None:
    print_header(
        "BUILDING CUAD ML DATASET"
    )

    print(
        f"Input:\n{INPUT_PATH}"
    )

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"CUAD dataset not found at: "
            f"{INPUT_PATH}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    records = parse_cuad(
        INPUT_PATH,
        include_negative_examples=True,
    )

    if not records:
        raise RuntimeError(
            "Parser returned zero records."
        )

    df = pd.DataFrame(
        records
    )

    validate_dataset(
        df
    )

    print_statistics(
        df
    )

    print_examples(
        df
    )

    print_header(
        "SAVING DATASET"
    )

    df.to_csv(
        CSV_OUTPUT,
        index=False,
        encoding="utf-8",
    )

    save_jsonl(
        records,
        JSONL_OUTPUT,
    )

    print(
        f"CSV saved to:\n"
        f"{CSV_OUTPUT}"
    )

    print(
        f"\nJSONL saved to:\n"
        f"{JSONL_OUTPUT}"
    )

    print(
        "\nDataset build completed successfully."
    )


if __name__ == "__main__":
    main()