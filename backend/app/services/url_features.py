import ipaddress
from urllib.parse import urlparse


SUSPICIOUS_WORDS = [
    "login",
    "verify",
    "account",
    "secure",
    "bank",
    "update",
    "password",
    "signin",
]


def has_ip(hostname):
    try:
        ipaddress.ip_address(hostname)
        return 1
    except ValueError:
        return 0


def extract_url_features(url):
    url = str(url).strip().lower()

    # Add protocol only for parsing
    parse_url = url if "://" in url else "http://" + url
    parsed = urlparse(parse_url)

    domain = parsed.hostname or ""
    path = parsed.path

    return {
        "url_length": len(url),
        "domain_length": len(domain),
        "path_length": len(path),

        "dot_count": url.count("."),
        "hyphen_count": url.count("-"),
        "slash_count": url.count("/"),
        "digit_count": sum(c.isdigit() for c in url),

        "has_https": int(url.startswith("https://")),
        "has_ip_address": has_ip(domain),

        "has_at_symbol": int("@" in url),

        "has_suspicious_word": int(
            any(word in url for word in SUSPICIOUS_WORDS)
        ),

        "subdomain_count": max(domain.count(".") - 1, 0),
    }