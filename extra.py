python -c "
from get_analysis_sids import get_analyses_for_project
analyses = get_analyses_for_project('1', 'DefaultUW')
for a in analyses:
    print(f\"SID {a['AnalysisSid']}  Type: {a['AnalysisType']}  {a['AnalysisName']}\")
"