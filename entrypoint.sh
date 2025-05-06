#!/bin/bash
echo "🔥 Booting Sandbox Container..."

export PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
export PYTHONPATH=/app

if [ ! -f /ms-playwright/chromium-*/chrome-linux/chrome ]; then
  echo "⚙️ Chromium not found — installing..."
  playwright install chromium
else
  echo "✅ Chromium already installed."
fi

# Keep container alive
exec uvicorn sandbox.sandbox_api:app --host 0.0.0.0 --port 8000
