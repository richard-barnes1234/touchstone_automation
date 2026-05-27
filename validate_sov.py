# validate_sov.py — Validates SOV CSV before uploading to Touchstone

import pandas as pd
import os

def validate_sov(filepath):
    """Validates a SOV CSV file before uploading to Touchstone"""

    print(f"\n{'='*55}")
    print(f"  SOV VALIDATION REPORT")
    print(f"{'='*55}")
    print(f"  File: {os.path.basename(filepath)}")

    # Check file exists
    if not os.path.exists(filepath):
        print(f"  ✗ File not found: {filepath}")
        return False, None

    # Load CSV
    try:
        df = pd.read_csv(filepath)
        print(f"  ✓ File loaded successfully")
        print(f"  Rows         : {len(df):,}")
        print(f"  Columns      : {len(df.columns)}")
    except Exception as e:
        print(f"  ✗ Failed to read CSV: {e}")
        return False, None

    # Check for empty rows
    empty_rows = df.isnull().all(axis=1).sum()
    print(f"  Empty rows   : {empty_rows}")

    # Check for null percentages
    print(f"\n  Null % per column:")
    has_warnings = False
    for col in df.columns:
        null_pct = df[col].isnull().mean() * 100
        if null_pct == 100:
            print(f"    ⚠ {col:<30} 100% null — consider removing")
            has_warnings = True
        elif null_pct > 50:
            print(f"    ⚠ {col:<30} {null_pct:.1f}% null")

    # Preview
    print(f"\n  Columns in file:")
    for col in df.columns:
        print(f"    • {col}")

    print(f"\n  Preview (first 3 rows):")
    print(df.head(3).to_string())

    print(f"\n{'='*55}")
    print(f"  RESULT: ✓ File readable and ready for upload")
    if has_warnings:
        print(f"  ⚠ Some columns are fully null — API will")
        print(f"    reject invalid fields and report them back")
    print(f"{'='*55}\n")

    return True, df

if __name__ == "__main__":
    validate_sov("sample_sov.csv")