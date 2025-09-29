#!/usr/bin/env python3
"""
featurize.py
Compute simple input-level features and merge with execution metadata.

Usage:
  python3 featurize.py --candidates replication/candidates --exec replication/exec_results.csv --out replication/data.csv --candidates-out replication/candidates_features.csv

Outputs:
 - labeled data CSV (data.csv) with columns:
   filename,len,entropy,num_digits,byte_runs,bb_hits,path_depth,label
 - candidates features CSV (candidates_features.csv) similar but without label
"""

import argparse
import os
import numpy as np
import pandas as pd

def shannon_entropy(bs: bytes) -> float:
    if len(bs) == 0:
        return 0.0
    counts = np.bincount(np.frombuffer(bs, dtype=np.uint8), minlength=256)
    probs = counts[counts > 0] / len(bs)
    return -float(np.sum(probs * np.log2(probs)))

def byte_runs(bs: bytes) -> int:
    if len(bs) == 0:
        return 0
    runs = 1
    prev = bs[0]
    for b in bs[1:]:
        if b != prev:
            runs += 1
            prev = b
    return runs

def num_digits(bs: bytes) -> int:
    return int(sum(1 for b in bs if 48 <= b <= 57))

def extract_features_for_file(path):
    with open(path, "rb") as f:
        data = f.read()
    return {
        "filename": os.path.basename(path),
        "len": len(data),
        "entropy": shannon_entropy(data),
        "num_digits": num_digits(data),
        "byte_runs": byte_runs(data),
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--candidates", required=True)
    p.add_argument("--exec", required=False, help="execution CSV path (optional)")
    p.add_argument("--out", required=True, help="labeled output CSV")
    p.add_argument("--cands-out", required=False, help="unlabeled candidate features output CSV")
    args = p.parse_args()

    files = []
    for f in sorted(os.listdir(args.candidates)):
        path = os.path.join(args.candidates, f)
        if os.path.isfile(path):
            files.append(path)

    feats = []
    for path in files:
        feats.append(extract_features_for_file(path))
    df_feats = pd.DataFrame(feats).set_index("filename")

    # default columns
    df_feats["bb_hits"] = 0
    df_feats["path_depth"] = 0
    df_feats["label"] = 0

    if args.exec:
        exec_df = pd.read_csv(args.exec)
        # exec_df expected columns: filename, crashed, exit_code, runtime_ms, optionally bb_hits,path_depth
        exec_df = exec_df.set_index("filename")
        # join on filename; missing rows remain as defaults
        for col in ["crashed", "bb_hits", "path_depth"]:
            if col in exec_df.columns:
                df_feats[col] = exec_df[col].reindex(df_feats.index).fillna(0).astype(int)
        # define label: crashed==1 or bb_hits increase logic already done upstream; here we set label = crashed or bb_hits>0
        df_feats["label"] = ((df_feats.get("crashed", 0) == 1) | (df_feats["bb_hits"].astype(int) > 0)).astype(int)

    # output labeled data
    df_feats_reset = df_feats.reset_index()
    df_feats_reset.to_csv(args.out, index=False)

    if args.cands_out:
        # create candidate features without label/crashed if exec file provided we already included them;
        df_cands = df_feats_reset.copy()
        # remove label if you want pure unlabeled candidates:
        # df_cands = df_cands.drop(columns=["label","crashed"], errors="ignore")
        df_cands.to_csv(args.cands_out, index=False)

    print(f"Wrote {args.out}")
    if args.cands_out:
        print(f"Wrote {args.cands_out}")

if __name__ == "__main__":
    main()
