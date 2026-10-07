import ipaddress
import re
from urllib.parse import parse_qsl, unquote, urlparse


SUSPICIOUS_WORDS = {
    "account", "banking", "confirm", "login", "password", "payment",
    "secure", "signin", "update", "verification", "verify", "wallet",
}

SHORTENERS = {
    "bit.ly", "goo.gl", "is.gd", "ow.ly", "t.co", "tinyurl.com",
}

SECOND_LEVEL_SUFFIXES = {
    "ac.uk", "co.in", "co.jp", "co.uk", "com.au", "com.br", "com.cn",
    "com.mx", "com.sg", "com.tr", "net.au", "org.uk",
}

BRAND_DOMAINS = {
    "amazon": {"amazon.com", "amazon.in", "amazon.co.uk"},
    "apple": {"apple.com"},
    "facebook": {"facebook.com"},
    "github": {"github.com"},
    "google": {"google.com", "google.co.in", "google.co.uk"},
    "instagram": {"instagram.com"},
    "linkedin": {"linkedin.com"},
    "microsoft": {"microsoft.com"},
    "netflix": {"netflix.com"},
    "paypal": {"paypal.com"},
    "whatsapp": {"whatsapp.com"},
}

REDIRECT_PARAMETERS = {"continue", "dest", "destination", "next", "redirect", "return", "url"}
SUSPICIOUS_EXTENSIONS = {".apk", ".bat", ".cmd", ".exe", ".js", ".msi", ".rar", ".scr", ".zip"}


def contains_ip_address(hostname):
    try:
        ipaddress.ip_address(hostname)
        return 1
    except ValueError:
        return 0


def contains_suspicious_word(value):
    tokens = set(re.findall(r"[a-z0-9]+", unquote(value.lower())))
    return int(bool(tokens & SUSPICIOUS_WORDS))


def count_subdomains(hostname):
    if not hostname or contains_ip_address(hostname):
        return 0

    labels = [label for label in hostname.strip(".").split(".") if label]
    suffix = ".".join(labels[-2:])
    registrable_labels = 3 if suffix in SECOND_LEVEL_SUFFIXES else 2
    return max(len(labels) - registrable_labels, 0)


def get_domain_parts(hostname):
    if not hostname or contains_ip_address(hostname):
        return "", ""

    labels = [label for label in hostname.strip(".").split(".") if label]
    if len(labels) < 2:
        return labels[0] if labels else "", ""

    suffix = ".".join(labels[-2:])
    suffix_labels = 2 if suffix in SECOND_LEVEL_SUFFIXES else 1
    if len(labels) <= suffix_labels:
        return labels[0], ".".join(labels)

    domain_index = -(suffix_labels + 1)
    domain_label = labels[domain_index]
    registrable_domain = ".".join(labels[domain_index:])
    return domain_label, registrable_domain


def is_one_edit_from(left, right):
    length_difference = len(left) - len(right)
    if abs(length_difference) > 1 or left == right:
        return False

    if length_difference == 0:
        differences = [
            index
            for index, (left_char, right_char) in enumerate(zip(left, right))
            if left_char != right_char
        ]
        if len(differences) == 1:
            return True
        return (
            len(differences) == 2
            and differences[1] == differences[0] + 1
            and left[differences[0]] == right[differences[1]]
            and left[differences[1]] == right[differences[0]]
        )

    shorter, longer = (left, right) if len(left) < len(right) else (right, left)
    short_index = 0
    long_index = 0
    edits = 0

    while short_index < len(shorter) and long_index < len(longer):
        if shorter[short_index] == longer[long_index]:
            short_index += 1
        else:
            edits += 1
            if edits > 1:
                return False
        long_index += 1

    return True


def brand_risk_features(hostname):
    domain_label, registrable_domain = get_domain_parts(hostname)
    hostname_tokens = set(re.findall(r"[a-z0-9]+", hostname))
    typosquatting = 0
    impersonation = 0

    for brand, official_domains in BRAND_DOMAINS.items():
        if registrable_domain in official_domains:
            continue

        if brand in hostname_tokens:
            impersonation = 1
        elif domain_label and is_one_edit_from(domain_label, brand):
            typosquatting = 1

    return typosquatting, impersonation


def normalize_url(url):
    url = str(url).strip().lower()

    if url.startswith("https://www."):
        return "https://" + url[len("https://www."):]
    if url.startswith("http://www."):
        return "http://" + url[len("http://www."):]
    if url.startswith("www."):
        return url[len("www."):]

    return url


def extract_url_features(url):
    url = normalize_url(url)
    parsing_url = url

    if not parsing_url.startswith(("http://", "https://")):
        parsing_url = "http://" + parsing_url

    parsed = urlparse(parsing_url)
    hostname = (parsed.hostname or "").rstrip(".")
    path = parsed.path
    query = parsed.query
    fragment = parsed.fragment
    path_content = " ".join((path, query, fragment))

    domain_label, registrable_domain = get_domain_parts(hostname)
    labels = [label for label in hostname.split(".") if label]
    typosquatting, brand_impersonation = brand_risk_features(hostname)
    query_parameters = parse_qsl(query, keep_blank_values=True)
    query_names = {name.lower() for name, _ in query_parameters}

    try:
        port = parsed.port
        invalid_port = 0
    except ValueError:
        port = None
        invalid_port = 1

    return {
        # URL structure
        "url_length": len(url),
        "domain_length": len(hostname),
        "path_length": len(path),
        "query_length": len(query),
        "fragment_length": len(fragment),
        "path_depth": len([part for part in path.split("/") if part]),
        "query_parameter_count": len(query_parameters),
        "subdomain_count": count_subdomains(hostname),
        "hostname_label_count": len(labels),
        "longest_hostname_label_length": max(map(len, labels), default=0),
        "tld_length": len(registrable_domain.rsplit(".", 1)[-1]) if registrable_domain else 0,

        # Character patterns
        "dot_count": url.count("."),
        "hyphen_count": url.count("-"),
        "at_count": url.count("@"),
        "question_count": url.count("?"),
        "equal_count": url.count("="),
        "slash_count": url.count("/"),
        "digit_count": sum(char.isdigit() for char in url),
        "special_character_count": sum(not char.isalnum() for char in url),
        "domain_digit_count": sum(char.isdigit() for char in hostname),
        "domain_hyphen_count": hostname.count("-"),
        "encoded_character_count": url.count("%"),

        # Protocol and hostname security
        "has_https": int(url.startswith("https://")),
        "has_ip_address": contains_ip_address(hostname),
        "has_nonstandard_port": int(port is not None and port not in {80, 443}),
        "has_invalid_port": invalid_port,
        "has_punycode": int(any(
            label.startswith("xn--") for label in labels
        )),
        "has_credentials": int(parsed.username is not None),
        "uses_shortener": int(any(
            hostname == shortener or hostname.endswith("." + shortener)
            for shortener in SHORTENERS
        )),

        # Domain identity
        "has_suspicious_word_in_domain": contains_suspicious_word(hostname),
        "has_typosquatting": typosquatting,
        "has_brand_impersonation": brand_impersonation,

        # Path and query behavior
        "has_suspicious_word_in_path": contains_suspicious_word(path_content),
        "has_encoded_characters": int("%" in url),
        "has_redirect_parameter": int(bool(query_names & REDIRECT_PARAMETERS)),
        "has_suspicious_file_extension": int(any(
            path.lower().endswith(extension)
            for extension in SUSPICIOUS_EXTENSIONS
        )),
        "has_double_slash_in_path": int("//" in path),
    }
