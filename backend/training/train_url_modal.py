from pathlib import Path
import sys

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BACKEND_DIR))

from app.services.url_features import extract_url_features


DATASET_PATH = BACKEND_DIR.parent / "datasets" / "processed" / "phishing_urls.csv"
MODEL_PATH = BACKEND_DIR / "app" / "ml_models" / "url_model.pkl"


def main():
    # Load dataset
    data = pd.read_csv(DATASET_PATH)

    # Extract URL features
    X = pd.DataFrame(
        data["url"].apply(extract_url_features).tolist()
    )
    y = data["label"]

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    # Train model
    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    # Test model
    predictions = model.predict(X_test)

    print("Accuracy:", accuracy_score(y_test, predictions))
    print(classification_report(y_test, predictions))

    # Save model
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump({
        "model": model,
        "feature_names": list(X.columns)
    }, MODEL_PATH)

    print("Model saved:", MODEL_PATH)


if __name__ == "__main__":
    main()