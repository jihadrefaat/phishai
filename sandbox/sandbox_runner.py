# 🔄 Async support and system utilities
import asyncio
import os
import json
from datetime import datetime
import sys
import re
from urllib.parse import urlparse

# 📦 Configure Playwright browser path inside Docker
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/ms-playwright"

# ➕ Add app directory to the system path
sys.path.append("/app")

# 🧭 Import Playwright async API and stealth plugin to avoid bot detection
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

# 🔐 Load environment variables (e.g., email credentials, API keys)
from dotenv import load_dotenv

# 📢 Alerting system for Slack and Email notifications
from alerting.alerts import (
    send_slack_alert,
    send_email_alert,
    EMAIL_USER,
    EMAIL_PASS,
    EMAIL_TO
)

# 🖼️ Folder to save screenshots and logs
SCREENSHOT_FOLDER = "sandbox/screenshots"
LOG_FOLDER = "sandbox/logs"
os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)

# 🔄 Load .env file
load_dotenv()

# 🚀 Core sandbox runner that visits and analyzes a URL
async def run_url_sandbox(url: str) -> dict:
    results = {
        "url": url,
        "console_logs": [],
        "categorized_logs": {
            "errors": [],
            "warnings": [],
            "info": [],
            "other": []
        },
        "error": None,
        "screenshot_path": None,
        "debug": [],
        "auto_download_detected": False,
        "heuristic_score": 0,
        "title": ""
    }

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
                    "--disable-background-networking", "--disable-extensions",
                    "--disable-webgl", "--mute-audio", "--hide-scrollbars"
                ]
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                accept_downloads=False
            )
            page = await context.new_page()
            await stealth_async(page)

            async def block_resources(route, request):
                if request.resource_type in ["image", "font", "media"]:
                    await route.abort()
                else:
                    await route.continue_()
            await page.route("**/*", block_resources)

            def handle_console(msg):
                text = f"[{msg.type}] {msg.text}"
                results["console_logs"].append(text)
                lower = msg.text.lower()
                if "error" in lower:
                    results["categorized_logs"]["errors"].append(msg.text)
                elif "warning" in lower:
                    results["categorized_logs"]["warnings"].append(msg.text)
                elif "info" in lower or "log" in msg.type:
                    results["categorized_logs"]["info"].append(msg.text)
                else:
                    results["categorized_logs"]["other"].append(msg.text)

            page.on("console", handle_console)

            async def on_download(download):
                results["console_logs"].append("[ALERT] Auto-download attempt blocked")
                results["auto_download_detected"] = True
                await download.cancel()
                send_slack_alert(url, "download-attempt-blocked")
                send_email_alert(EMAIL_USER, EMAIL_PASS, EMAIL_TO,
                                 "🚨 Auto-Download Blocked",
                                 f"A download was blocked during sandbox visit to: {url}")
                results["debug"].append("Auto-download alert triggered.")

            page.on("download", lambda d: asyncio.create_task(on_download(d)))

            try:
                await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            except Exception as e:
                results["error"] = (
                    "⚠️ Page load failed. This page may be inactive, unreachable, or the URL is invalid.\n"
                    f"Details: {str(e)}"
                )
                results["console_logs"].append(results["error"])
                results["debug"].append(f"Page.goto error: {str(e)}")
                await browser.close()
                return results

            try:
                await page.mouse.move(100, 100)
                await page.mouse.move(300, 300)
                await page.mouse.wheel(0, 400)
                await asyncio.sleep(1)
                await page.mouse.click(300, 250)
                results["debug"].append("Mouse movement & scroll simulation performed.")
            except Exception as e:
                results["debug"].append(f"Mouse simulation failed: {str(e)}")

            await asyncio.sleep(3)

            try:
                results["title"] = await page.title()
            except:
                results["title"] = "Unknown"

            # 🧠 Heuristic scoring
            html = await page.content()
            script_count = html.count("<script")
            keywords = ["login", "verify", "password", "bank", "update", "reset", "signin", "checkout", "get cash", "win", "limited offer", "invoice"]
            dom_score = sum(k in html.lower() for k in keywords)
            console_error_score = len(results["categorized_logs"]["errors"])
            download_score = 2 if results["auto_download_detected"] else 0
            title_score = int(any(word in results["title"].lower() for word in keywords))

            # 🌐 Structural phishing signals
            parsed = urlparse(url)
            netloc = parsed.netloc.lower()
            path = parsed.path.lower()
            tld = netloc.split('.')[-1]

            suspect_brands = ["facebook", "paypal", "amazon", "netflix", "apple", "google", "microsoft", "instagram", "linkedin", "bank", "visa", "mastercard"]
            suspicious_tlds = ["xyz", "tk", "ml", "ga", "cf", "click", "shop"]
            suspicious_hosts = ["vercel.app", "netlify.app", "github.io", "glitch.me"]

            tld_score = 1 if tld in suspicious_tlds else 0
            host_score = 1 if any(h in netloc for h in suspicious_hosts) else 0
            brand_in_path = any(b in path for b in suspect_brands) and not any(b in netloc for b in suspect_brands)
            brand_score = 1 if brand_in_path else 0
            ip_like = 1 if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", netloc.split(':')[0]) else 0

            url_score = tld_score + host_score + brand_score + ip_like

            score = int(script_count > 10) + dom_score + console_error_score + download_score + title_score + url_score
            results["heuristic_score"] = min(score, 10)
            results["debug"].append(f"Heuristic score: {results['heuristic_score']}")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_url = url.replace("http://", "").replace("https://", "").replace("/", "_").replace("?", "_").replace(":", "_")
            screenshot_path = os.path.join(SCREENSHOT_FOLDER, f"{safe_url}_{timestamp}.png")
            await page.screenshot(path=screenshot_path, full_page=True)
            results["screenshot_path"] = screenshot_path

            await browser.close()

    except Exception as e:
        results["error"] = f"Sandbox Error: {str(e)}"
        results["debug"].append(results["error"])

    return results

# 📁 Save the results and return them
async def sandbox_analyze(url: str):
    result = await run_url_sandbox(url)
    log_path = os.path.join(LOG_FOLDER, f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(log_path, "w") as f:
        json.dump(result, f, indent=2)
    return result

