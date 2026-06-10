# test_elt_columns.py

import pandas as pd
import xml.etree.ElementTree as ET
from api_client import send_soap_request
from soap_templates import get_loss_analysis_event_results
from config import BUSINESS_UNIT_SID, SQL_INSTANCE_SID
from peril_lookup import enrich_with_peril, get_peril_description

print("Step 1 — Testing peril lookup directly...")
print(f"  PerilCode 1  → {get_peril_description(1)}")
print(f"  PerilCode 4  → {get_peril_description(4)}")

print("\nStep 2 — Fetching raw ELT from API...")
r = send_soap_request(get_loss_analysis_event_results(BUSINESS_UNIT_SID, SQL_INSTANCE_SID, 63))
print(f"  Status: {r.status_code}")

print("\nStep 3 — Parsing ELT...")
root = ET.fromstring(r.text)
records = []
for elem in root.iter():
    tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
    if tag == 'EventLoss':
        record = {}
        for child in elem:
            child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            record[child_tag] = child.text
        if record:
            records.append(record)

df = pd.DataFrame(records)
print(f"  Records: {len(df):,}")
print(f"  Columns: {list(df.columns)}")
print(f"  'PerilCode' present: {'PerilCode' in df.columns}")

print("\nStep 4 — Running enrich_with_peril...")
print(f"  Columns before: {list(df.columns)}")
col_found = next((c for c in df.columns if c in ('PerilCode', 'PeriSetCode', 'PerilSetCode')), None)
print(f"  Column match found: {col_found}")
df_enriched = enrich_with_peril(df)
print(f"  Columns after : {list(df_enriched.columns)}")
print(f"  PerilDescription present: {'PerilDescription' in df_enriched.columns}")
if 'PerilDescription' in df_enriched.columns:
    print(f"  Sample values : {df_enriched['PerilDescription'].unique()[:3].tolist()}")