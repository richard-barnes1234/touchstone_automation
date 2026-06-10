# peril_lookup.py
# ─────────────────────────────────────────────────────────────────────────────
# Loads PerilSetCode → Description mapping from file.
# Source: AIRReference.dbo.tPerilSet (tab-delimited export from SSMS)
# ─────────────────────────────────────────────────────────────────────────────

import os
import pandas as pd


def _load_peril_set():
    """Loads peril set lookup. Tries multiple filenames, always uses tab delimiter."""
    candidates = [
        "PerilSetCoes_sov.txt",
        "peril_set.txt",
        "peril_set.csv",
    ]

    for fname in candidates:
        if not os.path.exists(fname):
            continue
        try:
            # Always read with tab — the SSMS export is tab-delimited
            df = pd.read_csv(fname, sep='\t', encoding='utf-8', on_bad_lines='skip')
            df.columns = [c.strip() for c in df.columns]

            if len(df.columns) < 2:
                # Try with encoding that handles Windows line endings
                df = pd.read_csv(fname, sep='\t', encoding='cp1252', on_bad_lines='skip')
                df.columns = [c.strip() for c in df.columns]

            if len(df.columns) < 2:
                print(f"  ⚠ {fname} — only {len(df.columns)} column(s) found, skipping")
                continue

            # Identify columns
            code_col = df.columns[0]
            desc_col = df.columns[1]

            lookup = {}
            for _, row in df.iterrows():
                try:
                    lookup[int(str(row[code_col]).strip())] = str(row[desc_col]).strip()
                except (ValueError, TypeError):
                    pass

            if lookup:
                print(f"  ✓ Peril lookup loaded: {len(lookup):,} codes from {fname}")
                return lookup
            else:
                print(f"  ⚠ {fname} parsed but no valid rows found")

        except Exception as e:
            print(f"  ⚠ Failed to load {fname}: {e}")

    print("  ⚠ No peril set file found — descriptions will show as 'Peril Set {code}'")
    return {}


PERIL_SET = _load_peril_set()


def get_peril_description(peril_set_code):
    """Returns full peril description for a given PerilSetCode."""
    try:
        code = int(peril_set_code)
        return PERIL_SET.get(code, f"Peril Set {code}")
    except (TypeError, ValueError):
        return str(peril_set_code) if peril_set_code else "Unknown"


def enrich_with_peril(df):
    """
    Adds PerilDescription column to a DataFrame containing PeriSetCode.
    Inserts right after PeriSetCode. Safe to call on any DataFrame.
    """
    if df is None or df.empty:
        return df
    col = next((c for c in df.columns if c in ('PerilCode', 'PeriSetCode', 'PerilSetCode')), None)
    if not col:
        return df
    df = df.copy()
    df.insert(
        df.columns.get_loc('PerilDescription') + 1,
        'PerilDescription',
        df[col].apply(get_peril_description)
    )
    return df


def get_unique_perils(df):
    """Returns sorted list of unique peril descriptions in a DataFrame."""
    if df is None or df.empty or 'PeriSetCode' not in df.columns:
        return []
    codes = df['PeriSetCode'].dropna().unique()
    return sorted({get_peril_description(c) for c in codes})


if __name__ == "__main__":
    print(f"\nPeril Set Lookup — {len(PERIL_SET):,} codes loaded")
    print("\nSample entries:")
    for code in [1, 4, 7, 15, 16, 32, 64, 256]:
        print(f"  Code {code:>6}  →  {get_peril_description(code)}")