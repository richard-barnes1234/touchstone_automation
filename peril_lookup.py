# peril_lookup.py
# ─────────────────────────────────────────────────────────────────────────────
# Loads PerilSetCode → Description mapping from peril_set.csv
# Source: AIRReference.dbo.tPerilSet (exported via SSMS)
#
# To update: re-export tPerilSet from SSMS and replace peril_set.csv
# No code changes needed.
# ─────────────────────────────────────────────────────────────────────────────

import os
import pandas as pd

# ── Load lookup from file ─────────────────────────────────────────────────────

def _load_peril_set():
    """Loads peril set lookup from file. Falls back to empty dict if file missing."""
    paths = [
        "peril_set.csv",
        "PerilSetCoes_sov.txt",
        os.path.join(os.path.dirname(__file__), "peril_set.csv"),
        os.path.join(os.path.dirname(__file__), "peril_set.csv"),
    ]
    for path in paths:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path, sep=None, engine='python')
                # Normalize column names
                df.columns = [c.strip() for c in df.columns]
                code_col = next((c for c in df.columns if 'peril' in c.lower() and 'code' in c.lower()), df.columns[0])
                desc_col = next((c for c in df.columns if 'desc' in c.lower()), df.columns[1])
                lookup = {}
                for _, row in df.iterrows():
                    try:
                        lookup[int(row[code_col])] = str(row[desc_col]).strip()
                    except (ValueError, TypeError):
                        pass
                print(f"  ✓ Peril lookup loaded: {len(lookup):,} codes from {path}")
                return lookup
            except Exception as e:
                print(f"  ⚠ Failed to load {path}: {e}")
    print("  ⚠ No peril set file found — using empty lookup")
    return {}


PERIL_SET = _load_peril_set()


# ── Public functions ───────────────────────────────────────────────────────────

def get_peril_description(peril_set_code):
    """Returns full peril description for a given PerilSetCode"""
    try:
        code = int(peril_set_code)
        return PERIL_SET.get(code, f"Peril Set {code}")
    except (TypeError, ValueError):
        return str(peril_set_code) if peril_set_code else "Unknown"


def enrich_with_peril(df):
    """
    Adds PerilDescription column to a DataFrame containing PeriSetCode.
    Inserts it right after PeriSetCode. Safe to call on any DataFrame.
    """
    if df is None or df.empty:
        return df
    if 'PeriSetCode' not in df.columns:
        return df
    df = df.copy()
    df.insert(
        df.columns.get_loc('PeriSetCode') + 1,
        'PerilDescription',
        df['PeriSetCode'].apply(get_peril_description)
    )
    return df


def get_unique_perils(df):
    """
    Returns sorted list of unique peril descriptions in a DataFrame.
    Used to populate peril badges in the UI.
    """
    if df is None or df.empty or 'PeriSetCode' not in df.columns:
        return []
    codes = df['PeriSetCode'].dropna().unique()
    return sorted({get_peril_description(c) for c in codes})


if __name__ == "__main__":
    print(f"\nPeril Set Lookup — {len(PERIL_SET):,} codes loaded")
    print("\nSample entries:")
    for code in [1, 4, 7, 15, 16, 32, 64, 256, 9983]:
        print(f"  Code {code:>6}  →  {get_peril_description(code)}")