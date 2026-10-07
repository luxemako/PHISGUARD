from pathlib import Path
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent

DATASET_PATH = (
    PROJECT_DIR
    / "datasets"
    / "processed"
    / "text_messages.csv"
)

MODEL_PATH = (
    BACKEND_DIR
    / "app"
    / "ml_models"
    / "text_model.pkl"
)


def main():
    data = pd.read_csv(DATASET_PATH)

    required_columns = {"text", "label"}
    missing_columns = required_columns - set(data.columns)

    if missing_columns:
        raise ValueError(
            f"Missing dataset columns: {sorted(missing_columns)}"
        )

    data = data.dropna(subset=["text", "label"]).copy()
    data["text"] = data["text"].astype(str).str.strip()
    data = data[data["text"].str.len() > 2]
    data = data.drop_duplicates(subset=["text"])

    X_train, X_test, y_train, y_test = train_test_split(
        data["text"],
        data["label"].astype(int),
        test_size=0.2,
        random_state=42,
        stratify=data["label"]
    )

    pipeline = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                lowercase=True,
                stop_words="english",
                ngram_range=(1, 2),
                min_df=2,
                max_features=50000
            )
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                random_state=42
            )
        )
    ])

    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)

    print(classification_report(y_test, predictions, zero_division=0))
    print("Confusion matrix:")
    print(confusion_matrix(y_test, predictions))

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)

    print(f"Model saved at: {MODEL_PATH}")


if __name__ == "__main__":
    main()
