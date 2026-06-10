# debug_peril.py
import os
import pandas as pd

fname = "peril_set.csv"

print(f"File exists: {os.path.exists(fname)}")
print(f"File size  : {os.path.getsize(fname):,} bytes")

# Try reading it
df = pd.read_csv(fname, sep='\t')
print(f"Rows       : {len(df):,}")
print(f"Columns    : {list(df.columns)}")
print(f"\nFirst 3 rows:")
print(df.head(3).to_string())