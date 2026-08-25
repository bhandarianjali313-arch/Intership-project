from __future__ import annotations

from pathlib import Path
import json
import time

import numpy as np
import pandas as pd
import torch

from datasets import Dataset
from sklearn.metrics import classification_report

from transformers import (
    AutoConfig,
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    TrainingArguments,
)

from ml.src.classification.transformer_utils import (
    prepare_transformer_dataframe,
    tokenize_batch,
    trainer_metrics,
)

from ml.src.classification.weighted_trainer import (
    WeightedTrainer,
    calculate_class_weights,
)


# =============================================================================
# PROJECT PATHS
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "classification"
)

TRAIN_PATH = DATA_DIR / "train.csv"

VALIDATION_PATH = (
    DATA_DIR
    / "validation.csv"
)

TEST_PATH = DATA_DIR / "test.csv"

LABEL_MAPPING_PATH = (
    DATA_DIR
    / "label_mapping.json"
)


MODEL_DIR = (
    PROJECT_ROOT
    / "models"
    / "legal_bert_weighted"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "classification"
    / "transformer_weighted"
)


# =============================================================================
# MODEL
# =============================================================================

MODEL_NAME = "nlpaueb/legal-bert-base-uncased"

LEARNING_RATE = 2e-5

RANDOM_SEED = 42


# =============================================================================
# DEVICE CONFIGURATION
# =============================================================================

USE_CUDA = torch.cuda.is_available()


# GPU configuration
if USE_CUDA:

    MAX_LENGTH = 256

    TRAIN_BATCH_SIZE = 8

    EVAL_BATCH_SIZE = 16

    NUM_EPOCHS = 2


# CPU configuration
else:

    MAX_LENGTH = 96

    TRAIN_BATCH_SIZE = 8

    EVAL_BATCH_SIZE = 8

    NUM_EPOCHS = 1


# =============================================================================
# PRINT UTILITIES
# =============================================================================

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


# =============================================================================
# DATA LOADING
# =============================================================================

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

    dataframe = pd.read_csv(
        path
    )

    return (
        prepare_transformer_dataframe(
            dataframe
        )
    )


# =============================================================================
# LABEL MAPPING
# =============================================================================

def load_label_mapping():

    if not LABEL_MAPPING_PATH.exists():

        raise FileNotFoundError(
            f"{LABEL_MAPPING_PATH} "
            "not found."
        )

    with LABEL_MAPPING_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:

        mapping = json.load(
            file
        )

    label_to_id = {

        label: int(label_id)

        for label, label_id
        in mapping[
            "label_to_id"
        ].items()
    }

    id_to_label = {

        int(label_id): label

        for label_id, label
        in mapping[
            "id_to_label"
        ].items()
    }

    return (
        label_to_id,
        id_to_label,
    )


# =============================================================================
# DATASET CONVERSION
# =============================================================================

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


# =============================================================================
# TOKENIZATION
# =============================================================================

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


# =============================================================================
# SAVE JSON
# =============================================================================

def save_json(
    data: dict,
    path: Path,
) -> None:

    cleaned = {}

    for key, value in (
        data.items()
    ):

        if isinstance(
            value,
            (
                np.floating,
                np.integer,
            ),
        ):

            value = value.item()

        cleaned[key] = value

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            cleaned,
            file,
            indent=2,
            default=float,
        )


# =============================================================================
# PRINT METRICS
# =============================================================================

def print_metrics(
    title: str,
    metrics: dict,
) -> None:

    print_header(
        title
    )

    metric_keys = [

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

    for key in metric_keys:

        if key in metrics:

            print(
                f"{key:<25}: "
                f"{metrics[key]:.4f}"
            )


# =============================================================================
# CLASS WEIGHTS
# =============================================================================

def save_class_weights(
    weights: np.ndarray,
    id_to_label: dict[int, str],
) -> None:

    output = {}

    for class_id, weight in enumerate(
        weights
    ):

        output[
            id_to_label[
                class_id
            ]
        ] = float(weight)

    path = (
        OUTPUT_DIR
        / "class_weights.json"
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            output,
            file,
            indent=2,
        )


# =============================================================================
# SAVE TEST OUTPUT
# =============================================================================

def save_test_outputs(
    prediction_output,
    test_df: pd.DataFrame,
    id_to_label: dict[int, str],
) -> None:

    logits = (
        prediction_output.predictions
    )

    predictions = np.argmax(
        logits,
        axis=-1,
    )

    true_labels = (

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

    report = (
        classification_report(

            true_labels,

            predictions,

            labels=target_ids,

            target_names=target_names,

            output_dict=True,

            zero_division=0,
        )
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


    result_df = (

        test_df[
            [
                "contract_id",
                "cleaned_clause_text",
                "clause_label",
                "label_id",
            ]
        ]
        .copy()
    )

    result_df[
        "predicted_label_id"
    ] = predictions


    result_df[
        "predicted_label"
    ] = [

        id_to_label[
            int(label_id)
        ]

        for label_id
        in predictions
    ]


    result_df[
        "correct"
    ] = (

        result_df[
            "label_id"
        ]

        ==

        result_df[
            "predicted_label_id"
        ]
    )


    result_df.to_csv(

        OUTPUT_DIR
        / "test_predictions.csv",

        index=False,

        encoding="utf-8",
    )


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:

    print_header(
        "DAY 13 - CLASS-WEIGHTED LEGAL-BERT"
    )


    # =========================================================================
    # OUTPUT DIRECTORIES
    # =========================================================================

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    # =========================================================================
    # DEVICE INFORMATION
    # =========================================================================

    if USE_CUDA:

        device_name = (
            torch.cuda
            .get_device_name(0)
        )

        print(
            f"Device: CUDA GPU "
            f"({device_name})"
        )

    else:

        device_name = "CPU"

        print(
            "Device: CPU"
        )

        print(
            "\nCPU MODE ENABLED"
        )

        print(
            "Reduced configuration "
            "will be used to keep "
            "training practical."
        )


    # =========================================================================
    # TRAINING CONFIGURATION
    # =========================================================================

    print_header(
        "TRAINING CONFIGURATION"
    )

    print(
        f"Model                : "
        f"{MODEL_NAME}"
    )

    print(
        f"Max token length     : "
        f"{MAX_LENGTH}"
    )

    print(
        f"Train batch size     : "
        f"{TRAIN_BATCH_SIZE}"
    )

    print(
        f"Evaluation batch size: "
        f"{EVAL_BATCH_SIZE}"
    )

    print(
        f"Learning rate        : "
        f"{LEARNING_RATE}"
    )

    print(
        f"Epochs               : "
        f"{NUM_EPOCHS}"
    )


    # =========================================================================
    # LOAD DATA
    # =========================================================================

    print_header(
        "LOADING DATASET"
    )

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


    (
        label_to_id,
        id_to_label,
    ) = (
        load_label_mapping()
    )


    num_labels = len(
        label_to_id
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
        f"Classes             : "
        f"{num_labels}"
    )


    # =========================================================================
    # CLASS WEIGHTS
    # =========================================================================

    print_header(
        "CALCULATING CLASS WEIGHTS"
    )


    class_weights = (
        calculate_class_weights(

            train_df[
                "label_id"
            ].astype(int),

            num_classes=(
                num_labels
            ),
        )
    )


    save_class_weights(
        class_weights,
        id_to_label,
    )


    weight_table = (
        pd.DataFrame(
            {

                "label_id":
                    range(
                        num_labels
                    ),

                "label":
                    [
                        id_to_label[i]
                        for i in range(
                            num_labels
                        )
                    ],

                "weight":
                    class_weights,
            }
        )
    )


    print(
        weight_table
        .sort_values(
            "weight",
            ascending=False,
        )
        .head(10)
        .to_string(
            index=False
        )
    )


    # =========================================================================
    # TOKENIZER
    # =========================================================================

    print_header(
        "LOADING LEGAL-BERT TOKENIZER"
    )


    tokenizer = (
        AutoTokenizer
        .from_pretrained(
            MODEL_NAME
        )
    )


    # =========================================================================
    # MODEL CONFIGURATION
    # =========================================================================

    print_header(
        "CREATING 41-CLASS MODEL CONFIGURATION"
    )


    config = (
        AutoConfig
        .from_pretrained(
            MODEL_NAME
        )
    )


    # Override original model label configuration
    config.num_labels = (
        num_labels
    )

    config.label2id = (
        label_to_id
    )

    config.id2label = (
        id_to_label
    )


    print(
        f"Configured labels: "
        f"{config.num_labels}"
    )


    # =========================================================================
    # LOAD MODEL
    # =========================================================================

    print_header(
        "LOADING LEGAL-BERT MODEL"
    )


    model = (
        AutoModelForSequenceClassification
        .from_pretrained(

            MODEL_NAME,

            config=config,
        )
    )


    print(
        "\nLegal-BERT backbone loaded."
    )

    print(
        "New 41-class classification "
        "head initialized."
    )


    # =========================================================================
    # DATASET CONVERSION
    # =========================================================================

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


    # =========================================================================
    # TOKENIZATION
    # =========================================================================

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
        "Tokenization complete."
    )


    # =========================================================================
    # DATA COLLATOR
    # =========================================================================

    data_collator = (
        DataCollatorWithPadding(
            tokenizer=tokenizer
        )
    )


    # =========================================================================
    # TRAINING ARGUMENTS
    # =========================================================================

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

            num_train_epochs=(
                NUM_EPOCHS
            ),

            weight_decay=0.01,

            eval_strategy="epoch",

            save_strategy="epoch",

            load_best_model_at_end=True,

            metric_for_best_model=(
                "macro_f1"
            ),

            greater_is_better=True,

            save_total_limit=1,

            logging_strategy="steps",

            logging_steps=100,

            seed=RANDOM_SEED,

            report_to="none",

            # Only use pinned memory when
            # CUDA is actually available.
            dataloader_pin_memory=(
                USE_CUDA
            ),
        )
    )


    # =========================================================================
    # WEIGHTED TRAINER
    # =========================================================================

    trainer = (
        WeightedTrainer(

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

            class_weights=(
                class_weights
            ),
        )
    )


    # =========================================================================
    # TRAINING
    # =========================================================================

    print_header(
        "TRAINING WEIGHTED MODEL"
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
        f"{training_seconds:.2f} seconds"
    )


    # =========================================================================
    # VALIDATION
    # =========================================================================

    validation_metrics = (
        trainer.evaluate(
            validation_dataset
        )
    )


    print_metrics(
        "VALIDATION METRICS",
        validation_metrics,
    )


    # =========================================================================
    # TEST
    # =========================================================================

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


    # =========================================================================
    # SAVE METRICS
    # =========================================================================

    save_json(

        validation_metrics,

        OUTPUT_DIR
        / "validation_metrics.json",
    )


    save_json(

        test_metrics,

        OUTPUT_DIR
        / "test_metrics.json",
    )


    # =========================================================================
    # SAVE PREDICTIONS
    # =========================================================================

    save_test_outputs(

        test_output,

        test_df,

        id_to_label,
    )


    # =========================================================================
    # SAVE MODEL
    # =========================================================================

    print_header(
        "SAVING MODEL"
    )


    trainer.save_model(
        MODEL_DIR
    )


    tokenizer.save_pretrained(
        MODEL_DIR
    )


    print(
        f"Model saved to:\n"
        f"{MODEL_DIR}"
    )


    # =========================================================================
    # EXPERIMENT SUMMARY
    # =========================================================================

    run_summary = {

        "model":
            MODEL_NAME,

        "training_strategy":
            "class_weighted_cross_entropy",

        "device":
            device_name,

        "max_length":
            MAX_LENGTH,

        "epochs":
            NUM_EPOCHS,

        "learning_rate":
            LEARNING_RATE,

        "train_batch_size":
            TRAIN_BATCH_SIZE,

        "eval_batch_size":
            EVAL_BATCH_SIZE,

        "training_examples":
            len(train_df),

        "validation_examples":
            len(validation_df),

        "test_examples":
            len(test_df),

        "num_labels":
            num_labels,

        "training_seconds":
            training_seconds,

        "validation_metrics":
            validation_metrics,

        "test_metrics":
            test_metrics,
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


    # =========================================================================
    # DONE
    # =========================================================================

    print_header(
        "DAY 13 COMPLETE"
    )


    print(
        "Class-weighted Legal-BERT "
        "training completed successfully."
    )


    print(
        f"\nResults saved to:\n"
        f"{OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()