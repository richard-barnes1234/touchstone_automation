# test_elt_columns.py

from touchstone_client import get_all_loss_data
from peril_lookup import enrich_with_peril, get_peril_description

print("Step 1 — Testing peril lookup directly...")
print(f"  PerilCode 1  → {get_peril_description(1)}")
print(f"  PerilCode 4  → {get_peril_description(4)}")

print("\nStep 2 — Fetching ELT for Analysis SID 63...")
results = get_all_loss_data(63)
df_elt = results.get('ELT')

print(f"\nStep 3 — ELT shape: {df_elt.shape}")
print(f"Columns ({len(df_elt.columns)}):")
for col in df_elt.columns:
    print(f"  '{col}'")

print(f"\nStep 4 — PerilDescription present: {'PerilDescription' in df_elt.columns}")

print("\nStep 5 — Testing enrich_with_peril directly on the DataFrame...")
from touchstone_client import get_all_loss_data
import xml.etree.ElementTree as ET
from api_client import send_soap_request
from soap_templates import get_loss_analysis_event_results
from config import BUSINESS_UNIT_SID, SQL_INSTANCE_SID

r = send_soap_request(get_loss_analysis_event_results(BUSINESS_UNIT_SID, SQL_INSTANCE_SID, 63))
import pandas as pd
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

df_raw = pd.DataFrame(records)
print(f"  Raw ELT columns: {list(df_raw.columns)}")
print(f"  'PerilCode' in raw: {'PerilCode' in df_raw.columns}")

df_enriched = enrich_with_peril(df_raw)
print(f"  Enriched columns: {list(df_enriched.columns)}")
print(f"  'PerilDescription' in enriched: {'PerilDescription' in df_enriched.columns}")
if 'PerilDescription' in df_enriched.columns:
    print(f"  Sample values: {df_enriched['PerilDescription'].unique()[:3].tolist()}")