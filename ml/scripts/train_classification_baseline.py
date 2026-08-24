from pathlib import Path
import json
import time

import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from ml.src.classification.baseline_model import (
    create_classifier,
    create_vectorizer,
    fit_vectorizer,
    predict_with_confidence,
    train_classifier,
    transform_texts,
)


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

MODEL_DIR = (
    PROJECT_ROOT
    / "models"
    / "classification"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "classification"
    / "baseline"
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


def load_dataset(
    path: Path,
) -> pd.DataFrame:

    if not path.exists():
        raise FileNotFoundError(
            f"{path} does not exist.\n"
            "Run Day 9 first:\n"
            "python -m "
            "ml.scripts.build_classification_dataset"
        )

    df = pd.read_csv(path)

    df[
        "cleaned_clause_text"
    ] = (
        df[
            "cleaned_clause_text"
        ]
        .fillna("")
        .astype(str)
    )

    return df


def load_label_mapping() -> dict:

    if not LABEL_MAPPING_PATH.exists():
        raise FileNotFoundError(
            "label_mapping.json not found."
        )

    with LABEL_MAPPING_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def calculate_metrics(
    y_true,
    y_pred,
) -> dict:

    return {
        "accuracy": float(
            accuracy_score(
                y_true,
                y_pred,
            )
        ),
        "macro_precision": float(
            precision_score(
                y_true,
                y_pred,
                average="macro",
                zero_division=0,
            )
        ),
        "macro_recall": float(
            recall_score(
                y_true,
                y_pred,
                average="macro",
                zero_division=0,
            )
        ),
        "macro_f1": float(
            f1_score(
                y_true,
                y_pred,
                average="macro",
                zero_division=0,
            )
        ),
        "weighted_f1": float(
            f1_score(
                y_true,
                y_pred,
                average="weighted",
                zero_division=0,
            )
        ),
    }


def evaluate_split(
    split_name: str,
    df: pd.DataFrame,
    features,
    classifier,
    labels: list[int],
    target_names: list[str],
) -> dict:

    y_true = (
        df["label_id"]
        .astype(int)
        .to_numpy()
    )

    (
        predictions,
        confidence,
    ) = predict_with_confidence(
        classifier,
        features,
    )

    metrics = calculate_metrics(
        y_true,
        predictions,
    )

    metrics[
        "mean_confidence"
    ] = float(
        confidence.mean()
    )

    print_header(
        f"{split_name.upper()} METRICS"
    )

    for key, value in (
        metrics.items()
    ):

        print(
            f"{key:<20}: "
            f"{value:.4f}"
        )

    report = classification_report(
        y_true,
        predictions,
        labels=labels,
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

    report_path = (
        OUTPUT_DIR
        / (
            f"{split_name}_"
            "classification_report.csv"
        )
    )

    report_df.to_csv(
        report_path
    )

    metrics_path = (
        OUTPUT_DIR
        / f"{split_name}_metrics.json"
    )

    with metrics_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metrics,
            file,
            indent=2,
        )

    prediction_output = df[
        [
            "contract_id",
            "cleaned_clause_text",
            "clause_label",
            "label_id",
        ]
    ].copy()

    prediction_output[
        "predicted_label_id"
    ] = predictions

    prediction_output[
        "confidence"
    ] = confidence

    prediction_output.to_csv(
        OUTPUT_DIR
        / f"{split_name}_predictions.csv",
        index=False,
        encoding="utf-8",
    )

    return {
        "metrics": metrics,
        "predictions": predictions,
        "y_true": y_true,
    }


def save_confusion_matrix(
    y_true,
    y_pred,
    labels: list[int],
    target_names: list[str],
) -> None:

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=labels,
    )

    matrix_df = pd.DataFrame(
        matrix,
        index=target_names,
        columns=target_names,
    )

    matrix_df.to_csv(
        OUTPUT_DIR
        / "confusion_matrix.csv"
    )


def main() -> None:

    print_header(
        "DAY 10 - TF-IDF + "
        "LOGISTIC REGRESSION BASELINE"
    )

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    train_df = load_dataset(
        TRAIN_PATH
    )

    validation_df = load_dataset(
        VALIDATION_PATH
    )

    test_df = load_dataset(
        TEST_PATH
    )

    mapping = (
        load_label_mapping()
    )

    label_to_id = mapping[
        "label_to_id"
    ]

    labels = sorted(
        label_to_id.values()
    )

    id_to_label = {
        int(key): value
        for key, value
        in mapping[
            "id_to_label"
        ].items()
    }

    target_names = [
        id_to_label[
            label_id
        ]
        for label_id in labels
    ]

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
        f"{len(labels)}"
    )

    vectorizer = (
        create_vectorizer()
    )

    classifier = (
        create_classifier()
    )

    print_header(
        "TF-IDF FEATURE EXTRACTION"
    )

    start_time = time.time()

    X_train = fit_vectorizer(
        vectorizer,
        train_df[
            "cleaned_clause_text"
        ],
    )

    X_validation = (
        transform_texts(
            vectorizer,
            validation_df[
                "cleaned_clause_text"
            ],
        )
    )

    X_test = transform_texts(
        vectorizer,
        test_df[
            "cleaned_clause_text"
        ],
    )

    feature_time = (
        time.time()
        - start_time
    )

    print(
        f"Vocabulary size : "
        f"{len(vectorizer.vocabulary_):,}"
    )

    print(
        f"Train matrix    : "
        f"{X_train.shape}"
    )

    print(
        f"Validation      : "
        f"{X_validation.shape}"
    )

    print(
        f"Test matrix     : "
        f"{X_test.shape}"
    )

    print(
        f"Feature time    : "
        f"{feature_time:.2f}s"
    )

    print_header(
        "MODEL TRAINING"
    )

    start_time = time.time()

    classifier = train_classifier(
        classifier,
        X_train,
        train_df[
            "label_id"
        ].astype(int),
    )

    training_time = (
        time.time()
        - start_time
    )

    print(
        f"Training completed in "
        f"{training_time:.2f}s"
    )

    validation_result = (
        evaluate_split(
            "validation",
            validation_df,
            X_validation,
            classifier,
            labels,
            target_names,
        )
    )

    test_result = (
        evaluate_split(
            "test",
            test_df,
            X_test,
            classifier,
            labels,
            target_names,
        )
    )

    save_confusion_matrix(
        test_result[
            "y_true"
        ],
        test_result[
            "predictions"
        ],
        labels,
        target_names,
    )

    print_header(
        "SAVING MODEL"
    )

    joblib.dump(
        vectorizer,
        MODEL_DIR
        / "tfidf_vectorizer.joblib",
    )

    joblib.dump(
        classifier,
        MODEL_DIR
        / "logistic_regression.joblib",
    )

    run_summary = {
        "model": (
            "TF-IDF + Logistic Regression"
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
        "num_classes": (
            len(labels)
        ),
        "vocabulary_size": (
            len(
                vectorizer.vocabulary_
            )
        ),
        "training_seconds": (
            training_time
        ),
        "validation_metrics": (
            validation_result[
                "metrics"
            ]
        ),
        "test_metrics": (
            test_result[
                "metrics"
            ]
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
        )

    print(
        "Vectorizer saved."
    )

    print(
        "Logistic Regression "
        "model saved."
    )

    print_header(
        "DAY 10 COMPLETE"
    )

    print(
        "Baseline model trained "
        "and evaluated successfully."
    )


if __name__ == "__main__":
    main()