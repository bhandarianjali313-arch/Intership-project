from __future__ import annotations

import random
from collections import Counter
from typing import Iterable

import pandas as pd


def split_contract_ids(
    contract_ids: Iterable[int],
    train_ratio: float = 0.70,
    validation_ratio: float = 0.15,
    test_ratio: float = 0.15,
    random_seed: int = 42,
) -> tuple[set[int], set[int], set[int]]:
    """
    Split unique contract IDs into train, validation and test sets.

    The split happens at contract level to prevent leakage.
    """

    total_ratio = (
        train_ratio
        + validation_ratio
        + test_ratio
    )

    if abs(total_ratio - 1.0) > 1e-9:
        raise ValueError(
            "train_ratio + validation_ratio + test_ratio "
            "must equal 1.0"
        )

    unique_ids = sorted(
        set(contract_ids)
    )

    if not unique_ids:
        raise ValueError(
            "No contract IDs provided."
        )

    random_generator = random.Random(
        random_seed
    )

    random_generator.shuffle(
        unique_ids
    )

    total_contracts = len(
        unique_ids
    )

    train_end = int(
        total_contracts
        * train_ratio
    )

    validation_end = (
        train_end
        + int(
            total_contracts
            * validation_ratio
        )
    )

    train_ids = set(
        unique_ids[:train_end]
    )

    validation_ids = set(
        unique_ids[
            train_end:validation_end
        ]
    )

    test_ids = set(
        unique_ids[
            validation_end:
        ]
    )

    return (
        train_ids,
        validation_ids,
        test_ids,
    )


def assign_split_column(
    df: pd.DataFrame,
    random_seed: int = 42,
) -> pd.DataFrame:
    """
    Add a `split` column based on contract-level grouping.
    """

    df = df.copy()

    (
        train_ids,
        validation_ids,
        test_ids,
    ) = split_contract_ids(
        df["contract_id"],
        random_seed=random_seed,
    )

    def get_split(
        contract_id: int
    ) -> str:

        if contract_id in train_ids:
            return "train"

        if contract_id in validation_ids:
            return "validation"

        if contract_id in test_ids:
            return "test"

        raise ValueError(
            f"Contract {contract_id} was not assigned."
        )

    df["split"] = (
        df["contract_id"]
        .apply(get_split)
    )

    return df


def validate_no_contract_leakage(
    df: pd.DataFrame
) -> bool:
    """
    Verify that every contract appears in only one split.
    """

    grouped = (
        df.groupby("contract_id")["split"]
        .nunique()
    )

    leaking_contracts = grouped[
        grouped > 1
    ]

    return leaking_contracts.empty


def get_split_contract_counts(
    df: pd.DataFrame
) -> dict[str, int]:
    """
    Count unique contracts per split.
    """

    return (
        df.groupby("split")["contract_id"]
        .nunique()
        .to_dict()
    )


def get_split_row_counts(
    df: pd.DataFrame
) -> dict[str, int]:
    """
    Count records per split.
    """

    return (
        df["split"]
        .value_counts()
        .to_dict()
    )


def get_label_presence(
    df: pd.DataFrame,
    split_name: str,
) -> Counter:
    """
    Count positive examples per label in one split.
    """

    subset = df[
        (df["split"] == split_name)
        &
        (df["has_answer"] == True)
    ]

    return Counter(
        subset["clause_label"]
    )