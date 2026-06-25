#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Activate venv if present
if [ -f "$PROJECT_DIR/venv/bin/activate" ]; then
    source "$PROJECT_DIR/venv/bin/activate"
fi

PYTHON="${PYTHON:-python3}"

echo "================================================"
echo "  Security Audit"
echo "================================================"

PASS=0
FAIL=0

check() {
    local name="$1"
    local cmd="$2"
    echo ""
    echo "--- $name ---"
    if eval "$cmd"; then
        echo "  PASS: $name"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $name"
        FAIL=$((FAIL + 1))
    fi
}

check "Bandit (static analysis)" "$PYTHON -m bandit -r app/ -x venv,tests 2>&1"
check "pip-audit (dependencies)" "$PYTHON -m pip_audit --strict --requirement requirements.txt 2>&1"

echo ""
echo "================================================"
echo "  Security Audit Results: $PASS passed, $FAIL failed"
echo "================================================"
exit $FAIL
