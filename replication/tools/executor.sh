#!/usr/bin/env bash
# executor.sh
# Usage: executor.sh <target_binary> <candidates_dir> <out_csv>
# Runs the target binary on each input file (stdin) and emits a CSV:
# filename,crashed,exit_code,runtime_ms
#
# Notes:
# - This script is intentionally simple and does NOT collect coverage by default.
# - To collect per-input coverage (bb_hits), compile the target with gcov or use kcov and extend this script.

set -eu

if [ "$#" -ne 3 ]; then
  echo "Usage: $0 <target_binary> <candidates_dir> <out_csv>"
  exit 2
fi

TARGET="$1"
CAND_DIR="$2"
OUT_CSV="$3"

mkdir -p "$(dirname "$OUT_CSV")"
echo "filename,crashed,exit_code,runtime_ms" > "$OUT_CSV"

# iterate over files (non-recursive). Support any extension.
for f in "$CAND_DIR"/*; do
  [ -e "$f" ] || continue
  fname="$(basename "$f")"
  # temp file for stderr
  errf="$(mktemp)"
  start=$(date +%s%3N)
  # run with timeout to avoid hangs (5s); adapt as needed
  if timeout 5s "$TARGET" < "$f" 2> "$errf"; then
    rc=$?
  else
    rc=$?
  fi
  end=$(date +%s%3N)
  runtime_ms=$((end - start))

  crashed=0
  if grep -q "ERROR: AddressSanitizer" "$errf" 2>/dev/null; then
    crashed=1
  fi
  # also consider non-zero exit codes as "crashed" for our simple pipeline
  if [ "$rc" -ne 0 ]; then
    crashed=1
  fi

  printf "%s,%d,%d,%d\n" "$fname" "$crashed" "$rc" "$runtime_ms" >> "$OUT_CSV"
  rm -f "$errf"
done

echo "Executed $(wc -l < "$OUT_CSV") entries (incl. header)."
