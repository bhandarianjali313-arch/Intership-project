"""
Contract-level dataset splitting utilities.
"""
import random
from typing import Iterable, Set, Tuple

import pandas as pd


def split_contract_ids(
    contract_ids: Iterable,
    train_ratio: float = 0.70,
    validation_ratio: float = 0.15,
    test_ratio: float = 0.15,
    random_seed: int = 42,
) -> Tuple[Set, Set, Set]:
    """
    Split a collection of contract IDs into train/validation/test sets
    at the contract level (no contract overlap allowed).

    Default split: 70% / 15% / 15%.
    """
    if abs((train_ratio + validation_ratio + test_ratio) - 1.0) > 1e-9:
        raise ValueError(
            "train_ratio + validation_ratio + test_ratio must equal 1.0 "
            f"(got {train_ratio + validation_ratio + test_ratio})"
        )

    ids = list(contract_ids)
    rng = random.Random(random_seed)
    rng.shuffle(ids)

    n = len(ids)
    train_end = int(n * train_ratio)
    val_end = train_end + int(n * validation_ratio)

    train_ids = set(ids[:train_end])
    validation_ids = set(ids[train_end:val_end])
    test_ids = set(ids[val_end:])

    return train_ids, validation_ids, test_ids


def assign_split_column(
    df: pd.DataFrame,
    train_ratio: float = 0.70,
    validation_ratio: float = 0.15,
    test_ratio: float = 0.15,
    random_seed: int = 42,
    contract_column: str = "contract_id",
    split_column: str = "split",
) -> pd.DataFrame:
    """Assign a 'split' label to every row, preserving contract integrity."""
    df = df.copy()

    unique_contracts = df[contract_column].unique().tolist()
    train_ids, val_ids, test_ids = split_contract_ids(
        unique_contracts,
        train_ratio=train_ratio,
        validation_ratio=validation_ratio,
        test_ratio=test_ratio,
        random_seed=random_seed,
    )

    def _resolve_split(cid) -> str:
        if cid in train_ids:
            return "train"
        if cid in val_ids:
            return "validation"
        return "test"

    df[split_column] = df[contract_column].apply(_resolve_split)
    return df


def validate_no_contract_leakage(
    df: pd.DataFrame,
    contract_column: str = "contract_id",
    split_column: str = "split",
) -> bool:
    """Return True if every contract_id appears in exactly one split."""
    if contract_column not in df.columns or split_column not in df.columns:
        return True

    splits_per_contract = df.groupby(contract_column)[split_column].nunique()
    return bool((splits_per_contract == 1).all())
