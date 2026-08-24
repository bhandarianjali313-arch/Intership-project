from __future__ import annotations

from pathlib import Path
import json
import time

import numpy as np
import pandas as pd
import torch

from datasets import Dataset

from sklearn.metrics import (
    classification_report,
)

from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
)

from ml.src.classification.transformer_utils import (
    prepare_transformer_dataframe,
    tokenize_batch,
    trainer_metrics,
)


# ============================================================
# Project paths
# ============================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "classification"
)

TRAIN_PATH = (
    DATA_DIR
    / "train.csv"
)

VALIDATION_PATH = (
    DATA_DIR
    / "validation.csv"
)

TEST_PATH = (
    DATA_DIR
    / "test.csv"
)

LABEL_MAPPING_PATH = (
    DATA_DIR
    / "label_mapping.json"
)


MODEL_DIR = (
    PROJECT_ROOT
    / "models"
    / "legal_bert_baseline"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "classification"
    / "transformer"
)


# ============================================================
# Model configuration
# ============================================================

MODEL_NAME = (
    "nlpaueb/legal-bert-base-uncased"
)

MAX_LENGTH = 256

LEARNING_RATE = 2e-5

RANDOM_SEED = 42


# ============================================================
# Training mode
# ============================================================

# True:
# small local CPU test.
#
# False:
# full dataset training.
#
# Keep True while testing locally.
SMOKE_TEST = True


if SMOKE_TEST:

    TRAIN_BATCH_SIZE = 4
    EVAL_BATCH_SIZE = 8
    NUM_EPOCHS = 1

else:

    TRAIN_BATCH_SIZE = 8
    EVAL_BATCH_SIZE = 16
    NUM_EPOCHS = 2


# ============================================================
# Utility
# ============================================================

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


# ============================================================
# Dataset loading
# ============================================================

def load_dataframe(
    path: Path,
) -> pd.DataFrame:

    if not path.exists():

        raise FileNotFoundError(
            f"{path} not found.\n"
            "Run Day 9 first:\n"
            "python -m "
            "ml.scripts.build_classification_dataset"
        )

    df = pd.read_csv(
        path
    )

    return (
        prepare_transformer_dataframe(
            df
        )
    )


# ============================================================
# Label mapping
# ============================================================

def load_label_mapping():

    if not LABEL_MAPPING_PATH.exists():

        raise FileNotFoundError(
            "label_mapping.json not found.\n"
            "Run Day 9 classification "
            "dataset builder first."
        )

    with LABEL_MAPPING_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:

        mapping = json.load(
            file
        )

    label_to_id = {
        label: int(
            label_id
        )
        for label, label_id
        in mapping[
            "label_to_id"
        ].items()
    }

    id_to_label = {
        int(
            label_id
        ): label
        for label_id, label
        in mapping[
            "id_to_label"
        ].items()
    }

    return (
        label_to_id,
        id_to_label,
    )


# ============================================================
# Hugging Face dataset conversion
# ============================================================

def dataframe_to_dataset(
    dataframe: pd.DataFrame,
) -> Dataset:

    dataset = Dataset.from_pandas(
        dataframe[
            [
                "cleaned_clause_text",
                "label_id",
            ]
        ],
        preserve_index=False,
    )

    dataset = (
        dataset.rename_column(
            "label_id",
            "labels",
        )
    )

    return dataset


# ============================================================
# Tokenization
# ============================================================

def tokenize_dataset(
    dataset: Dataset,
    tokenizer,
) -> Dataset:

    return dataset.map(
        lambda batch: tokenize_batch(
            {
                "cleaned_clause_text":
                    batch[
                        "cleaned_clause_text"
                    ]
            },
            tokenizer=tokenizer,
            max_length=MAX_LENGTH,
        ),
        batched=True,
        remove_columns=[
            "cleaned_clause_text"
        ],
    )


# ============================================================
# Metrics saving
# ============================================================

def save_metrics(
    metrics: dict,
    filename: str,
) -> None:

    path = (
        OUTPUT_DIR
        / filename
    )

    clean_metrics = {}

    for key, value in (
        metrics.items()
    ):

        if isinstance(
            value,
            (
                np.floating,
                float,
                int,
            ),
        ):

            clean_metrics[
                key
            ] = float(
                value
            )

        else:

            clean_metrics[
                key
            ] = value

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            clean_metrics,
            file,
            indent=2,
        )


# ============================================================
# Pretty metrics output
# ============================================================

def print_metrics(
    title: str,
    metrics: dict,
) -> None:

    print_header(
        title
    )

    possible_metrics = [
        "eval_accuracy",
        "eval_macro_precision",
        "eval_macro_recall",
        "eval_macro_f1",
        "eval_weighted_f1",

        "test_accuracy",
        "test_macro_precision",
        "test_macro_recall",
        "test_macro_f1",
        "test_weighted_f1",
    ]

    for key in (
        possible_metrics
    ):

        if key in metrics:

            print(
                f"{key:<25}: "
                f"{metrics[key]:.4f}"
            )


# ============================================================
# Test prediction report
# ============================================================

def build_test_report(
    trainer: Trainer,
    test_dataset: Dataset,
    test_df: pd.DataFrame,
    id_to_label: dict[int, str],
) -> None:

    prediction_output = (
        trainer.predict(
            test_dataset
        )
    )

    logits = (
        prediction_output.predictions
    )

    predictions = np.argmax(
        logits,
        axis=-1,
    )

    labels = (
        test_df[
            "label_id"
        ]
        .astype(int)
        .to_numpy()
    )

    target_ids = sorted(
        id_to_label.keys()
    )

    target_names = [
        id_to_label[
            label_id
        ]
        for label_id
        in target_ids
    ]

    report = classification_report(
        labels,
        predictions,
        labels=target_ids,
        target_names=target_names,
        output_dict=True,
        zero_division=0,
    )

    report_df = (
        pd.DataFrame(
            report
        )
        .transpose()
    )

    report_df.to_csv(
        OUTPUT_DIR
        / "test_classification_report.csv"
    )

    prediction_df = test_df[
        [
            "contract_id",
            "cleaned_clause_text",
            "clause_label",
            "label_id",
        ]
    ].copy()

    prediction_df[
        "predicted_label_id"
    ] = predictions

    prediction_df[
        "predicted_label"
    ] = [
        id_to_label[
            int(
                label_id
            )
        ]
        for label_id
        in predictions
    ]

    prediction_df[
        "correct"
    ] = (
        prediction_df[
            "label_id"
        ]
        == prediction_df[
            "predicted_label_id"
        ]
    )

    prediction_df.to_csv(
        OUTPUT_DIR
        / "test_predictions.csv",
        index=False,
        encoding="utf-8",
    )


# ============================================================
# Main training pipeline
# ============================================================

def main() -> None:

    print_header(
        "DAY 12 - LEGAL-BERT "
        "CLAUSE CLASSIFICATION BASELINE"
    )

    device_name = (
        "CUDA GPU"
        if torch.cuda.is_available()
        else "CPU"
    )

    print(
        f"Device available: "
        f"{device_name}"
    )

    print(
        f"Model: {MODEL_NAME}"
    )

    print(
        f"Smoke test: "
        f"{SMOKE_TEST}"
    )

    print(
        f"Random seed: "
        f"{RANDOM_SEED}"
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    train_df = (
        load_dataframe(
            TRAIN_PATH
        )
    )

    validation_df = (
        load_dataframe(
            VALIDATION_PATH
        )
    )

    test_df = (
        load_dataframe(
            TEST_PATH
        )
    )


    # --------------------------------------------------------
    # CPU smoke test
    # --------------------------------------------------------

    if SMOKE_TEST:

        print_header(
            "CPU SMOKE TEST MODE"
        )

        print(
            "Using a small dataset "
            "to verify the pipeline."
        )

        train_df = (
            train_df.head(
                200
            )
        )

        validation_df = (
            validation_df.head(
                100
            )
        )

        test_df = (
            test_df.head(
                100
            )
        )


    # --------------------------------------------------------
    # Labels
    # --------------------------------------------------------

    (
        label_to_id,
        id_to_label,
    ) = (
        load_label_mapping()
    )

    num_labels = len(
        label_to_id
    )


    # --------------------------------------------------------
    # Dataset summary
    # --------------------------------------------------------

    print_header(
        "DATASET SUMMARY"
    )

    print(
        f"Training examples   : "
        f"{len(train_df):,}"
    )

    print(
        f"Validation examples : "
        f"{len(validation_df):,}"
    )

    print(
        f"Test examples       : "
        f"{len(test_df):,}"
    )

    print(
        f"Number of classes   : "
        f"{num_labels}"
    )


    # --------------------------------------------------------
    # Load tokenizer and model
    # --------------------------------------------------------

    print_header(
        "LOADING LEGAL-BERT"
    )

    tokenizer = (
        AutoTokenizer
        .from_pretrained(
            MODEL_NAME
        )
    )

    model = (
        AutoModelForSequenceClassification
        .from_pretrained(
            MODEL_NAME,
            num_labels=num_labels,
            label2id=label_to_id,
            id2label=id_to_label,
            ignore_mismatched_sizes=True,
        )
    )


    # --------------------------------------------------------
    # Convert datasets
    # --------------------------------------------------------

    train_dataset = (
        dataframe_to_dataset(
            train_df
        )
    )

    validation_dataset = (
        dataframe_to_dataset(
            validation_df
        )
    )

    test_dataset = (
        dataframe_to_dataset(
            test_df
        )
    )


    # --------------------------------------------------------
    # Tokenization
    # --------------------------------------------------------

    print_header(
        "TOKENIZATION"
    )

    train_dataset = (
        tokenize_dataset(
            train_dataset,
            tokenizer,
        )
    )

    validation_dataset = (
        tokenize_dataset(
            validation_dataset,
            tokenizer,
        )
    )

    test_dataset = (
        tokenize_dataset(
            test_dataset,
            tokenizer,
        )
    )

    print(
        "Tokenization completed."
    )


    # --------------------------------------------------------
    # Dynamic padding
    # --------------------------------------------------------

    data_collator = (
        DataCollatorWithPadding(
            tokenizer=tokenizer
        )
    )


    # --------------------------------------------------------
    # Training configuration
    # --------------------------------------------------------

    training_args = (
        TrainingArguments(

            output_dir=str(
                MODEL_DIR
            ),

            learning_rate=(
                LEARNING_RATE
            ),

            per_device_train_batch_size=(
                TRAIN_BATCH_SIZE
            ),

            per_device_eval_batch_size=(
                EVAL_BATCH_SIZE
            ),

            # Your current system is CPU-only.
            # Prevent unnecessary pinned-memory warning.
            dataloader_pin_memory=False,

            num_train_epochs=(
                NUM_EPOCHS
            ),

            weight_decay=0.01,

            eval_strategy="epoch",

            save_strategy="epoch",

            logging_strategy="steps",

            logging_steps=25,

            load_best_model_at_end=True,

            metric_for_best_model=(
                "macro_f1"
            ),

            greater_is_better=True,

            save_total_limit=1,

            seed=RANDOM_SEED,

            report_to="none",
        )
    )


    # --------------------------------------------------------
    # Trainer
    # --------------------------------------------------------

    trainer = Trainer(

        model=model,

        args=training_args,

        train_dataset=(
            train_dataset
        ),

        eval_dataset=(
            validation_dataset
        ),

        data_collator=(
            data_collator
        ),

        compute_metrics=(
            trainer_metrics
        ),
    )


    # --------------------------------------------------------
    # Training
    # --------------------------------------------------------

    print_header(
        "MODEL TRAINING"
    )

    start_time = (
        time.time()
    )

    trainer.train()

    training_seconds = (
        time.time()
        - start_time
    )

    print(
        f"\nTraining completed in "
        f"{training_seconds:.2f}s"
    )


    # --------------------------------------------------------
    # Validation evaluation
    # --------------------------------------------------------

    validation_metrics = (
        trainer.evaluate(
            validation_dataset
        )
    )

    print_metrics(
        "VALIDATION METRICS",
        validation_metrics,
    )


    # --------------------------------------------------------
    # Test evaluation
    # --------------------------------------------------------

    test_output = (
        trainer.predict(
            test_dataset
        )
    )

    test_metrics = (
        test_output.metrics
    )

    print_metrics(
        "TEST METRICS",
        test_metrics,
    )


    # --------------------------------------------------------
    # Save metrics
    # --------------------------------------------------------

    save_metrics(
        validation_metrics,
        "validation_metrics.json",
    )

    save_metrics(
        test_metrics,
        "test_metrics.json",
    )


    # --------------------------------------------------------
    # Detailed test report
    # --------------------------------------------------------

    build_test_report(
        trainer,
        test_dataset,
        test_df,
        id_to_label,
    )


    # --------------------------------------------------------
    # Save final model
    # --------------------------------------------------------

    print_header(
        "SAVING MODEL"
    )

    trainer.save_model(
        MODEL_DIR
    )

    tokenizer.save_pretrained(
        MODEL_DIR
    )


    # --------------------------------------------------------
    # Run summary
    # --------------------------------------------------------

    run_summary = {

        "model": MODEL_NAME,

        "smoke_test": (
            SMOKE_TEST
        ),

        "max_length": (
            MAX_LENGTH
        ),

        "epochs": (
            NUM_EPOCHS
        ),

        "train_batch_size": (
            TRAIN_BATCH_SIZE
        ),

        "eval_batch_size": (
            EVAL_BATCH_SIZE
        ),

        "learning_rate": (
            LEARNING_RATE
        ),

        "training_examples": (
            len(train_df)
        ),

        "validation_examples": (
            len(validation_df)
        ),

        "test_examples": (
            len(test_df)
        ),

        "num_labels": (
            num_labels
        ),

        "device": (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        ),

        "training_seconds": (
            training_seconds
        ),

        "validation_metrics": (
            validation_metrics
        ),

        "test_metrics": (
            test_metrics
        ),
    }

    with (
        OUTPUT_DIR
        / "run_summary.json"
    ).open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            run_summary,
            file,
            indent=2,
            default=float,
        )


    # --------------------------------------------------------
    # Complete
    # --------------------------------------------------------

    print(
        f"Model saved to:\n"
        f"{MODEL_DIR}"
    )

    print(
        f"\nOutputs saved to:\n"
        f"{OUTPUT_DIR}"
    )

    print_header(
        "DAY 12 COMPLETE"
    )


if __name__ == "__main__":
    main()