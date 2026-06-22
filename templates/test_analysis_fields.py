# test_analysis_fields.py
# Check what fields come back from GetDetailedLossAnalyses

from get_analysis_sids import get_analyses_for_project

PROJECT_SID  = "19731"
PROJECT_NAME = "Affin26"

print("=" * 55)
print("  ANALYSIS FIELDS TEST")
print("=" * 55)

analyses = get_analyses_for_project(PROJECT_SID, PROJECT_NAME)
print(f"\nFound: {len(analyses)} analyses")
print(f"\nAll fields in first analysis:")
for k, v in analyses[0].items():
    print(f"  {k:<25} : {repr(v)}")

print(f"\nFirst 5 analyses — key fields:")
print(f"  {'SID':<10} {'Name':<20} {'ModelCode':<12} {'Status'}")
print(f"  {'-'*60}")
for a in analyses[:5]:
    print(f"  {a.get('AnalysisSid',''):<10} {a.get('AnalysisName',''):<20} {a.get('ModelCode',''):<12} {a.get('Status','')}")

print("\n" + "=" * 55)