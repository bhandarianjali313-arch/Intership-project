from pathlib import Path

import pandas as pd

from ml.src.preprocessing.chunking import (
    create_word_chunks,
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
    / "chunks"
)

SUMMARY_PATH = (
    OUTPUT_DIR
    / "chunk_summary.csv"
)


CHUNK_SIZE = 350
CHUNK_OVERLAP = 50


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


def load_split(
    split_name: str
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

    return pd.read_csv(
        path
    )


def build_chunks(
    df: pd.DataFrame,
    split_name: str,
) -> pd.DataFrame:

    records = []

    positive_df = df[
        df["has_answer"] == True
    ].copy()

    for _, row in (
        positive_df.iterrows()
    ):

        text = row.get(
            "cleaned_clause_text",
            "",
        )

        if pd.isna(text):
            text = ""

        chunks = (
            create_word_chunks(
                text=text,
                chunk_size=CHUNK_SIZE,
                overlap=CHUNK_OVERLAP,
            )
        )

        for chunk in chunks:

            records.append(
                {
                    "split": split_name,
                    "contract_id": row[
                        "contract_id"
                    ],
                    "contract_title": row[
                        "contract_title"
                    ],
                    "qa_id": row[
                        "qa_id"
                    ],
                    "clause_name": row[
                        "clause_name"
                    ],
                    "clause_label": row[
                        "clause_label"
                    ],
                    "chunk_id": chunk[
                        "chunk_id"
                    ],
                    "chunk_text": chunk[
                        "chunk_text"
                    ],
                    "word_start": chunk[
                        "word_start"
                    ],
                    "word_end": chunk[
                        "word_end"
                    ],
                    "word_count": chunk[
                        "word_count"
                    ],
                }
            )

    return pd.DataFrame(
        records
    )


def validate_chunks(
    df: pd.DataFrame,
    split_name: str,
) -> None:

    print_header(
        f"{split_name.upper()} CHUNK VALIDATION"
    )

    if df.empty:
        raise RuntimeError(
            f"No chunks created "
            f"for {split_name}."
        )

    print(
        f"Total chunks     : "
        f"{len(df):,}"
    )

    print(
        f"Contracts        : "
        f"{df['contract_id'].nunique():,}"
    )

    print(
        f"Clause labels    : "
        f"{df['clause_label'].nunique():,}"
    )

    print(
        f"Minimum words    : "
        f"{df['word_count'].min():,}"
    )

    print(
        f"Maximum words    : "
        f"{df['word_count'].max():,}"
    )

    print(
        f"Mean words       : "
        f"{df['word_count'].mean():.2f}"
    )

    oversized = df[
        df["word_count"]
        > CHUNK_SIZE
    ]

    print(
        f"Oversized chunks : "
        f"{len(oversized):,}"
    )

    if len(oversized) > 0:
        raise RuntimeError(
            "Chunk size validation failed."
        )


def build_summary(
    chunk_datasets: dict[
        str,
        pd.DataFrame
    ]
) -> pd.DataFrame:

    rows = []

    for (
        split_name,
        df,
    ) in (
        chunk_datasets.items()
    ):

        rows.append(
            {
                "split": split_name,
                "chunks": len(df),
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
                "mean_words": (
                    df[
                        "word_count"
                    ]
                    .mean()
                ),
                "max_words": (
                    df[
                        "word_count"
                    ]
                    .max()
                ),
            }
        )

    return pd.DataFrame(
        rows
    )


def main() -> None:

    print_header(
        "DAY 6 - BUILDING "
        "TRANSFORMER CHUNKS"
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    chunk_datasets = {}

    for split_name in [
        "train",
        "validation",
        "test",
    ]:

        print(
            f"\nProcessing "
            f"{split_name}..."
        )

        split_df = load_split(
            split_name
        )

        chunk_df = build_chunks(
            split_df,
            split_name,
        )

        validate_chunks(
            chunk_df,
            split_name,
        )

        output_path = (
            OUTPUT_DIR
            / f"{split_name}_chunks.csv"
        )

        chunk_df.to_csv(
            output_path,
            index=False,
            encoding="utf-8",
        )

        chunk_datasets[
            split_name
        ] = chunk_df

        print(
            f"Saved:\n"
            f"{output_path}"
        )

    summary = build_summary(
        chunk_datasets
    )

    summary.to_csv(
        SUMMARY_PATH,
        index=False,
    )

    print_header(
        "CHUNK SUMMARY"
    )

    print(
        summary.to_string(
            index=False
        )
    )

    print(
        f"\nSummary saved to:\n"
        f"{SUMMARY_PATH}"
    )

    print(
        "\nDay 6 chunking "
        "completed successfully."
    )


if __name__ == "__main__":
    main()