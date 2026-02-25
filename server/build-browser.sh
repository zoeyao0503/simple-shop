#!/usr/bin/env bash
set -o errexit

# Pin Playwright browser path so build and runtime use the same location.
# This is also set via PLAYWRIGHT_BROWSERS_PATH in render.yaml envVars,
# but we export it here as a safety net.
export PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-/opt/render/project/.playwright-browsers}"

pip install --upgrade pip
pip install -r requirements.txt

apt-get update -yq
apt-get install -yq --no-install-recommends \
  libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
  libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 \
  libpango-1.0-0 libcairo2 libasound2 libxshmfence1 libx11-xcb1 \
  fonts-liberation

playwright install chromium
echo "Chromium installed to: $PLAYWRIGHT_BROWSERS_PATH"
ls -la "$PLAYWRIGHT_BROWSERS_PATH"
