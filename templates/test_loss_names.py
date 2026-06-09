# test_loss_names.py — Check what names come back for LOSS analyses

from get_analysis_sids import get_analyses_for_project

PROJECT_SID  = "19731"
PROJECT_NAME = "Affin26"

print(f"Checking LOSS analysis names for: {PROJECT_NAME}")
print("="*55)

analyses = get_analyses_for_project(PROJECT_SID, PROJECT_NAME)
print(f"Found: {len(analyses)}\n")

for a in analyses[:10]:
    name = a.get('AnalysisName', '')
    sid  = a['AnalysisSid']
    print(f"  SID: {sid:<8}  Name: '{name}'")