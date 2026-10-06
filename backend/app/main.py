from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.services.url_features import extract_url_features


# Load model
MODEL_PATH = Path(__file__).parent / "ml_models" / "url_model.pkl"
package = joblib.load(MODEL_PATH)

model = package["model"]
feature_names = package["feature_names"]


# FastAPI
app = FastAPI(title="PhishGuard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class URLRequest(BaseModel):
    url: str


@app.get("/api/health")
def health():
    return {"status": "online"}


@app.post("/api/analyze/url")
def analyze_url(request: URLRequest):

    # Extract URL features
    features = extract_url_features(request.url)

    # Convert features to model input
    input_data = pd.DataFrame([features])[feature_names]

    # Prediction
    prediction = int(model.predict(input_data)[0])
    probability = model.predict_proba(input_data)[0]

    risk_score = round(float(probability[1]) * 100, 2)

    return {
        "url": request.url,
        "prediction": "phishing" if prediction == 1 else "legitimate",
        "risk_score": risk_score,
    }