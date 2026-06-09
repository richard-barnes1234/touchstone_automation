# get_exposure_fields.py
# ─────────────────────────────────────────────────────────────────────────────
# PURPOSE:
#   Discovers the full AIR field schema that Touchstone expects in SOV uploads.
#
# HOW IT WORKS:
#   Step 1 — Calls GetExposureSets to get the first available ExposureSetSid
#   Step 2 — Calls GetExposureViews with that SID to retrieve all field definitions
#   Step 3 — Parses and prints every field: name, data type, required/optional
#   Step 4 — Saves the full field list to air_fields.csv
#
# SAFE TO RUN: Read-only calls only. Nothing is written to Touchstone.
# ─────────────────────────────────────────────────────────────────────────────

import xml.etree.ElementTree as ET
import xml.dom.minidom
import pandas as pd
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from api_client import send_soap_request
from config import BUSINESS_UNIT_SID, SQL_INSTANCE_SID, DATA_SOURCE_SID


# ── SOAP TEMPLATE: GetExposureSets ───────────────────────────────────────────

def soap_get_exposure_sets():
    return f"""<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
        xmlns:a="http://www.w3.org/2005/08/addressing">
  <s:Header>
    <a:Action s:mustUnderstand="1">AIR.Services.DataSourceManagementService.Api/IDataSourceManagementService/GetExposureSets</a:Action>
    <a:MessageID>urn:uuid:f23aa50c-9a41-4932-bd0e-51a37913fde1</a:MessageID>
    <a:ReplyTo><a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address></a:ReplyTo>
    <a:To s:mustUnderstand="1">https://crcins-na-prod-touchstoneapi.air-worldwide.com/FEP/AirServiceFacade.svc</a:To>
  </s:Header>
  <s:Body>
    <GetExposureSets xmlns="AIR.Services.DataSourceManagementService.Api">
      <request xmlns:b="AIR.Services.DataSourceManagement.Api"
               xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
        <BusinessUnitSid xmlns="AIR.Services.Common.Api">{BUSINESS_UNIT_SID}</BusinessUnitSid>
        <LicenseUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</LicenseUid>
        <RequestUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</RequestUid>
        <SqlInstanceSid xmlns="AIR.Services.Common.Api">{SQL_INSTANCE_SID}</SqlInstanceSid>
        <b:DataSourceSid>{DATA_SOURCE_SID}</b:DataSourceSid>
      </request>
    </GetExposureSets>
  </s:Body>
</s:Envelope>"""


# ── SOAP TEMPLATE: GetExposureViews ──────────────────────────────────────────

def soap_get_exposure_views(exposure_set_sid):
    return f"""<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
        xmlns:a="http://www.w3.org/2005/08/addressing">
  <s:Header>
    <a:Action s:mustUnderstand="1">AIR.Services.ProjectManagementService.Api/IProjectManagementService/GetExposureViews</a:Action>
    <a:MessageID>urn:uuid:a1b2c3d4-e5f6-7890-abcd-ef1234567890</a:MessageID>
    <a:ReplyTo><a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address></a:ReplyTo>
    <a:To s:mustUnderstand="1">https://crcins-na-prod-touchstoneapi.air-worldwide.com/FEP/AirServiceFacade.svc</a:To>
  </s:Header>
  <s:Body>
    <GetExposureViews xmlns="AIR.Services.ProjectManagementService.Api">
      <request xmlns:b="AIR.Services.ProjectManagement.Api"
               xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
        <BusinessUnitSid xmlns="AIR.Services.Common.Api">{BUSINESS_UNIT_SID}</BusinessUnitSid>
        <LicenseUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</LicenseUid>
        <RequestUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</RequestUid>
        <SqlInstanceSid xmlns="AIR.Services.Common.Api">{SQL_INSTANCE_SID}</SqlInstanceSid>
        <b:ExposureSetSid>{exposure_set_sid}</b:ExposureSetSid>
      </request>
    </GetExposureViews>
  </s:Body>
</s:Envelope>"""


# ── STEP 1: Get first ExposureSetSid ─────────────────────────────────────────

def get_first_exposure_set_sid():
    print("\n" + "="*60)
    print("  STEP 1 — Fetching Exposure Sets...")
    print("="*60)

    response = send_soap_request(soap_get_exposure_sets())
    print(f"  Status: {response.status_code}")

    if response.status_code != 200:
        print(f"  ✗ Failed to fetch exposure sets")
        print(response.text[:500])
        return None

    root = ET.fromstring(response.text)
    sids = []

    for elem in root.iter():
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
        if tag == 'Sid' and elem.text and elem.text.strip() not in ('0', ''):
            sids.append(elem.text.strip())

    if not sids:
        print("  ✗ No ExposureSetSids found in response")
        print("\n  Raw response (first 1000 chars):")
        print(response.text[:1000])
        return None

    # Deduplicate and take first
    unique_sids = list(dict.fromkeys(sids))
    first_sid = unique_sids[0]
    print(f"  ✓ Found {len(unique_sids)} SID(s) — using first: {first_sid}")
    return first_sid


# ── STEP 2: Call GetExposureViews ─────────────────────────────────────────────

def get_exposure_views(exposure_set_sid):
    print("\n" + "="*60)
    print(f"  STEP 2 — Calling GetExposureViews (SID: {exposure_set_sid})...")
    print("="*60)

    response = send_soap_request(soap_get_exposure_views(exposure_set_sid))
    print(f"  Status: {response.status_code}")

    if response.status_code != 200:
        print(f"  ✗ GetExposureViews failed")
        print(response.text[:1000])
        return None

    print("  ✓ Response received")
    return response.text


# ── STEP 3: Parse field definitions ──────────────────────────────────────────

def parse_fields(response_text):
    print("\n" + "="*60)
    print("  STEP 3 — Parsing field definitions...")
    print("="*60)

    root = ET.fromstring(response_text)
    fields = []

    # Print raw XML for inspection
    try:
        pretty = xml.dom.minidom.parseString(
            response_text.encode('utf-8')
        ).toprettyxml(indent="  ")
        with open("exposure_views_raw.xml", "w", encoding="utf-8") as f:
            f.write(pretty)
        print("  ✓ Raw XML saved to: exposure_views_raw.xml")
    except Exception as e:
        print(f"  ⚠ Could not save raw XML: {e}")

    # Try to extract field/column definitions
    # Common tag patterns in AIR responses: Column, Field, ViewColumn, FieldDefinition
    field_tags = {'Column', 'Field', 'ViewColumn', 'FieldDefinition',
                  'ExposureViewColumn', 'PropertyDefinition'}

    for elem in root.iter():
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag

        if tag in field_tags:
            field = {}
            for child in elem:
                child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                field[child_tag] = child.text
            if field:
                fields.append(field)

    # If nothing found with known tags, do a broader sweep
    if not fields:
        print("  ⚠ No fields found with standard tags — doing broad sweep...")
        print("  All unique tags in response:")
        all_tags = set()
        for elem in root.iter():
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            all_tags.add(tag)
        for t in sorted(all_tags):
            print(f"    • {t}")

    return fields


# ── STEP 4: Display and save results ─────────────────────────────────────────

def display_and_save(fields):
    print("\n" + "="*60)
    print("  STEP 4 — Results")
    print("="*60)

    if not fields:
        print("  ✗ No field definitions extracted.")
        print("  → Check exposure_views_raw.xml to inspect the full response.")
        print("  → Share the XML with the project and we'll adjust the parser.")
        return

    df = pd.DataFrame(fields)
    print(f"\n  ✓ {len(fields)} field(s) found")
    print(f"\n  Columns in response: {list(df.columns)}")
    print(f"\n{df.to_string()}")

    df.to_csv("air_fields.csv", index=False)
    print(f"\n  ✓ Saved to: air_fields.csv")


# ── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  AIR FIELD SCHEMA DISCOVERY")
    print("  Safe to run — read-only API calls only")
    print("="*60)

    # Step 1 — Get a valid ExposureSetSid
    sid = get_first_exposure_set_sid()
    if not sid:
        print("\n✗ Could not get ExposureSetSid — stopping.")
        exit(1)

    # Step 2 — Call GetExposureViews
    response_text = get_exposure_views(sid)
    if not response_text:
        print("\n✗ GetExposureViews failed — stopping.")
        exit(1)

    # Step 3 — Parse fields
    fields = parse_fields(response_text)

    # Step 4 — Display and save
    display_and_save(fields)

    print("\n" + "="*60)
    print("  DONE")
    print("  Files produced:")
    print("    • exposure_views_raw.xml  — full raw API response")
    print("    • air_fields.csv          — extracted field list")
    print("="*60)