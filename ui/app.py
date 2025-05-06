import streamlit as st
import joblib
import requests
import sys
import os
from dotenv import load_dotenv
from PIL import Image

# 🛠 Path setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(dotenv_path=env_path)

API_URL = os.getenv("API_URL", "http://localhost:8000")

from utils.feature_engineering import extract_features

# 🌐 Streamlit Config
st.set_page_config(page_title="PhishAI - Advanced Phishing Detection", layout="centered")
st.title("🎯 PhishAI - Advanced Phishing Detection Platform")

st.markdown("""
Welcome to **PhishAI** 🛡  
A next-generation platform for analyzing suspicious links using:
- 🔍 Final Verdict Powered by Whitelist + Threat Intelligence  
- 🤖 AI Model Learns Silently Behind-the-Scenes  
- 🧪 Secure Sandbox Execution & Behavior Capture  
""")

# 🔗 User Input
url = st.text_input("🔗 Enter URL to Analyze")
message = st.text_area("💬 Optional Message or Email Body (text content)")

# ℹ️ Tip
st.info("💡 **Tip**: Start with '🚦 Full AI + Intel Scan'. Use '🧬 Deep Scan (Sandbox)' for suspicious links.")

col1, col2 = st.columns(2)

# 🚦 AI + Intel Scan
with col1:
    if st.button("🚦 Full AI + Intel Scan"):
        if not url:
            st.warning("Please enter a URL to analyze.")
        else:
            with st.spinner("Running full analysis pipeline..."):
                try:
                    response = requests.post(f"{API_URL}/scan", json={"text": url, "message": message})
                    if response.status_code == 200:
                        result = response.json()
                        label = result.get("label", "unknown")
                        confidence = result.get("confidence", 0)
                        override = result.get("override")
                        vt = result.get("threat_intel", {}).get("VirusTotal", {})
                        haus = result.get("threat_intel", {}).get("URLhaus", {})

                        vt_safe = vt.get("malicious") is False
                        haus_safe = haus.get("listed") is False

                        st.subheader("🔎 Final Verdict")
                        if override == "whitelist":
                            st.success("✅ BENIGN — Whitelist override applied (trusted domain).")
                        elif vt_safe and haus_safe:
                            st.success("✅ BENIGN — Confirmed safe by Threat Intelligence.")
                        elif label == "phishing":
                            st.error("🚨 PHISHING DETECTED — AI flagged this as suspicious.")
                        else:
                            st.success("✅ BENIGN — No threats or AI triggers found.")

                        with st.expander("🛡️ Threat Intelligence Layer"):
                            st.json({"VirusTotal": vt, "URLhaus": haus})

                        with st.expander("📄 Raw API Response (Debug Panel)"):
                            st.json(result)
                    else:
                        st.error(f"API error {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"🚫 Scan Error: {str(e)}")

# 🧬 Deep Sandbox Scan
with col2:
    if st.button("🧬 Deep Scan (Sandbox)", help="Simulates behavior and captures JS/auto-downloads"):
        if not url:
            st.warning("Please enter a URL to sandbox.")
        else:
            with st.spinner("Running inside secure sandbox..."):
                try:
                    response = requests.post(f"{API_URL}/sandbox-check", json={"url": url})
                    if response.status_code == 200:
                        raw = response.json()

                        # Handle nested report
                        report = raw.get("sandbox_report", {})
                        if isinstance(report.get("sandbox_report"), dict):
                            report = report["sandbox_report"]

                        st.subheader("🔬 Deep Scan Results — Behavioral Sandbox")

                        # 🧠 Heuristic Score
                        score = report.get("heuristic_score", 0)
                        st.info(f"🧠 Heuristic Risk Score: **{score} / 10**", icon="📊")
                        with st.expander("ℹ️ What is this?"):
                            st.markdown("""
**Heuristic Score** estimates phishing risk using:

- Suspicious JS behavior
- Phishing keywords
- Console errors
- Auto-download attempts
""")

                        # 🖱️ Mouse Interaction
                        if "Mouse movement & scroll simulation performed." in report.get("debug", []):
                            st.success("🖱️ Simulated user interaction successful.")

                        # 📸 Screenshot
                        screenshot_path = report.get("screenshot_path")
                        local_screenshot_path = os.path.join("sandbox/screenshots", os.path.basename(screenshot_path)) if screenshot_path else None

                        if local_screenshot_path and os.path.exists(local_screenshot_path):
                            st.image(Image.open(local_screenshot_path), caption="📸 Captured Screenshot", use_container_width=True)
                        elif local_screenshot_path:
                            st.image(local_screenshot_path, caption="📸 Captured Screenshot", use_container_width=True)
                        else:
                            st.info("No screenshot was captured.")

                        # 🧾 Categorized Console Logs
                        categorized = report.get("categorized_logs", {})
                        if categorized:
                            with st.expander("🖥️ Console Logs — Categorized"):
                                if categorized.get("errors"):
                                    st.error("🚫 **Errors**")
                                    for log in categorized["errors"]:
                                        st.code(log)
                                if categorized.get("warnings"):
                                    st.warning("⚠️ **Warnings**")
                                    for log in categorized["warnings"]:
                                        st.code(log)
                                if categorized.get("info"):
                                    st.info("ℹ️ **Info Logs**")
                                    for log in categorized["info"]:
                                        st.code(log)
                                if categorized.get("other"):
                                    st.markdown("🔍 **Other Logs**")
                                    for log in categorized["other"]:
                                        st.code(log)
                        else:
                            st.info("No console logs captured.")

                        # 🚨 Auto-download
                        if report.get("auto_download_detected"):
                            st.error("🚨 Auto-download attempt detected!")

                        # ⚠️ Errors
                        if report.get("error"):
                            st.warning(f"⚠️ Sandbox Error: {report['error']}")

                        # 🛠 Raw
                        with st.expander("📄 Raw Sandbox Response (Debug Panel)"):
                            st.json(report)
                    else:
                        st.error(f"🚫 Sandbox API Error {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"🚫 Sandbox Connection Error: {str(e)}")

# Footer
st.markdown("""<hr style="height:1px;border:none;color:#ccc;background-color:#ccc;" /> """, unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; padding: 10px; font-size: 13px; color: gray;">
    PhishAI © 2025 | Developed by <strong>Gehad</strong> — Advanced Phishing Detection and Sandbox Analysis.
</div>
""", unsafe_allow_html=True)

