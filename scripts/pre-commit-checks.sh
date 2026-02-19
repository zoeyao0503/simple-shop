#!/usr/bin/env bash
#
# SnooCommerce pre-commit self-test & deployment-readiness check
# Runs automatically before every commit via the pre-commit framework.
# Exits non-zero (blocking the commit) only for hard errors.
# Prints a DEPLOYMENT SUMMARY with warnings for anything that needs attention.
#
set -euo pipefail

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

ERRORS=()
WARNINGS=()

err()  { ERRORS+=("$1"); }
warn() { WARNINGS+=("$1"); }

REPO_ROOT="$(git rev-parse --show-toplevel)"

# ─── 1. Frontend build check ───────────────────────────────────────────────────
echo -e "${CYAN}[1/7] Frontend build...${NC}"
if [ -f "$REPO_ROOT/package.json" ]; then
  if ! npm run build --prefix "$REPO_ROOT" >/dev/null 2>&1; then
    err "Frontend build (npm run build) FAILED — will break the Render static-site deploy."
  else
    echo -e "  ${GREEN}✓${NC} vite build succeeded"
  fi
else
  warn "No package.json found — skipping frontend build check."
fi

# ─── 2. Python syntax / import check ───────────────────────────────────────────
echo -e "${CYAN}[2/7] Python syntax check...${NC}"
PY_ERRORS=0
while IFS= read -r -d '' pyfile; do
  if ! python3 -c "import py_compile; py_compile.compile('$pyfile', doraise=True)" 2>/dev/null; then
    err "Python syntax error in $pyfile"
    PY_ERRORS=$((PY_ERRORS + 1))
  fi
done < <(find "$REPO_ROOT/server" -name '*.py' -not -path '*__pycache__*' -print0 2>/dev/null)
if [ "$PY_ERRORS" -eq 0 ]; then
  echo -e "  ${GREEN}✓${NC} all .py files compile cleanly"
fi

# ─── 3. Django settings sanity (static analysis — no running server needed) ────
echo -e "${CYAN}[3/7] Django settings audit...${NC}"
SETTINGS="$REPO_ROOT/server/server/settings.py"
if [ -f "$SETTINGS" ]; then
  if grep -q "ALLOWED_HOSTS\s*=\s*\['\*'\]" "$SETTINGS"; then
    warn "ALLOWED_HOSTS = ['*'] — consider restricting to your Render domain(s) for production."
  fi
  if grep -q "CORS_ALLOW_ALL_ORIGINS\s*=\s*True" "$SETTINGS"; then
    warn "CORS_ALLOW_ALL_ORIGINS = True — consider restricting to your frontend origin for production."
  fi
  if grep -q "django-insecure" "$SETTINGS"; then
    warn "SECRET_KEY still contains the insecure dev default. Ensure DJANGO_SECRET_KEY env var is set on Render."
  fi
  echo -e "  ${GREEN}✓${NC} settings.py audited"
else
  warn "server/server/settings.py not found — skipping Django audit."
fi

# ─── 4. render.yaml consistency ─────────────────────────────────────────────────
echo -e "${CYAN}[4/7] render.yaml consistency...${NC}"
RENDER_YAML="$REPO_ROOT/render.yaml"
if [ -f "$RENDER_YAML" ]; then
  SETTINGS_ENVS=$(grep -o "os\.environ\.get('[A-Z_]*'" "$SETTINGS" 2>/dev/null | sed "s/os\.environ\.get('//;s/'//" | sort -u)
  MISSING_IN_RENDER=()
  for var in $SETTINGS_ENVS; do
    if ! grep -q "key: $var" "$RENDER_YAML"; then
      MISSING_IN_RENDER+=("$var")
    fi
  done
  if [ ${#MISSING_IN_RENDER[@]} -gt 0 ]; then
    warn "Env vars used in settings.py but missing from render.yaml: ${MISSING_IN_RENDER[*]}"
  fi

  if ! grep -q "DJANGO_SECRET_KEY" "$RENDER_YAML"; then
    warn "DJANGO_SECRET_KEY not listed in render.yaml — Django will use the insecure default in prod."
  fi
  echo -e "  ${GREEN}✓${NC} render.yaml checked"
else
  warn "No render.yaml found — skipping Render deployment check."
fi

# ─── 5. Pixel ID consistency (index.html ↔ settings.py ↔ render.yaml) ──────────
echo -e "${CYAN}[5/7] Pixel ID consistency...${NC}"
INDEX="$REPO_ROOT/index.html"
if [ -f "$INDEX" ] && [ -f "$SETTINGS" ]; then
  META_PID_HTML=$(grep -o "fbq('init', '[^']*'" "$INDEX" 2>/dev/null | sed "s/fbq('init', '//;s/'//" || true)
  META_PID_PY=$(grep "META_PIXEL_ID" "$SETTINGS" 2>/dev/null | grep -o "'[^']*'" | tail -1 | tr -d "'" || true)
  if [ -n "$META_PID_HTML" ] && [ -n "$META_PID_PY" ] && [ "$META_PID_HTML" != "$META_PID_PY" ]; then
    warn "Meta Pixel ID mismatch — index.html ($META_PID_HTML) vs settings.py default ($META_PID_PY)."
  fi

  TT_PID_HTML=$(grep -o "ttq\.load('[^']*'" "$INDEX" 2>/dev/null | sed "s/ttq\.load('//;s/'//" || true)
  TT_PID_PY=$(grep "TIKTOK_PIXEL_ID" "$SETTINGS" 2>/dev/null | grep -o "'[^']*'" | tail -1 | tr -d "'" || true)
  if [ -n "$TT_PID_HTML" ] && [ -n "$TT_PID_PY" ] && [ "$TT_PID_HTML" != "$TT_PID_PY" ]; then
    warn "TikTok Pixel ID mismatch — index.html ($TT_PID_HTML) vs settings.py default ($TT_PID_PY)."
  fi

  RDT_PID_HTML=$(grep -o "rdt('init', '[^']*'" "$INDEX" 2>/dev/null | sed "s/rdt('init', '//;s/'//" || true)
  RDT_PID_PY=$(grep "REDDIT_PIXEL_ID" "$SETTINGS" 2>/dev/null | grep -o "'[^']*'" | tail -1 | tr -d "'" || true)
  if [ -n "$RDT_PID_HTML" ] && [ -n "$RDT_PID_PY" ] && [ "$RDT_PID_HTML" != "$RDT_PID_PY" ]; then
    warn "Reddit Pixel ID mismatch — index.html ($RDT_PID_HTML) vs settings.py default ($RDT_PID_PY)."
  fi
  echo -e "  ${GREEN}✓${NC} pixel IDs cross-checked"
fi

# ─── 6. Secrets leak check ─────────────────────────────────────────────────────
echo -e "${CYAN}[6/7] Secrets leak scan...${NC}"
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACMR 2>/dev/null || true)
LEAK_FOUND=0
for f in $STAGED_FILES; do
  [ "$f" = ".env" ] || [ "$f" = ".env.local" ] && {
    err ".env file staged for commit — this file contains secrets and MUST stay gitignored."
    LEAK_FOUND=1
    continue
  }
  FULL="$REPO_ROOT/$f"
  [ -f "$FULL" ] || continue
  if grep -iE '(access.token|secret.key)[[:space:]]*[:=][[:space:]]*[^[:space:]]{20,}' "$FULL" 2>/dev/null | grep -qv 'os\.environ' 2>/dev/null; then
    if [[ "$f" != *.example ]] && [[ "$f" != *.sample ]]; then
      err "Possible hardcoded secret in staged file: $f"
      LEAK_FOUND=1
    fi
  fi
done
if [ "$LEAK_FOUND" -eq 0 ]; then
  echo -e "  ${GREEN}✓${NC} no secrets found in staged files"
fi

# ─── 7. API URL / rewrite consistency ──────────────────────────────────────────
echo -e "${CYAN}[7/7] API routing consistency...${NC}"
TRACK_EVENT="$REPO_ROOT/src/lib/trackEvent.js"
if [ -f "$TRACK_EVENT" ]; then
  FE_API_PATH=$(grep -o "fetch('[^']*'" "$TRACK_EVENT" 2>/dev/null | sed "s/fetch('//;s/'//" || true)
  if [ -n "$FE_API_PATH" ] && [ -f "$RENDER_YAML" ]; then
    if ! grep -q "${FE_API_PATH%%\**}" "$RENDER_YAML" 2>/dev/null; then
      warn "Frontend fetches '$FE_API_PATH' but render.yaml rewrite may not cover it."
    fi
  fi
  echo -e "  ${GREEN}✓${NC} API routes cross-checked"
fi

# ─── Summary ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}  DEPLOYMENT READINESS SUMMARY${NC}"
echo -e "${BOLD}═══════════════════════════════════════════════════════════${NC}"

if [ ${#ERRORS[@]} -eq 0 ] && [ ${#WARNINGS[@]} -eq 0 ]; then
  echo -e "  ${GREEN}All checks passed — ready for production.${NC}"
fi

if [ ${#WARNINGS[@]} -gt 0 ]; then
  echo -e ""
  echo -e "  ${YELLOW}⚠  WARNINGS (won't block commit, but review before deploy):${NC}"
  for w in "${WARNINGS[@]}"; do
    echo -e "     ${YELLOW}• $w${NC}"
  done
fi

if [ ${#ERRORS[@]} -gt 0 ]; then
  echo -e ""
  echo -e "  ${RED}✗  ERRORS (commit blocked):${NC}"
  for e in "${ERRORS[@]}"; do
    echo -e "     ${RED}• $e${NC}"
  done
  echo -e "${BOLD}═══════════════════════════════════════════════════════════${NC}"
  exit 1
fi

echo -e "${BOLD}═══════════════════════════════════════════════════════════${NC}"
exit 0
