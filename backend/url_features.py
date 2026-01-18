import re
from urllib.parse import urlparse

def extract_features(url):
    features = {}

    features["url_length"] = len(url)
    features["num_dots"] = url.count(".")
    features["num_hyphens"] = url.count("-")
    features["num_at"] = url.count("@")
    features["has_https"] = 1 if url.startswith("https") else 0
    features["has_ip"] = 1 if re.search(r"\d+\.\d+\.\d+\.\d+", url) else 0

    suspicious_words = ["login", "verify", "secure", "update", "bank", "upi", "paytm", "sbi", "account"]
    features["suspicious_word_count"] = sum(1 for w in suspicious_words if w in url.lower())

    return features
