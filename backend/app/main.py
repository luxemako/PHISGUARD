<<<<<<< HEAD
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
=======
import ipaddress
import logging
from pathlib import Path
from urllib.parse import urlparse

import joblib
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

from app.services.analyzers import analyze_email, analyze_text, analyze_url

logger = logging.getLogger(__name__)
MODEL_DIR = Path(__file__).parent / "ml_models"

url_package = joblib.load(MODEL_DIR / "url_model.pkl")
url_model = url_package["model"]
url_feature_names = url_package["feature_names"]
text_model = joblib.load(MODEL_DIR / "text_model.pkl")

app = FastAPI(
    title="PhishGuard API",
    description="Message, email, and URL risk analysis",
    version="2.0.0",
)
>>>>>>> 5a9a7e0f789cfc6e27ef0129d373bedccb4039fa

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


<<<<<<< HEAD
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
=======
def require_text(value, field_name):
    value = value.strip()
    if len(value) < 3:
        raise ValueError(f"Please enter a valid {field_name}.")
    return value


class URLRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def validate_url(cls, value):
        value = require_text(value, "URL")
        lowered = value.lower()

        if "://" in lowered and not lowered.startswith(("http://", "https://")):
            raise ValueError("Only HTTP and HTTPS URLs are supported.")

        parsed = urlparse(value if "://" in value else f"http://{value}")
        hostname = parsed.hostname or ""

        try:
            is_ip = bool(ipaddress.ip_address(hostname))
        except ValueError:
            is_ip = False

        if not hostname or ("." not in hostname and not is_ip):
            raise ValueError("Please enter a URL with a valid hostname.")

        return value


class TextRequest(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def validate_text(cls, value):
        return require_text(value, "message")


class EmailRequest(BaseModel):
    subject: str = ""
    body: str

    @field_validator("subject")
    @classmethod
    def clean_subject(cls, value):
        return value.strip()

    @field_validator("body")
    @classmethod
    def validate_body(cls, value):
        return require_text(value, "email body")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    error: RequestValidationError,
):
    messages = [
        item["msg"].replace("Value error, ", "")
        for item in error.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "detail": " ".join(messages),
        },
    )


@app.get("/api/health")
def health():
    return {
        "status": "online",
        "url_model_loaded": True,
        "text_model_loaded": True,
    }


@app.post("/api/analyze/url")
def analyze_url_endpoint(request: URLRequest):
    try:
        result = analyze_url(
            request.url,
            url_model,
            url_feature_names,
        )

        return result
    except Exception as error:
        logger.exception("URL analysis failed")
        raise HTTPException(
            500,
            "Unable to analyze the URL.",
        ) from error

@app.post("/api/analyze/text")
def analyze_text_endpoint(request: TextRequest):
    try:
        result = analyze_text(request.text, text_model)

        return result
    except Exception as error:
        logger.exception("Text analysis failed")
        raise HTTPException(
            500,
            "Unable to analyze the message.",
        ) from error

@app.post("/api/analyze/email")
def analyze_email_endpoint(request: EmailRequest):
    try:
        result = analyze_email(
            request.subject,
            request.body,
            text_model,
            url_model,
            url_feature_names,
        )

        return result
    except Exception as error:
        logger.exception("Email analysis failed")
        raise HTTPException(
            500,
            "Unable to analyze the email.",
        ) from error
>>>>>>> 5a9a7e0f789cfc6e27ef0129d373bedccb4039fa
