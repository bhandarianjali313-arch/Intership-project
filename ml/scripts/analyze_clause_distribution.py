from pathlib import Path
import json

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "cuad_clauses.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

DISTRIBUTION_PATH = (
    OUTPUT_DIR
    / "clause_distribution.csv"
)

MAPPING_PATH = (
    OUTPUT_DIR
    / "clause_label_mapping.json"
)

CHART_PATH = (
    OUTPUT_DIR
    / "clause_distribution.png"
)


def print_header(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def load_dataset() -> pd.DataFrame:

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            "Processed CUAD dataset not found. "
            "Run build_clause_dataset first."
        )

    return pd.read_csv(DATASET_PATH)


def build_distribution(
    df: pd.DataFrame
) -> pd.DataFrame:

    grouped = (
        df.groupby(
            [
                "clause_name",
                "clause_label",
            ]
        )
        .agg(
            total_records=(
                "qa_id",
                "count"
            ),
            positive_examples=(
                "has_answer",
                "sum"
            ),
        )
        .reset_index()
    )

    grouped["positive_examples"] = (
        grouped["positive_examples"]
        .astype(int)
    )

    grouped["negative_examples"] = (
        grouped["total_records"]
        - grouped["positive_examples"]
    )

    grouped["positive_ratio"] = (
        grouped["positive_examples"]
        / grouped["total_records"]
    )

    grouped = grouped.sort_values(
        by="positive_examples",
        ascending=False,
    )

    return grouped


def save_label_mapping(
    distribution: pd.DataFrame
) -> None:

    mapping = {}

    for _, row in distribution.iterrows():

        mapping[row["clause_label"]] = (
            row["clause_name"]
        )

    with MAPPING_PATH.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            mapping,
            file,
            indent=4,
            ensure_ascii=False,
        )


def print_summary(
    distribution: pd.DataFrame
) -> None:

    print_header("CLAUSE DISTRIBUTION SUMMARY")

    print(
        f"Total categories : "
        f"{len(distribution)}"
    )

    print(
        f"Most common      : "
        f"{distribution.iloc[0]['clause_label']}"
    )

    print(
        f"Positive examples: "
        f"{distribution.iloc[0]['positive_examples']}"
    )

    print(
        f"\nLeast common     : "
        f"{distribution.iloc[-1]['clause_label']}"
    )

    print(
        f"Positive examples: "
        f"{distribution.iloc[-1]['positive_examples']}"
    )

    print("\nTop 10 categories:\n")

    print(
        distribution[
            [
                "clause_label",
                "positive_examples",
                "negative_examples",
                "positive_ratio",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )


def analyze_imbalance(
    distribution: pd.DataFrame
) -> None:

    print_header("CLASS IMBALANCE ANALYSIS")

    max_count = (
        distribution["positive_examples"]
        .max()
    )

    min_count = (
        distribution["positive_examples"]
        .min()
    )

    median_count = (
        distribution["positive_examples"]
        .median()
    )

    print(
        f"Maximum positive examples : "
        f"{max_count}"
    )

    print(
        f"Minimum positive examples : "
        f"{min_count}"
    )

    print(
        f"Median positive examples  : "
        f"{median_count:.2f}"
    )

    if min_count > 0:

        imbalance_ratio = (
            max_count / min_count
        )

        print(
            f"Max/min imbalance ratio   : "
            f"{imbalance_ratio:.2f}"
        )

    rare_classes = distribution[
        distribution["positive_examples"] < 100
    ]

    print(
        f"\nClasses with fewer than "
        f"100 positive examples: "
        f"{len(rare_classes)}"
    )

    if not rare_classes.empty:

        print("\nRare classes:\n")

        print(
            rare_classes[
                [
                    "clause_label",
                    "positive_examples",
                ]
            ]
            .to_string(index=False)
        )


def create_chart(
    distribution: pd.DataFrame
) -> None:

    chart_df = distribution.sort_values(
        "positive_examples",
        ascending=True,
    )

    plt.figure(
        figsize=(12, 14)
    )

    plt.barh(
        chart_df["clause_label"],
        chart_df["positive_examples"],
    )

    plt.xlabel(
        "Positive Examples"
    )

    plt.ylabel(
        "Clause Category"
    )

    plt.title(
        "CUAD Clause Category Distribution"
    )

    plt.tight_layout()

    plt.savefig(
        CHART_PATH,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()


def main() -> None:

    print_header(
        "DAY 3 - CUAD CLAUSE ANALYSIS"
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df = load_dataset()

    print(
        f"Loaded records: "
        f"{len(df):,}"
    )

    distribution = build_distribution(
        df
    )

    print_summary(
        distribution
    )

    analyze_imbalance(
        distribution
    )

    distribution.to_csv(
        DISTRIBUTION_PATH,
        index=False,
    )

    save_label_mapping(
        distribution
    )

    create_chart(
        distribution
    )

    print_header("OUTPUT FILES")

    print(
        f"Distribution:\n"
        f"{DISTRIBUTION_PATH}"
    )

    print(
        f"\nLabel mapping:\n"
        f"{MAPPING_PATH}"
    )

    print(
        f"\nDistribution chart:\n"
        f"{CHART_PATH}"
    )

    print(
        "\nDay 3 analysis completed successfully."
    )


if __name__ == "__main__":
    main()