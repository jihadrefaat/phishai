# utils/threat_intel.py

import base64
import requests
from urllib.parse import urlparse

# === VirusTotal Check (URL-based) ===
def check_virustotal(url: str, api_key: str) -> dict:
    try:
        if not api_key:
            return {"error": "API key missing"}

        # VT requires the URL to be base64-url encoded without padding
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        vt_url = f"https://www.virustotal.com/api/v3/urls/{url_id}"
        headers = {
            "x-apikey": api_key
        }

        response = requests.get(vt_url, headers=headers, timeout=15)

        if response.status_code == 200:
            data = response.json()
            stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            malicious = stats.get("malicious", 0) > 0
            return {
                "malicious": malicious,
                "stats": stats,
                "scan_date": data.get("data", {}).get("attributes", {}).get("last_analysis_date"),
                "url": url
            }
        else:
            return {"error": f"VT error {response.status_code}", "url": url}

    except Exception as e:
        return {"error": str(e), "url": url}


# === URLhaus Check ===
def check_urlhaus(url: str) -> dict:
    try:
        api = "https://urlhaus-api.abuse.ch/v1/url/"
        resp = requests.post(api, data={"url": url}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "listed": data.get("query_status") == "ok",
                "threat": data.get("threat")
            }
        else:
            return {"error": f"URLhaus error {resp.status_code}"}
    except Exception as e:
        return {"error": str(e)}

