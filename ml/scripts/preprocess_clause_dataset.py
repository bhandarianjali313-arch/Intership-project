from pathlib import Path

import pandas as pd

from ml.src.preprocessing.text_cleaning import (
    clean_legal_text,
    count_words,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "cuad_clauses.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "cuad_clauses_clean.csv"
)


def print_header(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def load_dataset() -> pd.DataFrame:
    """
    Load the flattened CUAD dataset.
    """

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            "Processed CUAD dataset not found.\n"
            "Run Day 2 dataset builder first:\n"
            "python -m ml.scripts.build_clause_dataset"
        )

    return pd.read_csv(INPUT_PATH)


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean clause text and create useful ML features.
    """

    df = df.copy()

    # Pandas can convert empty CSV values into NaN.
    df["clause_text"] = (
        df["clause_text"]
        .fillna("")
        .astype(str)
    )

    df["question"] = (
        df["question"]
        .fillna("")
        .astype(str)
    )

    df["clause_name"] = (
        df["clause_name"]
        .fillna("")
        .astype(str)
    )

    # Preserve original clause text for debugging.
    df["original_clause_text"] = df["clause_text"]

    # Clean the extracted legal clause.
    df["cleaned_clause_text"] = (
        df["clause_text"]
        .apply(clean_legal_text)
    )

    # Clean question text as well.
    df["cleaned_question"] = (
        df["question"]
        .apply(clean_legal_text)
    )

    # Length features.
    df["clause_char_length"] = (
        df["cleaned_clause_text"]
        .str.len()
    )

    df["clause_word_count"] = (
        df["cleaned_clause_text"]
        .apply(count_words)
    )

    return df


def validate_dataset(
    df: pd.DataFrame
) -> None:
    """
    Run basic quality checks after preprocessing.
    """

    print_header("DATA QUALITY VALIDATION")

    print(
        f"Total records              : "
        f"{len(df):,}"
    )

    print(
        f"Unique contracts           : "
        f"{df['contract_id'].nunique():,}"
    )

    print(
        f"Unique clause labels       : "
        f"{df['clause_label'].nunique():,}"
    )

    positive_df = df[
        df["has_answer"] == True
    ]

    negative_df = df[
        df["has_answer"] == False
    ]

    print(
        f"Positive examples          : "
        f"{len(positive_df):,}"
    )

    print(
        f"Negative examples          : "
        f"{len(negative_df):,}"
    )

    empty_positive = positive_df[
        positive_df[
            "cleaned_clause_text"
        ].str.strip() == ""
    ]

    print(
        f"Empty positive clauses     : "
        f"{len(empty_positive):,}"
    )

    missing_labels = df[
        df["clause_label"]
        .fillna("")
        .str.strip() == ""
    ]

    print(
        f"Missing clause labels      : "
        f"{len(missing_labels):,}"
    )


def analyze_lengths(
    df: pd.DataFrame
) -> None:
    """
    Analyze clause-text length distribution.
    """

    print_header("CLAUSE LENGTH ANALYSIS")

    positive_df = df[
        df["has_answer"] == True
    ]

    word_counts = (
        positive_df["clause_word_count"]
    )

    print(
        f"Minimum words  : "
        f"{word_counts.min():,}"
    )

    print(
        f"Maximum words  : "
        f"{word_counts.max():,}"
    )

    print(
        f"Mean words     : "
        f"{word_counts.mean():.2f}"
    )

    print(
        f"Median words   : "
        f"{word_counts.median():.2f}"
    )

    print(
        f"90th percentile: "
        f"{word_counts.quantile(0.90):.2f}"
    )

    print(
        f"95th percentile: "
        f"{word_counts.quantile(0.95):.2f}"
    )

    print(
        f"99th percentile: "
        f"{word_counts.quantile(0.99):.2f}"
    )


def analyze_duplicates(
    df: pd.DataFrame
) -> None:
    """
    Inspect exact duplicate positive annotations.
    """

    print_header("DUPLICATE ANALYSIS")

    positive_df = df[
        df["has_answer"] == True
    ]

    duplicate_mask = (
        positive_df.duplicated(
            subset=[
                "contract_id",
                "clause_label",
                "cleaned_clause_text",
                "answer_start",
            ],
            keep=False,
        )
    )

    duplicate_count = int(
        duplicate_mask.sum()
    )

    print(
        f"Potential duplicate records: "
        f"{duplicate_count:,}"
    )


def show_examples(
    df: pd.DataFrame
) -> None:

    print_header("CLEANING EXAMPLES")

    positive_df = df[
        df["has_answer"] == True
    ]

    sample = positive_df[
        [
            "clause_label",
            "original_clause_text",
            "cleaned_clause_text",
            "clause_word_count",
        ]
    ].head(5)

    print(
        sample.to_string(
            index=False
        )
    )


def main() -> None:

    print_header(
        "DAY 4 - CUAD TEXT PREPROCESSING"
    )

    print(
        f"Input dataset:\n{INPUT_PATH}"
    )

    df = load_dataset()

    print(
        f"\nLoaded records: "
        f"{len(df):,}"
    )

    cleaned_df = clean_dataset(
        df
    )

    validate_dataset(
        cleaned_df
    )

    analyze_lengths(
        cleaned_df
    )

    analyze_duplicates(
        cleaned_df
    )

    show_examples(
        cleaned_df
    )

    cleaned_df.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8",
    )

    print_header(
        "PREPROCESSING COMPLETE"
    )

    print(
        f"Clean dataset saved to:\n"
        f"{OUTPUT_PATH}"
    )

    print(
        "\nDay 4 completed successfully."
    )


if __name__ == "__main__":
    main()