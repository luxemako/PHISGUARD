import re


URGENT_WORDS = {
    "urgent",
    "immediately",
    "warning",
    "suspended",
    "limited",
    "expire",
    "action required"
}

CREDENTIAL_WORDS = {
    "password",
    "pin",
    "otp",
    "login",
    "sign in",
    "credentials"
}

REWARD_WORDS = {
    "winner",
    "prize",
    "reward",
    "free gift",
    "lottery",
    "claim now"
}

PAYMENT_WORDS = {
    "payment",
    "bank",
    "credit card",
    "refund",
    "invoice"
}


def find_matches(text, words):
    normalized = text.lower()

    return sorted(
        word
        for word in words
        if re.search(
            rf"\b{re.escape(word)}\b",
            normalized
        )
    )


def analyze_text_rules(text):
    warnings = []
    score = 0

    urgent = find_matches(text, URGENT_WORDS)
    credentials = find_matches(text, CREDENTIAL_WORDS)
    rewards = find_matches(text, REWARD_WORDS)
    payments = find_matches(text, PAYMENT_WORDS)

    if urgent:
        score += 20
        warnings.append("Urgent or threatening language was detected.")

    if credentials:
        score += 30
        warnings.append("The message requests sign-in information.")

    if rewards:
        score += 30
        warnings.append("The message contains a prize or reward claim.")

    if payments:
        score += 20
        warnings.append("The message discusses payment or banking information.")

    return {
        "score": min(score, 100),
        "warnings": warnings
    }


def combine_text_risk(model_score, rule_score):
    return round(
        model_score * 0.85
        + rule_score * 0.15,
        2
    )


def combine_email_risk(text_score, url_scores, rule_score):
    if url_scores:
        final_score = (
            text_score * 0.50
            + max(url_scores) * 0.40
            + rule_score * 0.10
        )
    else:
        final_score = (
            text_score * 0.85
            + rule_score * 0.15
        )

    return round(min(final_score, 100), 2)


def risk_level(score):
    if score >= 60:
        return "high"

    if score >= 30:
        return "medium"

    return "low"


def prediction_from_score(score):
    return "phishing" if score >= 60 else "legitimate"