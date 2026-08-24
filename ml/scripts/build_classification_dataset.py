from pathlib import Path
import json

import pandas as pd

from ml.src.classification.dataset_utils import (
    add_label_ids,
    create_label_mapping,
    find_conflicting_labels,
    prepare_classification_rows,
    remove_exact_duplicates,
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

SPLIT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "splits"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "classification"
)

LABEL_MAPPING_PATH = (
    OUTPUT_DIR
    / "label_mapping.json"
)

SUMMARY_PATH = (
    OUTPUT_DIR
    / "classification_summary.csv"
)

CONFLICT_PATH = (
    OUTPUT_DIR
    / "conflicting_examples.csv"
)


SPLITS = [
    "train",
    "validation",
    "test",
]


def print_header(
    title: str,
) -> None:

    print(
        "\n"
        + "=" * 80
    )

    print(title)

    print(
        "=" * 80
    )


def load_split(
    split_name: str,
) -> pd.DataFrame:

    path = (
        SPLIT_DIR
        / f"{split_name}.csv"
    )

    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found.\n"
            "Run Day 5 first:\n"
            "python -m ml.scripts.create_dataset_splits"
        )

    return pd.read_csv(path)


def build_all_splits() -> dict[str, pd.DataFrame]:

    datasets = {}

    for split_name in SPLITS:

        print(
            f"\nPreparing {split_name}..."
        )

        raw_df = load_split(
            split_name
        )

        prepared_df = (
            prepare_classification_rows(
                raw_df
            )
        )

        prepared_df, removed = (
            remove_exact_duplicates(
                prepared_df
            )
        )

        print(
            f"Raw records             : "
            f"{len(raw_df):,}"
        )

        print(
            f"Usable positive clauses : "
            f"{len(prepared_df):,}"
        )

        print(
            f"Exact duplicates removed: "
            f"{removed:,}"
        )

        datasets[
            split_name
        ] = prepared_df

    return datasets


def create_global_label_mapping(
    datasets: dict[str, pd.DataFrame],
):
    """
    Build the mapping from all known dataset labels.

    Using all splits here is safe because this only exposes
    the class vocabulary, not document text or statistics.
    """

    all_labels = []

    for df in datasets.values():

        all_labels.extend(
            df[
                "clause_label"
            ].tolist()
        )

    return create_label_mapping(
        all_labels
    )


def validate_contract_separation(
    datasets: dict[str, pd.DataFrame],
) -> None:

    print_header(
        "LEAKAGE VALIDATION"
    )

    train_contracts = set(
        datasets["train"][
            "contract_id"
        ]
    )

    validation_contracts = set(
        datasets["validation"][
            "contract_id"
        ]
    )

    test_contracts = set(
        datasets["test"][
            "contract_id"
        ]
    )

    train_validation = (
        train_contracts
        & validation_contracts
    )

    train_test = (
        train_contracts
        & test_contracts
    )

    validation_test = (
        validation_contracts
        & test_contracts
    )

    print(
        "Train/validation overlap : "
        f"{len(train_validation)}"
    )

    print(
        "Train/test overlap       : "
        f"{len(train_test)}"
    )

    print(
        "Validation/test overlap  : "
        f"{len(validation_test)}"
    )

    if (
        train_validation
        or train_test
        or validation_test
    ):
        raise RuntimeError(
            "Contract leakage detected."
        )

    print(
        "Contract-level leakage check passed."
    )


def analyze_conflicts(
    datasets: dict[str, pd.DataFrame],
) -> pd.DataFrame:

    combined = []

    for (
        split_name,
        df,
    ) in datasets.items():

        temp = df.copy()

        temp[
            "dataset_split"
        ] = split_name

        combined.append(
            temp
        )

    combined_df = pd.concat(
        combined,
        ignore_index=True,
    )

    conflicts = (
        find_conflicting_labels(
            combined_df
        )
    )

    return conflicts


def save_label_mapping(
    label_to_id: dict[str, int],
    id_to_label: dict[int, str],
) -> None:

    mapping = {
        "num_labels": len(
            label_to_id
        ),
        "label_to_id": (
            label_to_id
        ),
        "id_to_label": {
            str(key): value
            for key, value
            in id_to_label.items()
        },
    }

    with LABEL_MAPPING_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            mapping,
            file,
            indent=2,
            ensure_ascii=False,
        )


def save_datasets(
    datasets: dict[str, pd.DataFrame],
) -> None:

    for (
        split_name,
        df,
    ) in datasets.items():

        output_path = (
            OUTPUT_DIR
            / f"{split_name}.csv"
        )

        columns = [
            "contract_id",
            "contract_title",
            "qa_id",
            "cleaned_clause_text",
            "clause_label",
            "label_id",
            "clause_word_count",
        ]

        available_columns = [
            column
            for column in columns
            if column in df.columns
        ]

        df[
            available_columns
        ].to_csv(
            output_path,
            index=False,
            encoding="utf-8",
        )


def build_summary(
    datasets: dict[str, pd.DataFrame],
) -> pd.DataFrame:

    rows = []

    for (
        split_name,
        df,
    ) in datasets.items():

        label_counts = (
            df["clause_label"]
            .value_counts()
        )

        rows.append(
            {
                "split": split_name,
                "examples": len(df),
                "contracts": (
                    df[
                        "contract_id"
                    ]
                    .nunique()
                ),
                "labels": (
                    df[
                        "clause_label"
                    ]
                    .nunique()
                ),
                "smallest_class": (
                    int(
                        label_counts.min()
                    )
                    if not label_counts.empty
                    else 0
                ),
                "largest_class": (
                    int(
                        label_counts.max()
                    )
                    if not label_counts.empty
                    else 0
                ),
            }
        )

    return pd.DataFrame(
        rows
    )


def print_class_distribution(
    train_df: pd.DataFrame,
) -> None:

    print_header(
        "TRAINING CLASS DISTRIBUTION"
    )

    counts = (
        train_df[
            "clause_label"
        ]
        .value_counts()
    )

    print(
        counts.to_string()
    )

    if not counts.empty:

        imbalance_ratio = (
            counts.max()
            / counts.min()
        )

        print(
            "\nLargest/smallest "
            "class ratio: "
            f"{imbalance_ratio:.2f}"
        )


def main() -> None:

    print_header(
        "DAY 9 - CLAUSE "
        "CLASSIFICATION DATASET"
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    datasets = (
        build_all_splits()
    )

    validate_contract_separation(
        datasets
    )

    (
        label_to_id,
        id_to_label,
    ) = (
        create_global_label_mapping(
            datasets
        )
    )

    print_header(
        "LABEL MAPPING"
    )

    print(
        f"Number of classes: "
        f"{len(label_to_id)}"
    )

    for (
        label,
        label_id,
    ) in label_to_id.items():

        print(
            f"{label_id:>2} -> "
            f"{label}"
        )

    for split_name in SPLITS:

        datasets[
            split_name
        ] = add_label_ids(
            datasets[
                split_name
            ],
            label_to_id,
        )

    conflicts = (
        analyze_conflicts(
            datasets
        )
    )

    print_header(
        "CONFLICT ANALYSIS"
    )

    print(
        "Rows belonging to text "
        "with multiple labels: "
        f"{len(conflicts):,}"
    )

    if not conflicts.empty:

        print(
            "\nImportant: these rows "
            "are reported, not automatically removed."
        )

    print_class_distribution(
        datasets["train"]
    )

    save_datasets(
        datasets
    )

    save_label_mapping(
        label_to_id,
        id_to_label,
    )

    summary = build_summary(
        datasets
    )

    summary.to_csv(
        SUMMARY_PATH,
        index=False,
    )

    conflicts.to_csv(
        CONFLICT_PATH,
        index=False,
        encoding="utf-8",
    )

    print_header(
        "CLASSIFICATION SUMMARY"
    )

    print(
        summary.to_string(
            index=False
        )
    )

    print_header(
        "OUTPUT FILES"
    )

    print(
        f"Classification datasets:\n"
        f"{OUTPUT_DIR}"
    )

    print(
        f"\nLabel mapping:\n"
        f"{LABEL_MAPPING_PATH}"
    )

    print(
        f"\nConflict report:\n"
        f"{CONFLICT_PATH}"
    )

    print(
        "\nDay 9 classification "
        "dataset build completed successfully."
    )


if __name__ == "__main__":
    main()