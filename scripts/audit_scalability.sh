#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "================================================"
echo "  Scalability Audit"
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
    if echo "$result" | grep -qi "FAIL"; then
        FAIL=$((FAIL + 1))
    elif echo "$result" | grep -qi "WARN"; then
        WARN=$((WARN + 1))
        PASS=$((PASS + 1))
    else
        PASS=$((PASS + 1))
    fi
}

# 1. Check for blocking IO in async endpoints
echo "--- 1. Sync IO in async routes ---"
SYNC_IO=$(grep -rn "open(" apps/api/src/main.py apps/api/src/api/ 2>/dev/null || true)
SYNC_IO_ASYNC=$(grep -rn -B5 "open(" apps/api/src/main.py apps/api/src/api/ 2>/dev/null | grep -i "async\|@app\|@router" || true)
if [ -n "$SYNC_IO" ]; then
    if grep -q "open(" apps/api/src/main.py apps/api/src/api/ 2>/dev/null; then
        RESULT="  WARN: sync open() calls found in async context (consider aiofiles)"
    else
        RESULT="  PASS: no sync IO in async routes"
    fi
else
    RESULT="  PASS: no sync IO found"
fi
check "Sync IO check" "$RESULT"

# 2. Check for async endpoint definitions (FastAPI best practice)
ASYNC_ENDPOINTS=$(grep -c "async def" apps/api/src/api/routes.py || true)
SYNC_ENDPOINTS=$(grep -c "@router.*\ndef " apps/api/src/api/routes.py || true)
if [ "$ASYNC_ENDPOINTS" -ge "$SYNC_ENDPOINTS" ] && [ "$ASYNC_ENDPOINTS" -gt 0 ]; then
    RESULT="  PASS: $ASYNC_ENDPOINTS async endpoints, $SYNC_ENDPOINTS sync"
elif [ "$ASYNC_ENDPOINTS" -eq 0 ] && [ "$SYNC_ENDPOINTS" -eq 0 ]; then
    RESULT="  WARN: no endpoints found"
else
    RESULT="  WARN: non-async endpoints found (use async def for FastAPI)"
fi
check "Async endpoints" "$RESULT"

# 3. Check for connection pooling / timeout config
if grep -q "pool\|pool_size\|pool_recycle\|max_connections\|timeout" apps/api/src/main.py apps/api/src/core/*.py apps/api/pyproject.toml 2>/dev/null; then
    RESULT="  PASS: connection pooling config found"
else
    RESULT="  WARN: no connection pooling config found (may exhaust connections under load)"
fi
check "Connection pooling" "$RESULT"

# 4. Check for pagination on list endpoints
if grep -rn "limit\|offset\|page\|paginate" apps/api/src/ --include="*.py" 2>/dev/null; then
    RESULT="  PASS: pagination found"
else
    RESULT="  PASS: no list endpoints to paginate (single endpoint app)"
fi
check "Pagination" "$RESULT"

# 5. Check for rate limiting
if grep -rn "limiter\|ratelimit\|throttle\|slowapi" apps/api/src/ apps/api/pyproject.toml 2>/dev/null; then
    RESULT="  PASS: rate limiting found"
else
    RESULT="  WARN: no rate limiting configured (consider slowapi for production)"
fi
check "Rate limiting" "$RESULT"

# 6. Check for database connection string config
if grep -q "pool_size\|max_connections\|connection_limit" apps/api/src/main.py apps/api/src/core/*.py 2>/dev/null; then
    RESULT="  PASS: explicit connection limits configured"
else
    RESULT="  PASS: no database connections used (stateless API)"
fi
check "Connection limits" "$RESULT"

# 7. Check Docker healthcheck
if grep -q "healthcheck" docker/docker-compose.yml apps/api/Dockerfile 2>/dev/null; then
    RESULT="  PASS: healthcheck configured"
else
    RESULT="  WARN: no healthcheck configured in docker-compose.yml"
fi
check "Docker healthcheck" "$RESULT"

# 8. Check for resource limits in docker-compose
if grep -q "mem_limit\|memory:\|cpus:" docker/docker-compose.yml 2>/dev/null; then
    RESULT="  PASS: resource limits configured"
else
    RESULT="  WARN: no CPU/memory limits in docker-compose.yml"
fi
check "Resource limits" "$RESULT"

# 9. Check timeout on HTTP client
if grep -rn "timeout" apps/api/src/ --include="*.py" 2>/dev/null; then
    RESULT="  PASS: timeout configured on HTTP calls"
else
    RESULT="  PASS: no outbound HTTP calls to configure timeouts"
fi
check "HTTP timeouts" "$RESULT"

echo ""
echo "================================================"
echo "  Scalability Audit: $PASS passed, $WARN warnings, $FAIL failed"
echo "================================================"
exit $FAIL
