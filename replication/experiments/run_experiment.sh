#!/usr/bin/env bash
# run_experiment.sh
# Simple orchestration for the minimal pipeline. Assumes you are in replication/ directory.
set -eu

ROOT_DIR="$(cd "$(dirname "$0")/.."; pwd)"
echo "Root: $ROOT_DIR"
mkdir -p "$ROOT_DIR/bin"
C_TARGET_SRC="$ROOT_DIR/c_parser.c $ROOT_DIR/c_target.c"
C_TARGET_BIN="$ROOT_DIR/bin/c_target"
CAND_DIR="$ROOT_DIR/candidates"
EXEC_CSV="$ROOT_DIR/exec_results.csv"
DATA_CSV="$ROOT_DIR/data.csv"
CANDS_FEATS="$ROOT_DIR/candidates_features.csv"
RANKED="$ROOT_DIR/ranked.csv"
PRIO_OUT="$ROOT_DIR/prioritized_results.csv"

# Build the C target (simple build). For sanitizers, change flags below.
echo "Building C target..."
clang -O0 -g $C_TARGET_SRC -o "$C_TARGET_BIN" || { echo "Build failed"; exit 1; }

# Ensure candidates exist
if [ ! -d "$CAND_DIR" ]; then
  echo "No candidates directory ($CAND_DIR) - creating and adding samples"
  mkdir -p "$CAND_DIR"
  printf "threads=4\n" > "$CAND_DIR/sample1.txt"
  printf "threads=notanumber\n" > "$CAND_DIR/sample2.txt"
  printf "abc=xyz\n" > "$CAND_DIR/sample3.txt"
  printf "threads=999999999999999999\n" > "$CAND_DIR/sample4.txt"
fi

# Step 1: execute all candidates to collect exec metadata
echo "Executing candidate inputs (this may take time)..."
bash "$ROOT_DIR/tools/executor.sh" "$C_TARGET_BIN" "$CAND_DIR" "$EXEC_CSV"

# Step 2: featurize and merge
echo "Featurizing..."
python3 "$ROOT_DIR/tools/featurize.py" --candidates "$CAND_DIR" --exec "$EXEC_CSV" --out "$DATA_CSV" --cands-out "$CANDS_FEATS"

# Step 3: train and rank
echo "Training ranker and ranking candidates..."
python3 "$ROOT_DIR/tools/ranker.py" --input "$DATA_CSV" --candidates "$CANDS_FEATS" --out "$RANKED"

# Step 4: prioritized re-execution: pick top N
TOPN=5
echo "Re-executing top $TOPN ranked candidates..."
head -n $((TOPN+1)) "$RANKED" | tail -n $TOPN | awk -F, '{print $1}' > "$ROOT_DIR/top_filenames.txt"

# Prepare prioritized candidate dir
PRIO_DIR="$ROOT_DIR/prioritized_candidates"
rm -rf "$PRIO_DIR"
mkdir -p "$PRIO_DIR"
while read -r fn; do
  cp "$CAND_DIR/$fn" "$PRIO_DIR/$fn"
done < "$ROOT_DIR/top_filenames.txt"

bash "$ROOT_DIR/tools/executor.sh" "$C_TARGET_BIN" "$PRIO_DIR" "$PRIO_OUT"

echo "Prioritized run saved to $PRIO_OUT"
echo "Done."
