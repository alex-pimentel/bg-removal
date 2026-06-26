#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

if [ -f "$PROJECT_DIR/venv/bin/activate" ]; then
    source "$PROJECT_DIR/venv/bin/activate"
fi

PYTHON="${PYTHON:-python3}"

echo "================================================"
echo "  Code Quality Audit"
echo "================================================"

PASS=0
FAIL=0
WARN=0

check() {
    local name="$1"
    local cmd="$2"
    local optional="${3:-false}"
    echo ""
    echo "--- $name ---"
    set +e
    output=$(eval "$cmd" 2>&1)
    rc=$?
    set -e
    if [ $rc -eq 0 ]; then
        echo "  PASS: $name"
        PASS=$((PASS + 1))
    elif [ "$optional" = "true" ]; then
        echo "  WARN: $name"
        echo "$output"
        WARN=$((WARN + 1))
    else
        echo "  FAIL: $name"
        echo "$output"
        FAIL=$((FAIL + 1))
    fi
}

check "Ruff (lint)" "$PYTHON -m ruff check apps/api/src/ 2>&1"
check "MyPy (types)" "$PYTHON -m mypy apps/api/src/ --ignore-missing-imports 2>&1" "true"

# Check for TODO/FIXME/HACK/XXX markers
TODOS=$(grep -rn "TODO\|FIXME\|HACK\|XXX" apps/api/src/ --include="*.py" 2>/dev/null || true)
if [ -z "$TODOS" ]; then
    echo "  PASS: no TODO/FIXME markers"
    PASS=$((PASS + 1))
else
    echo "  WARN: TODO/FIXME markers found"
    echo "$TODOS"
    WARN=$((WARN + 1))
fi

# Check for debug print() statements
PRINTS=$(grep -rn "print(" apps/api/src/ apps/web/src/ --include="*.py" --include="*.ts" --include="*.tsx" 2>/dev/null || true)
if [ -z "$PRINTS" ]; then
    echo "  PASS: no print() statements in app code"
    PASS=$((PASS + 1))
else
    echo "  WARN: print() statements found"
    echo "$PRINTS"
    WARN=$((WARN + 1))
fi

# Check for hardcoded secrets
SECRETS=$(grep -rn "password\|secret\|token\|api_key\|api-key" apps/api/src/ apps/web/src/ --include="*.py" --include="*.ts" --include="*.tsx" -i 2>/dev/null || true)
if [ -z "$SECRETS" ]; then
    echo "  PASS: no hardcoded secrets"
    PASS=$((PASS + 1))
else
    echo "  WARN: potential hardcoded secrets found"
    echo "$SECRETS"
    WARN=$((WARN + 1))
fi

echo ""
echo "================================================"
echo "  Code Quality Audit: $PASS passed, $WARN warnings, $FAIL failed"
echo "================================================"
exit $FAIL
