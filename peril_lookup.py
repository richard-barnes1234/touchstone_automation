# peril_lookup.py
# ─────────────────────────────────────────────────────────────────────────────
# Loads PerilSetCode → Description mapping from file.
# Supports .txt (tab-delimited) and .csv (comma-delimited).
# To update: re-export tPerilSet from SSMS and replace the file.
# ─────────────────────────────────────────────────────────────────────────────

import os
import pandas as pd


def _load_peril_set():
    """Loads peril set lookup from file. Returns dict of {code: description}."""
    candidates = [
        ("peril_set.txt",          "\t"),
        ("peril_set.csv",          ","),
        ("PerilSetCoes_sov.txt",   "\t"),
    ]

    for fname, sep in candidates:
        if not os.path.exists(fname):
            continue
        try:
            df = pd.read_csv(fname, sep=sep)
            df.columns = [c.strip() for c in df.columns]

            # Find code and description columns
            code_col = next(
                (c for c in df.columns if 'perilsetcode' in c.lower().replace(' ','')),
                df.columns[0]
            )
            desc_col = next(
                (c for c in df.columns if 'desc' in c.lower()),
                df.columns[1]
            )

            if len(df.columns) < 2:
                print(f"  ⚠ {fname} parsed as single column — wrong delimiter")
                continue

            lookup = {}
            for _, row in df.iterrows():
                try:
                    lookup[int(row[code_col])] = str(row[desc_col]).strip()
                except (ValueError, TypeError):
                    pass

            print(f"  ✓ Peril lookup loaded: {len(lookup):,} codes from {fname}")
            return lookup

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
    if df is None or df.empty or 'PeriSetCode' not in df.columns:
        return df
    df = df.copy()
    df.insert(
        df.columns.get_loc('PeriSetCode') + 1,
        'PerilDescription',
        df['PeriSetCode'].apply(get_peril_description)
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
    for code in [1, 4, 7, 15, 16, 32, 64, 256, 9983]:
        print(f"  Code {code:>6}  →  {get_peril_description(code)}")