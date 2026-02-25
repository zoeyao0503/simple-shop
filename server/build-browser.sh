#!/usr/bin/env bash
set -o errexit
pip install --upgrade pip
pip install -r requirements.txt

apt-get update -yq
apt-get install -yq --no-install-recommends \
  libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
  libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 \
  libpango-1.0-0 libcairo2 libasound2 libxshmfence1 libx11-xcb1 \
  fonts-liberation

playwright install chromium
