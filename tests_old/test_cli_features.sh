#!/bin/bash

# Test all features of the CLI by mimicking selections
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

# Clear previous log and results
> "$LOG"
> "$RESULTS"

declare -A options
options[1]="Analyze logs"
options[2]="Show summary"
options[3]="Visualize call volume"
options[4]="Exit"

# JSON array start
printf '[' > "$RESULTS"

for i in 1 2 3 4; do
  # Simulate user input (option + exit)
  echo -e "$i\n4" | python "$CLI" menu > /dev/null 2>&1
  # Check if log entry exists
  if grep -q "Menu option selected: $i" "$LOG"; then
    status="success"
  else
    status="fail"
  fi
  # Write result to JSON
  printf '{"option": %d, "feature": "%s", "status": "%s", "timestamp": "%s"}' \
    "$i" "${options[$i]}" "$status" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$RESULTS"
  if [ "$i" -lt 4 ]; then
    printf ',\n' >> "$RESULTS"
  fi
  echo "Tested option $i (${options[$i]}): $status"
done

# JSON array end
printf ']\n' >> "$RESULTS"

echo "All CLI options tested. Results in $RESULTS." 