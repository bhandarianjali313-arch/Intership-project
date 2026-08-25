from __future__ import annotations

from typing import Iterable

import numpy as np
import torch

from transformers import Trainer


def calculate_class_weights(
    labels: Iterable[int],
    num_classes: int,
) -> np.ndarray:
    """
    Calculate balanced class weights.

    Weight formula:

        total_samples
        ------------------------
        num_classes * class_count

    Rare classes therefore receive higher weights.
    """

    labels = np.asarray(
        list(labels),
        dtype=np.int64,
    )

    if len(labels) == 0:
        raise ValueError(
            "Cannot calculate class weights "
            "from an empty label collection."
        )

    if num_classes <= 0:
        raise ValueError(
            "num_classes must be positive."
        )

    counts = np.bincount(
        labels,
        minlength=num_classes,
    )

    if np.any(counts == 0):
        missing_classes = np.where(
            counts == 0
        )[0]

        raise ValueError(
            "Training data is missing class IDs: "
            f"{missing_classes.tolist()}"
        )

    total_samples = len(labels)

    weights = (
        total_samples
        /
        (
            num_classes
            * counts
        )
    )

    return weights.astype(
        np.float32
    )


class WeightedTrainer(Trainer):
    """
    Hugging Face Trainer using class-weighted
    cross-entropy loss.
    """

    def __init__(
        self,
        *args,
        class_weights=None,
        **kwargs,
    ):

        super().__init__(
            *args,
            **kwargs,
        )

        if class_weights is None:
            raise ValueError(
                "class_weights are required."
            )

        self.class_weights = torch.tensor(
            class_weights,
            dtype=torch.float32,
        )


    def compute_loss(
        self,
        model,
        inputs,
        return_outputs=False,
        num_items_in_batch=None,
    ):
        """
        Replace the default unweighted loss with
        class-weighted CrossEntropyLoss.
        """

        labels = inputs.get(
            "labels"
        )

        outputs = model(
            **inputs
        )

        logits = outputs.get(
            "logits"
        )

        weights = (
            self.class_weights
            .to(logits.device)
        )

        loss_function = (
            torch.nn.CrossEntropyLoss(
                weight=weights
            )
        )

        loss = loss_function(
            logits.view(
                -1,
                model.config.num_labels,
            ),
            labels.view(-1),
        )

        if return_outputs:
            return (
                loss,
                outputs,
            )

        return loss