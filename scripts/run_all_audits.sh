#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo ""
echo "  ╔══════════════════════════════════════════════════════════╗"
echo "  ║         Complete Project Audit Suite                    ║"
echo "  ╚══════════════════════════════════════════════════════════╝"
echo ""

TOTAL_PASS=0
TOTAL_FAIL=0

run_audit() {
    local name="$1"
    local script="$2"
    echo ""
    echo "  ┌────────────────────────────────────────────────────────┐"
    printf "  │  %-52s  │\n" "$name"
    echo "  └────────────────────────────────────────────────────────┘"
    set +e
    bash "$script"
    rc=$?
    set -e
    if [ $rc -eq 0 ]; then
        TOTAL_PASS=$((TOTAL_PASS + 1))
    else
        TOTAL_FAIL=$((TOTAL_FAIL + 1))
    fi
    echo ""
    echo "  Press ENTER to continue..."
    read -r
}

run_audit "1. Security Audit" "$SCRIPT_DIR/audit_security.sh"
run_audit "2. Scalability Audit" "$SCRIPT_DIR/audit_scalability.sh"
run_audit "3. Code Quality Audit" "$SCRIPT_DIR/audit_code_quality.sh"
run_audit "4. Performance Audit" "$SCRIPT_DIR/audit_performance.sh"

echo ""
echo "  ╔══════════════════════════════════════════════════════════╗"
echo "  ║                    Final Summary                        ║"
echo "  ╚══════════════════════════════════════════════════════════╝"
echo ""
echo "    Audits passed: $TOTAL_PASS"
echo "    Audits failed: $TOTAL_FAIL"
echo ""
echo "    Reports saved to:"
echo "      - Security:     output/audit_security.log"
echo "      - Scalability:  output/audit_scalability.log"
echo "      - Code Quality: output/audit_code_quality.log"
echo "      - Performance:  output/audit_performance.log"
echo ""
exit $TOTAL_FAIL
