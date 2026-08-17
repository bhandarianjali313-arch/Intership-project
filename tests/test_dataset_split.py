import pandas as pd

from ml.src.preprocessing.split_utils import (
    assign_split_column,
    split_contract_ids,
    validate_no_contract_leakage,
)


def test_split_ratios_sum_validation():

    contract_ids = list(
        range(100)
    )

    train_ids, validation_ids, test_ids = (
        split_contract_ids(
            contract_ids,
            random_seed=42,
        )
    )

    assert len(
        train_ids
    ) == 70

    assert len(
        validation_ids
    ) == 15

    assert len(
        test_ids
    ) == 15


def test_contracts_do_not_overlap():

    contract_ids = list(
        range(100)
    )

    train_ids, validation_ids, test_ids = (
        split_contract_ids(
            contract_ids,
            random_seed=42,
        )
    )

    assert train_ids.isdisjoint(
        validation_ids
    )

    assert train_ids.isdisjoint(
        test_ids
    )

    assert validation_ids.isdisjoint(
        test_ids
    )


def test_split_is_reproducible():

    ids = list(
        range(50)
    )

    split_a = split_contract_ids(
        ids,
        random_seed=42,
    )

    split_b = split_contract_ids(
        ids,
        random_seed=42,
    )

    assert split_a == split_b


def test_dataframe_has_no_leakage():

    df = pd.DataFrame(
        {
            "contract_id": [
                1,
                1,
                2,
                2,
                3,
                3,
                4,
                4,
            ],
            "clause_label": [
                "A",
                "B",
                "A",
                "C",
                "B",
                "C",
                "A",
                "B",
            ],
            "has_answer": [
                True,
                False,
                True,
                True,
                False,
                True,
                True,
                False,
            ],
        }
    )

    result = assign_split_column(
        df,
        random_seed=42,
    )

    assert (
        validate_no_contract_leakage(
            result
        )
        is True
    )


def test_invalid_ratios_raise_error():

    try:

        split_contract_ids(
            range(20),
            train_ratio=0.8,
            validation_ratio=0.2,
            test_ratio=0.2,
        )

        assert False

    except ValueError:

        assert True