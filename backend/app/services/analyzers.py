import re

import pandas as pd

from app.services.risk_engine import (
    analyze_text_rules,
    combine_email_risk,
    combine_text_risk,
    prediction_from_score,
    risk_level
)
from app.services.url_features import extract_url_features


URL_PATTERN = re.compile(
    r"https?://[^\s<>\"']+",
    re.IGNORECASE
)


def model_probability(model, input_data, phishing_class=1):
    probabilities = model.predict_proba(input_data)[0]
    classes = list(model.classes_)
    class_index = classes.index(phishing_class)

    return round(float(probabilities[class_index]) * 100, 2)


def analyze_url(url, model, feature_names):
    features = extract_url_features(url)
    input_data = pd.DataFrame([features])[feature_names]

    score = model_probability(model, input_data)
    warnings = []

    if features["has_ip_address"]:
        warnings.append("The URL uses an IP address.")

    if features["has_suspicious_word_in_domain"]:
        warnings.append("The domain contains a suspicious keyword.")

    if features["uses_shortener"]:
        warnings.append("A URL-shortening service was detected.")

    if features["has_punycode"]:
        warnings.append("The domain uses an encoded name.")

    if features["has_credentials"]:
        warnings.append("The URL contains embedded credentials.")

    if features["has_typosquatting"]:
        score = max(score, 90)
        warnings.append(
            "The domain closely resembles a known brand."
        )

    if features["has_brand_impersonation"]:
        score = max(score, 90)
        warnings.append(
            "A brand name appears outside its official domain."
        )

    return {
        "url": url,
        "prediction": prediction_from_score(score),
        "risk_score": score,
        "risk_level": risk_level(score),
        "warning_signs": warnings
    }


def analyze_text(text, model):
    model_score = model_probability(
        model,
        [text]
    )

    rules = analyze_text_rules(text)
    final_score = combine_text_risk(
        model_score,
        rules["score"]
    )

    return {
        "prediction": prediction_from_score(final_score),
        "risk_score": final_score,
        "risk_level": risk_level(final_score),
        "model_score": model_score,
        "rule_score": rules["score"],
        "warning_signs": rules["warnings"]
    }


def extract_urls(text):
    urls = URL_PATTERN.findall(text)

    return list(dict.fromkeys(
        url.rstrip(".,);]")
        for url in urls
    ))


def analyze_email(
    subject,
    body,
    text_model,
    url_model,
    url_feature_names
):
    combined_text = f"{subject}\n{body}".strip()

    text_result = analyze_text(
        combined_text,
        text_model
    )

    urls = extract_urls(combined_text)

    url_results = [
        analyze_url(
            url,
            url_model,
            url_feature_names
        )
        for url in urls
    ]

    url_scores = [
        result["risk_score"]
        for result in url_results
    ]

    final_score = combine_email_risk(
        text_result["model_score"],
        url_scores,
        text_result["rule_score"]
    )

    warnings = list(text_result["warning_signs"])

    for result in url_results:
        warnings.extend(result["warning_signs"])

    warnings = list(dict.fromkeys(warnings))

    return {
        "prediction": prediction_from_score(final_score),
        "risk_score": final_score,
        "risk_level": risk_level(final_score),
        "text_analysis": text_result,
        "url_analysis": url_results,
        "detected_urls": urls,
        "warning_signs": warnings
    }