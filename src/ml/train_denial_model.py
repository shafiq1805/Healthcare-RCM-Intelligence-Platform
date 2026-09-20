import os
import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


DATA_PATH = os.path.join(
    "data",
    "gold",
    "denial_ml_dataset.csv",
)

MODEL_DIR = "models"

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "denial_logistic_regression.joblib",
)

os.makedirs(
    MODEL_DIR,
    exist_ok=True,
)


def load_dataset():
    df = pd.read_csv(DATA_PATH)

    return df


def prepare_features(df):
    feature_columns = [
        "claim_amount",
        "claim_line_count",
        "total_charge_amount",
        "total_allowed_amount",
        "payer",
        "provider_specialty",
        "encounter_type",
        "days_to_submit",
    ]

    target_column = "denied_flag"

    X = df[
        feature_columns
    ].copy()

    y = df[
        target_column
    ].copy()

    return X, y


def build_pipeline():
    numeric_features = [
        "claim_amount",
        "claim_line_count",
        "total_charge_amount",
        "total_allowed_amount",
        "days_to_submit",
    ]

    categorical_features = [
        "payer",
        "provider_specialty",
        "encounter_type",
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                StandardScaler(),
                numeric_features,
            ),
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                categorical_features,
            ),
        ]
    )

    model = LogisticRegression(
        max_iter=1000,
        random_state=42,
        class_weight="balanced",
    )

    pipeline = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor,
            ),
            (
                "model",
                model,
            ),
        ]
    )

    return pipeline


def evaluate_model(
    model,
    X_test,
    y_test,
):
    predictions = model.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0,
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0,
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0,
    )

    matrix = confusion_matrix(
        y_test,
        predictions,
    )

    print()
    print("Model Evaluation")
    print("================")

    print(
        f"Accuracy:  {accuracy:.4f}"
    )

    print(
        f"Precision: {precision:.4f}"
    )

    print(
        f"Recall:    {recall:.4f}"
    )

    print(
        f"F1 Score:  {f1:.4f}"
    )

    print()
    print(
        "Confusion Matrix:"
    )

    print(matrix)

    print()
    print(
        "Classification Report:"
    )

    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0,
        )
    )


def main():
    print(
        "Training denial prediction model..."
    )

    df = load_dataset()

    X, y = prepare_features(
        df
    )

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y,
        )
    )

    print(
        f"Training samples: "
        f"{len(X_train)}"
    )

    print(
        f"Testing samples: "
        f"{len(X_test)}"
    )

    print(
        f"Training denial rate: "
        f"{y_train.mean():.2%}"
    )

    print(
        f"Testing denial rate: "
        f"{y_test.mean():.2%}"
    )

    model = build_pipeline()

    model.fit(
        X_train,
        y_train,
    )

    evaluate_model(
        model,
        X_test,
        y_test,
    )

    joblib.dump(
        model,
        MODEL_PATH,
    )

    print()
    print(
        f"Model saved to: "
        f"{MODEL_PATH}"
    )


if __name__ == "__main__":
    main()