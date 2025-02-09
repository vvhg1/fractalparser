#!/bin/bash
set -e # Exit on error

# Define input files (arguments or hardcoded)
parser_output="output.md"
expected_output="expected.md"
python3 fparse.py

# Compare
if ! diff -u $parser_output $expected_output; then
    echo "Test failed: Markdown output does not match expected result."
    # show the diff
    diff -u $parser_output $expected_output
    exit 1
else
    echo "Test passed: JSON output matches expected result."
fi
