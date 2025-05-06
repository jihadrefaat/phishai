# 🎯 PhishAI - Advanced Phishing Detection Platform

![GitHub stars](https://img.shields.io/github/stars/jihadrefaat/phishai?style=social)
![GitHub forks](https://img.shields.io/github/forks/jihadrefaat/phishai?style=social)
![GitHub license](https://img.shields.io/github/license/jihadrefaat/phishai)
![GitHub language](https://img.shields.io/github/languages/top/jihadrefaat/phishai)



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

* 📥 Auto-download attempts (**default trigger**)
* 🧬 Obfuscated JS or suspicious behavior (**optional**)
* ⚠️ High heuristic score (e.g. 8+/10, **optional**)

Want smarter alerts? You can extend alert logic inside the FastAPI or sandbox microservice.

---

## 🔐 Security & Isolation

* Sandbox runs in a fully isolated Docker container using Playwright in stealth mode
* URLs are accessed **only for analysis**, with no persistent sessions
* Connections are ephemeral and scoped to a single execution
* Your real IP address is never exposed — traffic is containerized and non-persistent

---

## ✅ Real Test Cases

### 🔬 High-Risk Phishing — Metamask Login

**URL**: `https://metamasklogin.wixsite.com/stepbystep`  
**Heuristic Score**: `9 / 10`

- ❌ Blocked network resources
- 🧬 JS fingerprinting + Sentry issues
- 👟 Mouse interaction simulated

---

### 🟡 Medium Risk — Amazon Clone

**URL**: `https://amazonkaclone.netlify.app/`  
**Heuristic Score**: `6 / 10`

- ❌ Multiple resource load failures
- 🧬 Firebase error stack trace
- 👟 Mouse movement simulated

---

### 🟢 Benign Case — Google Homepage

**URL**: `https://www.google.com/`  
**Heuristic Score**: `3 / 10`

- ✅ No threats detected
- ⚠️ Minor asset load failures (normal)

---

### 🧪 Simulated Phishing Payload Test

**URL**: `http://192.168.1.3:8888/`  
**Heuristic Score**: `6 / 10`

- 🧠 JS payload execution
- 📅 Auto-download attempt blocked
- 🧬 `eval()` & base64 code
- 👡 Mouse + click simulated

---

## 🖼️ Screenshot Gallery

<details>
<summary>📸 Click to expand full gallery</summary>

| Screenshot                                            | Description                             |
| ----------------------------------------------------- | --------------------------------------- |
| ![](screenshots/ui.png)                               | 🧠 Streamlit UI                         |
| ![](screenshots/sandbox_fake_amazon.png)              | 🧪 Fake Amazon (1st run)                |
| ![](screenshots/sandbox_fake_amazon2.png)             | 🧪 Fake Amazon (2nd run)                |
| ![](screenshots/ai+thread+intel_fake_amazon2.png)     | 🤖 AI + TI: Amazon clone (run 2)        |
| ![](screenshots/ai+thread_intel_fake_amazon.jpeg)     | 🤖 AI Verdict: Amazon phishing (JPEG)   |
| ![](screenshots/ai+thread_intel_metamask.jpeg)        | 🤖 AI Verdict: Metamask phishing (JPEG) |
| ![](screenshots/ai+thread_intel_metamask_2.png)       | 🤖 AI + TI: Metamask clone (run 2)      |
| ![](screenshots/sandbox_fake_metamask_login.png)      | 🧪 Sandbox: Metamask phishing (run 1)   |
| ![](screenshots/sandbox_fake_metamask_login2.png)     | 🔁 Sandbox: Metamask (run 2)            |
| ![](screenshots/sandbox_fake_metamask_login3.png)     | 🔁 Sandbox: Metamask (run 3)            |
| ![](screenshots/sandbox_simulated_phishing_page.png)  | 🧪 Simulated phishing test (run 1)      |
| ![](screenshots/sandbox_simulated_phishing_page2.png) | 🔁 Simulated phishing test (run 2)      |
| ![](screenshots/sandbox_benign.png)                   | ✅ Sandbox: Benign website               |
| ![](screenshots/AI+thread_intel_benign.png)           | ✅ AI Verdict: Benign case               |
| ![](screenshots/AI+thread_intel_benign2.png)          | ✅ AI Verdict: Benign (alt version)      |
| ![](screenshots/AI+thread_intel_phishing.jpeg)        | 🚨 AI Verdict: Phishing (JPEG)          |
| ![](screenshots/AI+thread_intel_phishing2.png)        | 🚨 AI + TI: Phishing (alt case)         |
| ![](screenshots/sandbox_logs.png)                     | 📂 Sandbox log directory view           |


</details>


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

Built with 💙 by [**Gehad Refaat**](https://github.com/jihadrefaat)  
📬 License: MIT

> Please credit the author for any public or commercial use.
