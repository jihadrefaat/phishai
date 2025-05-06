from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import os
import requests
from dotenv import load_dotenv
from urllib.parse import urlparse

# 🔐 Load environment
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(dotenv_path=env_path)

# 🧠 Local imports
from utils.feature_engineering import extract_features
from alerting.alerts import send_slack_alert, send_email_alert
from utils.threat_intel import check_virustotal, check_urlhaus

# 🔧 Config
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")
VT_API_KEY = os.getenv("VT_API_KEY")

# 🚀 Init FastAPI app
app = FastAPI(title="PhishAI API")

# 📦 Load model
model = joblib.load("ml_model/phish_model.pkl")

# ✅ Whitelist for trusted domains
TRUSTED_DOMAINS = {"google.com", "github.com", "wikipedia.org"}

# 📥 Input schema
class ScanInput(BaseModel):
    text: str
    message: str = ""

# 🔍 ML + Threat Intel Analyze endpoint
@app.post("/scan")
async def full_scan(input: ScanInput):
    try:
        # 🔍 Run AI Prediction
        features = extract_features(input.text)
        ai_prediction = model.predict([features])[0]
        ai_confidence = float(model.predict_proba([features])[0][int(ai_prediction)])

        # 🌐 Extract domain
        parsed_domain = urlparse(input.text).netloc.replace("www.", "")

        # ✅ Whitelist override
        if parsed_domain in TRUSTED_DOMAINS:
            return {
                "label": "benign",
                "override": "whitelist",
                "confidence": 1.0,
                "ai_label": "phishing" if ai_prediction == 1 else "benign",
                "ai_confidence": round(ai_confidence, 3),
                "threat_intel": {}
            }

        # 🔎 Run Threat Intel
        vt_result = check_virustotal(input.text, VT_API_KEY)
        uh_result = check_urlhaus(input.text)
        vt_malicious = vt_result.get("malicious", False)
        uh_listed = uh_result.get("listed", False)

        # 🧠 Final Verdict
        if not vt_malicious and not uh_listed:
            label = "benign"
            override = "intel"
            confidence = 1.0
        elif vt_malicious or uh_listed:
            label = "phishing"
            override = "intel"
            confidence = 0.99
        else:
            label = "phishing" if ai_prediction == 1 else "benign"
            override = None
            confidence = round(ai_confidence, 3)

        result = {
            "label": label,
            "override": override,
            "confidence": confidence,
            "ai_label": "phishing" if ai_prediction == 1 else "benign",
            "ai_confidence": round(ai_confidence, 3),
            "threat_intel": {
                "VirusTotal": vt_result,
                "URLhaus": uh_result
            }
        }

        # 🔔 Alerting for real phishing
        if result["label"] == "phishing" and result["confidence"] > 0.8:
            alert_msg = (
                f"⚠️ PHISHING DETECTED\nURL: {input.text}\nConfidence: {result['confidence']*100:.2f}%"
            )
            send_slack_alert(SLACK_WEBHOOK, alert_msg)
            send_email_alert(EMAIL_USER, EMAIL_PASS, EMAIL_TO, "⚠️ Phishing Alert", alert_msg)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan error: {str(e)}")

# 🌐 Root
@app.get("/")
def root():
    return {"message": "PhishAI API is running 🚀"}

# ✅ Late import to avoid circular dependency
from api.routes import sandbox_check
app.include_router(sandbox_check.router)

