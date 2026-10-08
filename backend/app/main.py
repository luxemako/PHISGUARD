import ipaddress
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlparse

import joblib
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.database import engine, get_db
from app.models import Base
from app.repository import get_dashboard, save_scan
from app.services.analyzers import analyze_email, analyze_text, analyze_url

logger = logging.getLogger(__name__)
MODEL_DIR = Path(__file__).parent / "ml_models"

url_package = joblib.load(MODEL_DIR / "url_model.pkl")
url_model = url_package["model"]
url_feature_names = url_package["feature_names"]
text_model = joblib.load(MODEL_DIR / "text_model.pkl")


@asynccontextmanager
async def lifespan(application):
    if engine:
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="PhishGuard API",
    description="Message, email, and URL risk analysis",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        "database_configured": engine is not None,
    }


@app.get("/api/dashboard")
def dashboard(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return get_dashboard(db, limit)


@app.post("/api/analyze/url")
def analyze_url_endpoint(
    request: URLRequest,
    db: Session = Depends(get_db),
):
    try:
        result = analyze_url(
            request.url,
            url_model,
            url_feature_names,
        )
        save_scan(db, "url", request.url, result)
        return result
    except Exception as error:
        db.rollback()
        logger.exception("URL analysis failed")
        raise HTTPException(
            500,
            "Unable to analyze the URL.",
        ) from error

@app.post("/api/analyze/text")
def analyze_text_endpoint(
    request: TextRequest,
    db: Session = Depends(get_db),
):
    try:
        result = analyze_text(request.text, text_model)
        save_scan(db, "text", request.text, result)
        return result
    except Exception as error:
        db.rollback()
        logger.exception("Text analysis failed")
        raise HTTPException(
            500,
            "Unable to analyze the message.",
        ) from error

@app.post("/api/analyze/email")
def analyze_email_endpoint(
    request: EmailRequest,
    db: Session = Depends(get_db),
):
    try:
        result = analyze_email(
            request.subject,
            request.body,
            text_model,
            url_model,
            url_feature_names,
        )
        content = f"{request.subject}\n{request.body}"
        save_scan(db, "email", content, result)
        return result
    except Exception as error:
        db.rollback()
        logger.exception("Email analysis failed")
        raise HTTPException(
            500,
            "Unable to analyze the email.",
        ) from error
