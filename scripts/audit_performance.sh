#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "================================================"
echo "  Performance Audit"
echo "================================================"

PASS=0
FAIL=0
WARN=0

check() {
    local name="$1"
    local result="$2"
    echo ""
    echo "--- $name ---"
    echo "$result"
    if echo "$result" | grep -qi "FAIL\|ERROR"; then
        FAIL=$((FAIL + 1))
    elif echo "$result" | grep -qi "WARN"; then
        WARN=$((WARN + 1))
        PASS=$((PASS + 1))
    else
        PASS=$((PASS + 1))
    fi
}

# 1. Check for heavy model loading at import time
IMPORT_TIME=$(cd apps/api && python3 -c "import time; s=time.time(); from src.main import app; print(f'{(time.time()-s)*1000:.0f}ms')" 2>&1 || true)
if [[ "$IMPORT_TIME" =~ ^[0-9] ]]; then
    if [ "${IMPORT_TIME%ms}" -gt 5000 ]; then
        RESULT="  WARN: import takes ${IMPORT_TIME} (model loads at import)"
    else
        RESULT="  PASS: import time ${IMPORT_TIME}"
    fi
else
    RESULT="  WARN: could not measure import time ($IMPORT_TIME)"
fi
check "Import time" "$RESULT"

# 2. Check for lazy imports in endpoints
LAZY_IMPORTS=$(grep -rn "import\|from" apps/api/src/main.py 2>/dev/null | head -20 || true)
if echo "$LAZY_IMPORTS" | grep -q "rembg"; then
    RESULT="  WARN: rembg imported at module level (adds startup latency)"
else
    RESULT="  PASS: no heavy imports at module level"
fi
check "Lazy imports" "$RESULT"

# 3. Check image processing in endpoint (no background task)
if grep -q "remove(" apps/api/src/main.py 2>/dev/null; then
    RESULT="  WARN: image processing runs synchronously in request (blocks the event loop)"
else
    RESULT="  PASS: no blocking calls in endpoint"
fi
check "Blocking calls" "$RESULT"

# 4. Check for missing cache headers
if grep -rn "Cache-Control\|cachecontrol\|cache_control\|@cache" apps/api/src/ --include="*.py" 2>/dev/null; then
    RESULT="  PASS: cache headers found"
else
    RESULT="  WARN: no caching strategy configured"
fi
check "Caching" "$RESULT"

# 5. Check for missing compression middleware
if grep -rn "GZipMiddleware\|CompressMiddleware\|gzip\|compress" apps/api/src/main.py 2>/dev/null; then
    RESULT="  PASS: compression middleware found"
else
    RESULT="  WARN: no compression middleware (consider GZipMiddleware for large images)"
fi
check "Compression" "$RESULT"

# 6. Run pytest-benchmark if available
echo ""
echo "--- Benchmark (pytest-benchmark) ---"
if python3 -c "import pytest_benchmark" 2>/dev/null; then
    cd apps/api && python3 -m pytest tests/ --benchmark-only --benchmark-warmup=on --benchmark-min-rounds=3 2>&1 || true
else
    echo "  pytest-benchmark not installed — skipping benchmark."
    echo "  Install: pip install pytest-benchmark"
fi

echo ""
echo "================================================"
echo "  Performance Audit: $PASS passed, $WARN warnings, $FAIL failed"
echo "================================================"
exit $FAIL
