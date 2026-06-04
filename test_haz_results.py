# test_haz_results.py — Tests HAZ results parser

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from get_analysis_sids import get_hazard_analyses_for_project
from touchstone_client import get_hazard_results

PROJECT_SID  = "19731"
PROJECT_NAME = "Affin26"

print("="*55)
print("  HAZ RESULTS PARSER TEST")
print("="*55)

# Step 1 — Get HAZ SIDs
print("\n[1] Fetching HAZ analyses...")
haz = get_hazard_analyses_for_project(PROJECT_SID, PROJECT_NAME)
print(f"    Found: {len(haz)}")

if not haz:
    print("    No HAZ analyses found — exiting")
    exit()

# Step 2 — Test parser on first SID
sid = haz[0]["AnalysisSid"]
print(f"\n[2] Fetching HAZ results for SID: {sid}...")
results = get_hazard_results(sid)

print(f"\n    Categories returned: {list(results.keys())}")
for cat, df in results.items():
    print(f"\n    [{cat}]")
    print(f"    Records  : {len(df):,}")
    print(f"    Columns  : {list(df.columns[:8])}")

print("\n" + "="*55)