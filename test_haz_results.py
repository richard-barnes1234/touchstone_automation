# test_haz_results.py — Tests fetching HAZ results for known analyses

import urllib3
import xml.etree.ElementTree as ET
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from api_client import send_soap_request
from config import BUSINESS_UNIT_SID, SQL_INSTANCE_SID
from get_analysis_sids import get_hazard_analyses_for_project
from soap_templates import get_hazard_analysis_results

PROJECT_SID  = "19731"
PROJECT_NAME = "Affin26"

print("="*55)
print("  HAZ ANALYSIS TEST")
print("="*55)

# Step 1 — Get HAZ analyses
print("\n[1] Fetching HAZ analyses...")
haz = get_hazard_analyses_for_project(PROJECT_SID, PROJECT_NAME)
print(f"    Found: {len(haz)}")
print(f"\n    {'SID':<12} {'Name':<20} {'Status':<15} {'Completed'}")
print(f"    {'-'*65}")
for h in haz:
    print(f"    {h['AnalysisSid']:<12} {h['AnalysisName']:<20} {h['Status']:<15} {h.get('Completed','—')}")

# Step 2 — Try fetching results for each SID
print("\n[2] Fetching results for each HAZ SID...")
for h in haz:
    sid = h['AnalysisSid']
    print(f"\n    SID: {sid}")
    try:
        soap     = get_hazard_analysis_results(BUSINESS_UNIT_SID, SQL_INSTANCE_SID, sid)
        response = send_soap_request(soap)
        print(f"    Status : {response.status_code}")

        if response.status_code == 200:
            root = ET.fromstring(response.text)
            # Print all unique tags in response
            tags = sorted({
                elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                for elem in root.iter()
            })
            print(f"    Tags   : {tags}")
        else:
            print(f"    Error  : {response.text[:200]}")
    except Exception as e:
        print(f"    Failed : {e}")

print("\n" + "="*55)