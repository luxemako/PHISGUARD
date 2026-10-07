from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "datasets" / "raw"
PROCESSED_DIR = BASE_DIR / "datasets" / "processed"

DATASET_FILE = RAW_DIR / "450k URL.csv"
OUTPUT_FILE = PROCESSED_DIR / "phishing_urls.csv"


def load_dataset():
    data = pd.read_csv(DATASET_FILE)
    data["label"] = (data["type"] == "phishing").astype(int)
    return data[["url", "label"]]

def clean_dataset(data):
    data = data.dropna()
    data["url"] = data["url"].str.strip()
    data = data.drop_duplicates(subset="url")
    return data


def main():
    final_data = clean_dataset(load_dataset())
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    final_data.to_csv(OUTPUT_FILE, index=False)
    print("\nDataset prepared successfully")

if __name__ == "__main__":
    main()
