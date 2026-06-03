# test_haz_type.py
from get_analysis_sids import get_analyses_for_project

# National26 - Hazard Analysis project
analyses = get_analyses_for_project('16726', 'Kistler')
print(f"Found {len(analyses)} analyses\n")
for a in analyses:
    print(f"SID {a['AnalysisSid']}  Type: {a['AnalysisType']}  {a['AnalysisName']}")