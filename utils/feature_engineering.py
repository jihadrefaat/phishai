

# utils/feature_engineering.py

import os
import re
import math
import joblib
import pandas as pd
from urllib.parse import urlparse
from typing import List, Tuple

_sentence_model = None

BATCH_FOLDER = "ml_model/feature_batches"
os.makedirs(BATCH_FOLDER, exist_ok=True)

# === Model loader ===
def load_sentence_model():
    global _sentence_model
    if _sentence_model is None:
        from sentence_transformers import SentenceTransformer
        _sentence_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _sentence_model

# === Handcrafted features ===
def extract_handcrafted_features(url: str) -> List[float]:
    parsed = urlparse(url)
    domain = parsed.netloc
    try:
        tld = domain.split('.')[-1]
    except Exception:
        tld = ''
    return [
        len(url),
        1 if re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", parsed.hostname or "") else 0,
        url.count("."),
        len(re.findall(r"[^\w\s]", url)),
        sum(word in url.lower() for word in ["login", "secure", "update", "free", "verify"]),
        1 if parsed.scheme == "https" else 0,
        len(tld),
        len(parsed.path),
        calculate_entropy(domain),
        get_subdomain_depth(domain),
        is_suspicious_tld(tld)
    ]

# === NEW: Full single URL feature wrapper ===
def extract_features(url: str) -> List[float]:
    model = load_sentence_model()
    handcrafted = extract_handcrafted_features(url)
    embedding = model.encode([url])[0].tolist()
    return handcrafted + embedding

# === Extra feature helpers ===
def calculate_entropy(string: str) -> float:
    if not string:
        return 0.0
    prob = [float(string.count(c)) / len(string) for c in set(string)]
    return -sum(p * math.log(p, 2) for p in prob)

def get_subdomain_depth(domain: str) -> int:
    return domain.count('.') - 1

def is_suspicious_tld(tld: str) -> int:
    return int(tld.lower() in {'tk', 'gq', 'ml', 'cf', 'ga', 'cn', 'ru'})

# === Batch extractor (features/labels saved separately) ===
def extract_features_in_batches(df: pd.DataFrame, batch_size=2000):
    model = load_sentence_model()
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # Shuffle

    total = len(df)
    batches = math.ceil(total / batch_size)
    print(f"🔄 Total samples: {total} → {batches} batches")

    for batch_num in range(batches):
        start = batch_num * batch_size
        end = min(start + batch_size, total)
        batch_df = df.iloc[start:end]

        urls = batch_df["url"].tolist()
        labels = batch_df["label"].map({"benign": 0, "phishing": 1}).tolist()

        print(f"⚙️ Processing batch {batch_num + 1}/{batches} [{start}:{end}]...")

        handcrafted = [extract_handcrafted_features(url) for url in urls]
        try:
            embeddings = model.encode(urls, batch_size=16, show_progress_bar=False)
        except Exception as e:
            print(f"⚠️ Batch embedding failed: {e}")
            embeddings = [model.encode([url])[0] for url in urls]

        combined_features = [h + e.tolist() for h, e in zip(handcrafted, embeddings)]

        # 💾 Save separately as X and y
        joblib.dump(combined_features, os.path.join(BATCH_FOLDER, f"X_batch_{batch_num}.pkl"))
        joblib.dump(labels, os.path.join(BATCH_FOLDER, f"y_batch_{batch_num}.pkl"))
        print(f"✅ Saved batch {batch_num} → X_batch_{batch_num}.pkl / y_batch_{batch_num}.pkl")

# === Loader for all batches (optional fallback) ===
def load_all_batches() -> Tuple[List[List[float]], List[int]]:
    feature_vectors = []
    labels = []

    batch_files = sorted(os.listdir(BATCH_FOLDER))
    for f in batch_files:
        if f.startswith("X_batch_"):
            idx = f.split("_")[-1].split(".")[0]
            X = joblib.load(os.path.join(BATCH_FOLDER, f))
            y = joblib.load(os.path.join(BATCH_FOLDER, f.replace("X_", "y_")))
            feature_vectors.extend(X)
            labels.extend(y)

    return feature_vectors, labels

__all__ = [
    "extract_handcrafted_features",
    "extract_features",
    "extract_features_in_batches",
    "load_all_batches"
]

if __name__ == "__main__":
    test_url = "http://secure-login.example.tk/account/reset"

    handcrafted = extract_handcrafted_features(test_url)

    feature_names = [
        "url_length",
        "has_ip",
        "dot_count",
        "special_char_count",
        "phishing_keywords_count",
        "is_https",
        "tld_length",
        "path_length",
        "domain_entropy",
        "subdomain_depth",
        "is_suspicious_tld"
    ]

    print(f"🧪 Handcrafted feature count: {len(handcrafted)}")
    for name, value in zip(feature_names, handcrafted):
        print(f"{name:25}: {value}")
