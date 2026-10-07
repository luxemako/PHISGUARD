from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = ROOT / "datasets" / "raw" / "phishing_email.csv"

OUTPUT_FILE = (
    ROOT
    / "datasets"
    / "processed"
    / "text_messages.csv"
)


LABEL_MAPPING = {
    "safe email": 0,
    "phishing email": 1,
}


def load_dataset():
    data = pd.read_csv(INPUT_FILE)

    if {"text_combined", "label"}.issubset(data.columns):
        data = data[["text_combined", "label"]].rename(
            columns={"text_combined": "text"}
        )
    elif {"Email Text", "Email Type"}.issubset(data.columns):
        data = data[["Email Text", "Email Type"]].rename(
            columns={"Email Text": "text", "Email Type": "label"}
        )
    else:
        raise ValueError(
            "Expected text_combined/label or Email Text/Email Type columns."
        )

    if not pd.api.types.is_numeric_dtype(data["label"]):
        data["label"] = (
            data["label"]
            .astype(str)
            .str.strip()
            .str.lower()
            .map(LABEL_MAPPING)
        )

    data = data.dropna(subset=["text", "label"]).copy()
    data["text"] = data["text"].astype(str).str.strip()
    data = data[data["text"].str.len() > 5]
    data["label"] = data["label"].astype(int)
    data = data[data["label"].isin([0, 1])]
    return data.drop_duplicates(subset=["text"])


def main():
    data = load_dataset()
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(OUTPUT_FILE, index=False)

    print("Dataset prepared")
    print("Total rows:", len(data))
    print(data["label"].value_counts())
    print("Saved at:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
