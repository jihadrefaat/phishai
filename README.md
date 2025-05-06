
# 🎯 PhishAI - Advanced Phishing Detection Platform

PhishAI is an end-to-end phishing detection and analysis platform that combines AI-based link classification, dynamic sandbox behavior analysis, and real-time threat intelligence.

It’s built for SOC teams, threat researchers, and cybersecurity professionals to analyze suspicious URLs in a safe, automated, and insightful environment.

---

## 🚀 Features

* 🤖 **AI URL Classification** — ML model using handcrafted + BERT embeddings
* 🧪 **Headless Browser Sandbox** — Analyzes behavior in a stealth Playwright browser
* 🧠 **Heuristic Scoring** — Flags risky behavior with capped scoring system
* 📸 **Evidence Capture** — Screenshots, console logs, mouse + click detection
* 🔔 **Live Alerts** — Slack & Email notifications on suspicious activity
* ☁️ **Threat Intelligence** — Modular integration with VirusTotal, URLhaus
* 🛡️ **Customizable Whitelist** — Skip analysis for trusted domains
* 📊 **Streamlit UI** — Clean interface for investigation and reporting
* 🟣 **Dockerized Microservices** — Isolated containers for sandbox, API, and UI

---

## 📦 Architecture Overview

```
User Input (UI)
     ↓
FastAPI API ─────→ AI Scan (ML model)
     ↓                 ↓
  Sandbox Scan   Threat Intel Lookup
     ↓                 ↓
Heuristic Score + Alerts → Slack / Email
     ↓
 Streamlit Report (Logs + Screenshot)
```

---

## 🧪 Quickstart (Local Testing)

```bash
# Clone the repo
git clone https://github.com/your-username/phishai.git
cd phishai

# Copy environment variables
cp .env.example .env

# Build and run
docker-compose up --build
```

Then open [http://localhost:8501](http://localhost:8501) to access the dashboard.

---

## 📁 Project Structure

```
phishai/
├── api/               # FastAPI backend (AI + Threat Intel)
├── ui/                # Streamlit dashboard
├── sandbox/           # Headless behavior sandbox (Playwright)
├── ml_model/          # ML model and training scripts
├── utils/             # Feature engineering, alerts, helpers
├── .env.example       # Template environment variables
└── docker-compose.yml # Docker microservices orchestration
```

---

## 📧 Alerts (Slack & Email)

Alerts are sent when the system detects:

📥 Auto-download attempts (**default trigger**)  
🧬 Obfuscated JS or suspicious behavior (optional extension)  
⚠️ High heuristic score (optional extension)

---

## 🔐 Security & Isolation

* Sandbox runs in an isolated Docker container with Playwright stealth mode
* URLs are accessed **only for analysis**, with no persistent sessions
* All connections are ephemeral and scoped to one execution
* Your real IP is never exposed — traffic routes through container networking

---

## 🖼️ Screenshot Gallery

<details>
<summary>📸 Click to expand full gallery</summary>

| Screenshot | Description |
| ---------- | ----------- |
| ![](sandbox/screenshots/ui.png) | 🧠 Streamlit UI |
| ![](sandbox/screenshots/sandbox fake amazon.png) | 🧪 Fake Amazon in sandbox |
| ![](sandbox/screenshots/sandbox fake amazon 2.png) | 🧪 Fake Amazon - 2nd run |
| ![](sandbox/screenshots/ai+thread intel fake amazon2.png) | 🤖 AI + Threat Intel (Amazon) |
| ![](sandbox/screenshots/ai+thread intel fake amazon.jpeg) | 🧠 AI scan - Fake Amazon (JPEG) |
| ![](sandbox/screenshots/ai + thread intel metamask 2.png) | 🤖 Metamask analysis |
| ![](sandbox/screenshots/ai + thread intel metamask.jpeg) | 🧠 AI + TI - Metamask (JPEG) |
| ![](sandbox/screenshots/sandbox fake metamask login.png) | 🧪 Sandbox - Metamask |
| ![](sandbox/screenshots/sandbox fake metamask login 2.png) | 🔁 Sandbox - Metamask rerun |
| ![](sandbox/screenshots/sandbox fake metamask login 3.png) | 🔁 Sandbox - Metamask 3 |
| ![](sandbox/screenshots/sandbox simulated phishing page.png) | 🧪 Simulated phishing test |
| ![](sandbox/screenshots/sandbox simulated phishing page 2.png) | 🔁 Simulated phishing test 2 |
| ![](sandbox/screenshots/sandbox benign.png) | ✅ Sandbox - Benign case |
| ![](sandbox/screenshots/AI+thread intel benign.png) | ✅ AI Verdict - Benign |
| ![](sandbox/screenshots/AI+thread intel benign 2 .png) | ✅ AI Verdict - Benign (Alt) |
| ![](sandbox/screenshots/AI+thread intel phishing.jpeg) | 🚨 AI Verdict - Phishing (JPEG) |
| ![](sandbox/screenshots/AI+thread intel phishing  2.png) | 🚨 AI + TI - Phishing case |
| ![](sandbox/screenshots/sandbox logs.png) | 🗂️ JSON Log Directory Screenshot |

</details>

---

## 📈 Future Improvements

* URL clustering to detect campaign patterns
* IP/domain reputation enrichment
* SIEM integration (Splunk, Wazuh)
* AI model fine-tuning based on behavior logs
* ✅ **Structured JSON logs ready for dashboards, report generation, and long-term analysis**

---

## ⚙️ Environment Configuration (`.env`)

```env
EMAIL_USER=you@example.com
EMAIL_PASS=yourpassword
EMAIL_TO=alert@example.com
SLACK_WEBHOOK=https://hooks.slack.com/...
API_URL=http://localhost:8000
```

---

## 🙇‍♀️ Author

Built with 💙 by [**Gehad Refaat**] (https://github.com/jihadrefaat)
📬 License: MIT

> Please credit the author for any public or commercial use.
