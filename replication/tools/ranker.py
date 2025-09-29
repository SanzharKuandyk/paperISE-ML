#!/usr/bin/env python3
"""
ranker.py
Train a RandomForest on labeled data and rank unlabeled candidates.

Usage:
  python3 ranker.py --input replication/data.csv --candidates replication/candidates_features.csv --out replication/ranked.csv
"""

import argparse
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="labeled csv")
    p.add_argument("--candidates", required=True, help="candidate features csv (unlabeled)")
    p.add_argument("--out", required=True, help="ranked output csv")
    p.add_argument("--model-out", required=False, default="replication/rf_model.pkl")
    args = p.parse_args()

    df = pd.read_csv(args.input)
    # ensure expected columns
    features = ['len','entropy','num_digits','byte_runs','bb_hits','path_depth']
    for c in features:
        if c not in df.columns:
            df[c] = 0

    X = df[features].fillna(0)
    if 'label' not in df.columns:
        raise SystemExit("Input CSV must contain 'label' column (0/1).")
    y = df['label'].astype(int)

    clf = RandomForestClassifier(n_estimators=50, class_weight='balanced', random_state=42)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(clf, X, y, cv=cv, scoring='roc_auc')
    print(f"CV ROC-AUC: {scores.mean():.3f} ± {scores.std():.3f}")
    clf.fit(X, y)
    joblib.dump(clf, args.model_out)
    print(f"Saved model to {args.model_out}")

    # rank candidates
    cands = pd.read_csv(args.candidates)
    for c in features:
        if c not in cands.columns:
            cands[c] = 0
    Xc = cands[features].fillna(0)
    probs = clf.predict_proba(Xc)[:,1]
    cands['score'] = probs
    cands = cands.sort_values('score', ascending=False)
    cands.to_csv(args.out, index=False)
    print(f"Wrote ranked candidates to {args.out}")

if __name__ == "__main__":
    main()
