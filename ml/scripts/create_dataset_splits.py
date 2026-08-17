from pathlib import Path

import pandas as pd

from ml.src.preprocessing.split_utils import (
    assign_split_column,
    validate_no_contract_leakage,
    get_split_contract_counts,
    get_split_row_counts,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "cuad_clauses_clean.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "splits"
)

TRAIN_PATH = (
    OUTPUT_DIR
    / "train.csv"
)

VALIDATION_PATH = (
    OUTPUT_DIR
    / "validation.csv"
)

TEST_PATH = (
    OUTPUT_DIR
    / "test.csv"
)

SUMMARY_PATH = (
    OUTPUT_DIR
    / "split_summary.csv"
)


def print_header(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def load_dataset() -> pd.DataFrame:

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            "Clean dataset not found.\n"
            "Run Day 4 first:\n"
            "python -m ml.scripts.preprocess_clause_dataset"
        )

    return pd.read_csv(
        INPUT_PATH
    )


def print_split_summary(
    df: pd.DataFrame
) -> None:

    print_header(
        "SPLIT SUMMARY"
    )

    contract_counts = (
        get_split_contract_counts(df)
    )

    row_counts = (
        get_split_row_counts(df)
    )

    total_contracts = (
        df["contract_id"]
        .nunique()
    )

    total_rows = len(df)

    for split_name in [
        "train",
        "validation",
        "test",
    ]:

        contracts = (
            contract_counts.get(
                split_name,
                0
            )
        )

        rows = (
            row_counts.get(
                split_name,
                0
            )
        )

        contract_percentage = (
            contracts
            / total_contracts
            * 100
        )

        row_percentage = (
            rows
            / total_rows
            * 100
        )

        print(
            f"{split_name.upper():<12}"
            f" contracts: {contracts:<4} "
            f"({contract_percentage:6.2f}%) "
            f"records: {rows:<7} "
            f"({row_percentage:6.2f}%)"
        )


def validate_splits(
    df: pd.DataFrame
) -> None:

    print_header(
        "SPLIT VALIDATION"
    )

    leakage_free = (
        validate_no_contract_leakage(
            df
        )
    )

    print(
        f"Contract leakage detected: "
        f"{not leakage_free}"
    )

    if not leakage_free:
        raise RuntimeError(
            "Contract leakage detected "
            "between dataset splits."
        )

    expected_splits = {
        "train",
        "validation",
        "test",
    }

    actual_splits = set(
        df["split"]
        .unique()
    )

    if actual_splits != expected_splits:

        raise RuntimeError(
            f"Unexpected splits: "
            f"{actual_splits}"
        )

    print(
        "All contracts appear in exactly one split."
    )


def check_label_coverage(
    df: pd.DataFrame
) -> None:

    print_header(
        "LABEL COVERAGE"
    )

    all_labels = set(
        df["clause_label"]
        .dropna()
        .unique()
    )

    print(
        f"Total labels: "
        f"{len(all_labels)}"
    )

    for split_name in [
        "train",
        "validation",
        "test",
    ]:

        positive_subset = df[
            (df["split"] == split_name)
            &
            (df["has_answer"] == True)
        ]

        labels = set(
            positive_subset[
                "clause_label"
            ]
            .dropna()
            .unique()
        )

        missing = (
            all_labels
            - labels
        )

        print(
            f"\n{split_name.upper()}"
        )

        print(
            f"Positive labels present: "
            f"{len(labels)}"
        )

        print(
            f"Missing labels: "
            f"{len(missing)}"
        )

        if missing:

            print(
                ", ".join(
                    sorted(missing)
                )
            )


def save_splits(
    df: pd.DataFrame
) -> None:

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    train_df = df[
        df["split"] == "train"
    ].copy()

    validation_df = df[
        df["split"] == "validation"
    ].copy()

    test_df = df[
        df["split"] == "test"
    ].copy()

    train_df.to_csv(
        TRAIN_PATH,
        index=False,
        encoding="utf-8",
    )

    validation_df.to_csv(
        VALIDATION_PATH,
        index=False,
        encoding="utf-8",
    )

    test_df.to_csv(
        TEST_PATH,
        index=False,
        encoding="utf-8",
    )

    summary = (
        df.groupby("split")
        .agg(
            records=(
                "contract_id",
                "size"
            ),
            contracts=(
                "contract_id",
                "nunique"
            ),
            positive_examples=(
                "has_answer",
                "sum"
            ),
        )
        .reset_index()
    )

    summary[
        "positive_examples"
    ] = (
        summary[
            "positive_examples"
        ]
        .astype(int)
    )

    summary.to_csv(
        SUMMARY_PATH,
        index=False,
    )


def main() -> None:

    print_header(
        "DAY 5 - CONTRACT LEVEL DATASET SPLITTING"
    )

    df = load_dataset()

    print(
        f"Loaded records: "
        f"{len(df):,}"
    )

    print(
        f"Unique contracts: "
        f"{df['contract_id'].nunique():,}"
    )

    split_df = (
        assign_split_column(
            df,
            random_seed=42,
        )
    )

    validate_splits(
        split_df
    )

    print_split_summary(
        split_df
    )

    check_label_coverage(
        split_df
    )

    save_splits(
        split_df
    )

    print_header(
        "OUTPUT FILES"
    )

    print(
        f"Train:\n{TRAIN_PATH}"
    )

    print(
        f"\nValidation:\n"
        f"{VALIDATION_PATH}"
    )

    print(
        f"\nTest:\n"
        f"{TEST_PATH}"
    )

    print(
        f"\nSummary:\n"
        f"{SUMMARY_PATH}"
    )

    print(
        "\nDay 5 split completed successfully."
    )


if __name__ == "__main__":
    main()