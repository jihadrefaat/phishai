# alerting/alerts.py

import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# 🚀 Load environment variables
load_dotenv()

# 📬 Slack and Email settings
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

def send_slack_alert(url: str, verdict: str) -> bool:
    """Send alert to Slack with emojis + mention."""
    if not SLACK_WEBHOOK:
        print("[Slack Error] Slack webhook URL not configured.")
        return False

    emoji = "✅" if verdict == "clean" else "🚨"
    attention = "<!channel> " if verdict != "clean" else ""

    payload = {
        "text": f"{attention}{emoji} *PhishAI Sandbox Alert* — Verdict: *{verdict.upper()}*\n🔗 <{url}>"
    }

    try:
        response = requests.post(SLACK_WEBHOOK, json=payload, timeout=10)
        print("[Slack Debug] Payload sent:", payload)
        if response.status_code != 200:
            print(f"[Slack Error] Failed with status {response.status_code}: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print("[Slack Error]", str(e))
        return False


def send_email_alert(sender_email, password, to_email, subject, body) -> bool:
    """Send generic email alert with subject + body."""
    if not (sender_email and password and to_email):
        print("[Email Error] Email credentials or recipient not properly set.")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = to_email

        text = body
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
                <h2 style="color: #d9534f;">{'✅' if 'benign' in subject.lower() else '🚨'} {subject}</h2>
                <p style="font-size: 16px;">{body}</p>
                <hr>
                <p style="font-size:12px; color:gray;">Sent automatically by PhishAI Detection System</p>
            </body>
        </html>
        """

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        msg.attach(part1)
        msg.attach(part2)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, to_email, msg.as_string())

        print("📧 Email alert sent successfully.")
        return True
    except Exception as e:
        print("[Email Error]", str(e))
        return False

