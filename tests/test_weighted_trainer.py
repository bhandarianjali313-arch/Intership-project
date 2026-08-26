import numpy as np
import pytest

from ml.src.classification.weighted_trainer import (
    calculate_class_weights,
)


def test_class_weight_count():

    labels = [
        0,
        0,
        1,
        1,
        2,
    ]

    weights = (
        calculate_class_weights(
            labels,
            num_classes=3,
        )
    )

    assert len(
        weights
    ) == 3


def test_rare_class_has_larger_weight():

    labels = [
        0,
        0,
        0,
        0,
        1,
    ]

    weights = (
        calculate_class_weights(
            labels,
            num_classes=2,
        )
    )

    assert (
        weights[1]
        > weights[0]
    )


def test_weights_are_positive():

    labels = [
        0,
        0,
        1,
        1,
    ]

    weights = (
        calculate_class_weights(
            labels,
            num_classes=2,
        )
    )

    assert np.all(
        weights > 0
    )


def test_empty_labels_raise():

    with pytest.raises(
        ValueError
    ):

        calculate_class_weights(
            [],
            num_classes=2,
        )


def test_missing_training_class_raises():

    labels = [
        0,
        0,
        1,
        1,
    ]

    with pytest.raises(
        ValueError
    ):

        calculate_class_weights(
            labels,
            num_classes=3,
        )


def test_more_frequent_class_gets_smaller_weight():

    labels = (
        [0] * 100
        + [1] * 10
        + [2] * 2
    )

    weights = (
        calculate_class_weights(
            labels,
            num_classes=3,
        )
    )

    assert (
        weights[0]
        < weights[1]
        < weights[2]
    )