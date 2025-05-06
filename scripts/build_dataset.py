# build_dataset.py

import os
import io
import zipfile
import requests
import sqlite3
import pandas as pd
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor

# 📥 Data sources
PHISHING_URL_SOURCE_1 = "https://phish.sinking.yachts/v2/all"
PHISHING_URL_SOURCE_2 = "https://openphish.com/feed.txt"
PHISHING_URL_SOURCE_3 = "https://urlhaus.abuse.ch/downloads/text/"

BENIGN_SOURCE = "https://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip"

# 📁 Paths
DB_PATH = "data/phishing_dataset.db"
TABLE_NAME = "phishing_dataset"

# 📏 How much we want
NUM_PHISHING = 200000
NUM_BENIGN = 200000

# === Fetch functions ===

def fetch_sinking_yachts(limit=NUM_PHISHING):
    try:
        resp = requests.get(PHISHING_URL_SOURCE_1, timeout=15)
        urls = resp.json()
        return urls[:limit] if isinstance(urls, list) else []
    except Exception as e:
        print(f"❌ Sinking Yachts fetch failed: {e}")
        return []

def fetch_openphish(limit=NUM_PHISHING):
    try:
        resp = requests.get(PHISHING_URL_SOURCE_2, timeout=15)
        urls = resp.text.strip().splitlines()
        return urls[:limit]
    except Exception as e:
        print(f"❌ OpenPhish fetch failed: {e}")
        return []

def fetch_urlhaus(limit=NUM_PHISHING):
    try:
        resp = requests.get(PHISHING_URL_SOURCE_3, timeout=15)
        lines = resp.text.strip().splitlines()
        urls = [line for line in lines if line.startswith("http")]
        return urls[:limit]
    except Exception as e:
        print(f"❌ URLHaus fetch failed: {e}")
        return []

def fetch_benign_urls(limit=NUM_BENIGN):
    try:
        r = requests.get(BENIGN_SOURCE, timeout=15)
        r.raise_for_status()
        z = zipfile.ZipFile(io.BytesIO(r.content))
        csv_data = z.read(z.namelist()[0]).decode("utf-8")
        df = pd.read_csv(io.StringIO(csv_data), header=None)
        return [f"http://{domain}" for domain in df[1].head(limit)]
    except Exception as e:
        print(f"⚠️ Benign fetch failed: {e}")
        return []

# === Feature Extraction (simple first step) ===
def extract_features(url):
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        tld = domain.split('.')[-1]
        return {
            "url": url,
            "domain": domain,
            "url_length": len(url),
            "num_dots": url.count("."),
            "has_https": int(url.startswith("https")),
            "path_length": len(parsed.path),
            "suspicious_keywords": sum(w in url.lower() for w in ["login", "secure", "verify", "update"]),
            "tld_len": len(tld)
        }
    except Exception as e:
        print(f"❌ Feature extraction failed for {url}: {e}")
        return {}

# === Build Dataset ===
def build_dataset():
    print("📥 Fetching phishing URLs from multiple sources...")
    phishing1 = fetch_sinking_yachts()
    phishing2 = fetch_openphish()
    phishing3 = fetch_urlhaus()

    all_phishing_urls = list(set(phishing1 + phishing2 + phishing3))
    print(f"✅ Total unique phishing URLs: {len(all_phishing_urls)}")

    print("📥 Fetching benign URLs...")
    benign_urls = fetch_benign_urls()

    # Label the URLs
    phishing = [{"url": u, "label": "phishing"} for u in all_phishing_urls]
    benign = [{"url": u, "label": "benign"} for u in benign_urls]

    # 🛡️ Balance the two classes
    min_count = min(len(phishing), len(benign))
    phishing = phishing[:min_count]
    benign = benign[:min_count]

    print(f"✅ Phishing: {len(phishing)} | Benign: {len(benign)}")

    all_urls = phishing + benign

    # ⚡ Enrich features in parallel
    print(f"⚡ Enriching features in parallel...")
    with ThreadPoolExecutor(max_workers=15) as executor:
        enriched = list(executor.map(lambda x: {**extract_features(x['url']), "label": x["label"]}, all_urls))

    df = pd.DataFrame([e for e in enriched if e and "url" in e])
    df.drop_duplicates(subset=["url"], inplace=True)

    print(f"🧹 Final dataset size: {len(df)} entries")

    # 🔍 Verify balance
    print("\n🧮 Label distribution:")
    print(df["label"].value_counts())
    print(df["label"].value_counts(normalize=True))

    # 💾 Save
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)

    print(f"✅ Saved to SQLite → {DB_PATH} (table: {TABLE_NAME})")

if __name__ == "__main__":
    build_dataset()

