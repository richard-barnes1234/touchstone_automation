# test_analyses.py — Tests loss and hazard analysis fetch for one project

from get_analysis_sids import get_analyses_for_project, get_hazard_analyses_for_project

# Using Kistler — known to have 15 completed analyses
PROJECT_SID  = "16726"
PROJECT_NAME = "Kistler"

print(f"\nTesting project: {PROJECT_NAME} (SID: {PROJECT_SID})")
print("="*50)

# Loss analyses
print("\n[1] Loss Analyses...")
loss = get_analyses_for_project(PROJECT_SID, PROJECT_NAME)
print(f"    Found: {len(loss)}")
for a in loss[:5]:
    print(f"    SID {a['AnalysisSid']}  —  {a['AnalysisName']}  [{a['Status']}]")
if len(loss) > 5:
    print(f"    ... and {len(loss) - 5} more")

# Hazard analyses
print("\n[2] Hazard Analyses...")
haz = get_hazard_analyses_for_project(PROJECT_SID, PROJECT_NAME)
print(f"    Found: {len(haz)}")
for a in haz[:5]:
    print(f"    SID {a['AnalysisSid']}  —  {a['AnalysisName']}  [{a['Status']}]")
if len(haz) > 5:
    print(f"    ... and {len(haz) - 5} more")

print("\n" + "="*50)
print(f"  Total: {len(loss)} loss + {len(haz)} hazard = {len(loss)+len(haz)} analyses")
print("="*50)