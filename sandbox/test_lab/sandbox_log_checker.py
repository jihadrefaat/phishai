# 📦 Import required libraries
import json  # for loading the sandbox result JSON
import sys   # for reading command-line arguments

# 🎯 Define specific log triggers we want to detect
TRIGGERS = {
    "🪤 Auto-download": "🪤 Auto-download triggered",
    "👀 Mouse movement": "👀 Mouse moved",
    "💥 Click event": "💥 Click event triggered",
    "🧬 Eval": "🧬 base64 payload decoded",
    "📤 C2 Beacon Sent": "📤 C2 beacon sent",
    "❌ C2 Beacon Failed": "❌ C2 beacon failed",
    "🔁 Redirect Log": "🔁 Redirecting to",
    "🚪 Unload Detected": "🚪 Page is unloading for redirect"
}

# 🧪 Function to analyze a sandbox log file
def check_log(file_path):
    # 📖 Load the sandbox JSON file
    with open(file_path, "r") as f:
        data = json.load(f)

    print(f"\n📄 Checking Sandbox Log: {file_path}\n")

    found = []

    # 🔍 Check for the presence of each trigger in the console logs
    for name, marker in TRIGGERS.items():
        match = any(marker in log for log in data.get("console_logs", []))
        status = "✅" if match else "❌"
        found.append((status, name))

    # 📊 Print results in a friendly format
    for status, name in found:
        print(f"{status} {name}")

    # 🧠 Print additional results from the sandbox
    print(f"\n🎯 Heuristic Score: {data.get('heuristic_score', 0)}")
    print(f"🛡️  Auto-Download Detected: {data.get('auto_download_detected', False)}")
    print(f"📸 Screenshot saved at: {data.get('screenshot_path')}\n")

# 🚀 Entry point: accept log file path as command-line argument
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sandbox_log_checker.py path/to/sandbox_log.json")
    else:
        check_log(sys.argv[1])

