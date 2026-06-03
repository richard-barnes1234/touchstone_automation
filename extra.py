# test_analysis_fields.py
# Prints ALL fields returned by the API for each analysis
# so we can see exactly what's available

from get_analysis_sids import get_analyses_for_project

analyses = get_analyses_for_project('16726', 'Kistler')
print(f"Found {len(analyses)} analyses\n")

# Print ALL fields for first analysis
if analyses:
    print("ALL FIELDS FOR FIRST ANALYSIS:")
    print("-" * 40)
    for key, value in analyses[0].items():
        print(f"  {key}: {value}")