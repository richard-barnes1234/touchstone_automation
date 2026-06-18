# model_lookup.py
# ─────────────────────────────────────────────────────────────────────────────
# Loads ModelCode → Model name mapping from file.
# Source: AIRReference.dbo.tModel (tab-delimited export from SSMS)
#
# To update: re-export tModel from SSMS and replace ModelCodes_sov.txt
# ─────────────────────────────────────────────────────────────────────────────

import os
import pandas as pd


def _load_model_set():
    """Loads model code lookup. Returns dict of {code: model_name}."""
    candidates = [
        "ModelCodes_sov.txt",
        "model_codes.txt",
        "model_codes.csv",
    ]

    for fname in candidates:
        if not os.path.exists(fname):
            continue
        try:
            df = pd.read_csv(fname, sep='\t', encoding='utf-8', on_bad_lines='skip')
            df.columns = [c.strip() for c in df.columns]

            if len(df.columns) < 2:
                df = pd.read_csv(fname, sep='\t', encoding='cp1252', on_bad_lines='skip')
                df.columns = [c.strip() for c in df.columns]

            if len(df.columns) < 2:
                print(f"  ⚠ {fname} — only {len(df.columns)} column(s) found, skipping")
                continue

            code_col = df.columns[0]   # ModelCode
            name_col = df.columns[1]   # Model

            lookup = {}
            for _, row in df.iterrows():
                try:
                    lookup[int(str(row[code_col]).strip())] = str(row[name_col]).strip()
                except (ValueError, TypeError):
                    pass

            if lookup:
                print(f"  ✓ Model lookup loaded: {len(lookup):,} codes from {fname}")
                return lookup
            else:
                print(f"  ⚠ {fname} parsed but no valid rows found")

        except Exception as e:
            print(f"  ⚠ Failed to load {fname}: {e}")

    print("  ⚠ No model code file found — descriptions will show as 'Model {code}'")
    return {}


MODEL_SET = _load_model_set()


def get_model_description(model_code):
    """Returns full model name for a given ModelCode."""
    try:
        code = int(model_code)
        return MODEL_SET.get(code, f"Model {code}")
    except (TypeError, ValueError):
        return str(model_code) if model_code else "Unknown"


def enrich_with_model(df):
    """
    Adds ModelDescription column to a DataFrame containing ModelCode.
    Inserts right after ModelCode. Safe to call on any DataFrame.
    """
    if df is None or df.empty or 'ModelCode' not in df.columns:
        return df
    df = df.copy()
    df.insert(
        df.columns.get_loc('ModelCode') + 1,
        'ModelDescription',
        df['ModelCode'].apply(get_model_description)
    )
    return df


def get_unique_models(df):
    """Returns sorted list of unique model names in a DataFrame."""
    if df is None or df.empty or 'ModelCode' not in df.columns:
        return []
    codes = df['ModelCode'].dropna().unique()
    return sorted({get_model_description(c) for c in codes})


if __name__ == "__main__":
    print(f"\nModel Lookup — {len(MODEL_SET):,} codes loaded")
    print("\nSample entries:")
    for code in [1, 21, 27, 11, 84]:
        print(f"  Code {code:>4}  →  {get_model_description(code)}")