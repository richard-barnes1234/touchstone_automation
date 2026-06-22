# test_analysis_xml.py
# Check ALL XML tags returned by GetDetailedLossAnalyses

import xml.etree.ElementTree as ET
from api_client import send_soap_request
from soap_templates import get_detailed_loss_analyses
from config import BUSINESS_UNIT_SID, SQL_INSTANCE_SID

PROJECT_SID = "19731"

# Build soap with project filter
from soap_templates import get_detailed_loss_analyses
soap = get_detailed_loss_analyses(BUSINESS_UNIT_SID, SQL_INSTANCE_SID, PROJECT_SID)
r    = send_soap_request(soap)

print(f"Status: {r.status_code}")

root = ET.fromstring(r.text)

# Find first DetailedLossAnalysis element and print ALL its children
for elem in root.iter():
    tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
    if tag == 'DetailedLossAnalysis':
        print(f"\nAll fields in first DetailedLossAnalysis:")
        for child in elem:
            child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            print(f"  {child_tag:<35} : {repr(child.text)}")
        break