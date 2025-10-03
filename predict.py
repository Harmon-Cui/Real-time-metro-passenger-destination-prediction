#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-time destination prediction demo with classifier fallback (RF / NB).
- Spatiotemporal profile match (unique) -> direct destination
- Spatiotemporal profile match (multiple) -> Monte Carlo by 'prob' (or freq-normalized)
- No spatiotemporal profile -> fallback classifier (RandomForest or NaiveBayes) using attributes + context
- If no attributes -> mark UNPROFILED (handled by HPA in aggregation stage)
"""
import argparse
import pandas as pd
import numpy as np
from datetime import datetime

# Optional: scikit-learn for classifiers
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--excel", default="metro_rt_dest_demo.xlsx", help="Path to Excel workbook")
    ap.add_argument("--sheet", default="entries_2018-04-30_xinjiekou", help="Entries sheet name")
    ap.add_argument("--clf", choices=["rf","nb","none"], default="rf", help="Classifier for fallback path")
    ap.add_argument("--out", default="predictions.csv", help="Output CSV path")
    return ap.parse_args()

def time_to_minutes_since_midnight(ts: str) -> int:
    dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S")
    return dt.hour * 60 + dt.minute

def time_to_hour(ts: str) -> int:
    dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S")
    return dt.hour

def load_data(excel_path: str, entries_sheet: str):
    xls = pd.ExcelFile(excel_path)
    entries = pd.read_excel(xls, sheet_name=entries_sheet, dtype={"passenger_id":str, "event_id":str})
    st = pd.read_excel(xls, sheet_name="profile_spatiotemporal", dtype={"passenger_id":str})
    attr = pd.read_excel(xls, sheet_name="profile_attributes", dtype={"passenger_id":str})
    stations = pd.read_excel(xls, sheet_name="stations")
    config = pd.read_excel(xls, sheet_name="config")
    # classifier training data (synthetic)
    try:
        train = pd.read_excel(xls, sheet_name="clf_training")
    except:
        train = None
    return entries, st, attr, stations, config, train

def sample_by_prob(df):
    if "prob" in df.columns and df["prob"].notna().all():
        probs = df["prob"].values.astype(float)
        probs = probs/ probs.sum() if probs.sum()>0 else np.ones(len(df))/len(df)
    else:
        freqs = df["freq"].values.astype(float)
        total = freqs.sum()
        probs = freqs/total if total>0 else np.ones(len(df))/len(df)
    idx = np.random.choice(df.index.values, p=probs)
    return df.loc[idx]

def build_classifier(train_df: pd.DataFrame, clf_type="rf"):
    """
    Build a tiny classifier pipeline.
    features: origin_station_id (num), hour (num), category (cat), pref_cluster (num)
    label: dest_station_id
    """
    if train_df is None or len(train_df)==0:
        return None

    X = train_df[["origin_station_id","hour","category","pref_cluster"]].copy()
    y = train_df["dest_station_id"].astype(int).values

    # preprocess: one-hot for 'category'
    pre = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), ["category"]),
            ("passthrough", "passthrough", ["origin_station_id","hour","pref_cluster"])
        ]
    )

    if clf_type=="rf":
        clf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    elif clf_type=="nb":
        clf = GaussianNB()
    else:
        return None

    pipe = Pipeline(steps=[("pre", pre), ("clf", clf)])
    pipe.fit(X, y)
    return pipe

def predict_row(row, st: pd.DataFrame, attr: pd.DataFrame, clf_pipe):
    m = time_to_minutes_since_midnight(row["event_time"])
    hour = time_to_hour(row["event_time"])
    pid = str(row["passenger_id"])
    oid = int(row["origin_station_id"])

    # spatiotemporal candidates
    cand = st[(st["passenger_id"]==pid) &
              (st["origin_station_id"]==oid) &
              (st["time_bucket_start_min"]<=m) &
              (m<st["time_bucket_end_min"])]
    if len(cand)==1:
        dest = int(cand.iloc[0]["dest_station_id"])
        return dest, "match_unique"
    elif len(cand)>1:
        chosen = sample_by_prob(cand)
        dest = int(chosen["dest_station_id"])
        return dest, "match_mc"
    else:
        # fallback to classifier if attributes exist AND classifier available
        pax_attr = attr[attr["passenger_id"]==pid]
        if len(pax_attr)>0 and clf_pipe is not None:
            X_one = pd.DataFrame([{
                "origin_station_id": oid,
                "hour": hour,
                "category": pax_attr.iloc[0]["category"],
                "pref_cluster": int(pax_attr.iloc[0]["pref_cluster"])
            }])
            pred = clf_pipe.predict(X_one)[0]
            return int(pred), "clf_fallback"
        elif len(pax_attr)>0 and clf_pipe is None:
            return None, "no_st_match_attr_available"
        else:
            return None, "no_profile"

def main():
    args = parse_args()
    entries, st, attr, stations, config, train = load_data(args.excel, args.sheet)

    # ensure dtypes
    entries["passenger_id"] = entries["passenger_id"].astype(str)
    entries["origin_station_id"] = entries["origin_station_id"].astype(int)
    if "event_id" not in entries.columns:
        entries["event_id"] = [f"E{i:06d}" for i in range(len(entries))]

    clf_pipe = None
    if args.clf in ("rf","nb"):
        clf_pipe = build_classifier(train, clf_type=args.clf)

    preds = []
    for _, row in entries.iterrows():
        dest, path = predict_row(row, st, attr, clf_pipe)
        preds.append({
            "event_id": row["event_id"],
            "event_time": row["event_time"],
            "passenger_id": row["passenger_id"],
            "origin_station_id": int(row["origin_station_id"]),
            "dest_pred": dest if dest is not None else "",
            "decision_path": path
        })
    out_df = pd.DataFrame(preds)
    out_df.to_csv(args.out, index=False, encoding="utf-8")
    print(f"Wrote {len(out_df)} predictions to {args.out}")

if __name__ == "__main__":
    main()
