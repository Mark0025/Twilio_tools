#!/bin/bash

# Test the lookup-error CLI subcommand for common Twilio error codes
# Results are stored in tests/cli_test_results.json

set -e

cd "$(dirname "$0")/.."  # Go to TwilioApp root

VENV=".venv/bin/activate"
CLI="src/cli.py"
LOG="tests/logs/test.log"
RESULTS="tests/cli_test_results.json"

if [ ! -f "$VENV" ]; then
  echo "Virtual environment not found. Please run setup_twilio_cli.sh first."
  exit 1
fi

source "$VENV"

# Test error codes
ERROR_CODES=(21610 30006 31002 99999)

declare -A options
options[lookup_error_21610]="Lookup error 21610"
options[lookup_error_30006]="Lookup error 30006"
options[lookup_error_31002]="Lookup error 31002"
options[lookup_error_99999]="Lookup error 99999 (not found)"

for code in "${ERROR_CODES[@]}"; do
  python "$CLI" lookup-error "$code" > /dev/null 2>&1
  if grep -q "Looked up error code $code" "$LOG"; then
    status="success"
  else
    status="fail"
  fi
  # Append to results JSON
  printf '{"option": "lookup_error_%s", "feature": "%s", "status": "%s", "timestamp": "%s"},\n' \
    "$code" "${options[lookup_error_$code]}" "$status" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$RESULTS"
  echo "Tested lookup-error $code: $status"
done

echo "CLI lookup-error tests complete. Results in $RESULTS." 