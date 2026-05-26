# extract_loss_data.py  Extracts loss data from Touchstone API

import xml.etree.ElementTree as ET
from config import BUSINESS_UNIT_SID, SQL_INSTANCE_SID
from soap_templates import (
    get_loss_analysis_event_results,
    get_loss_analysis_annual_results,
    get_loss_analysis_summary_results
)
from api_client import send_soap_request
import urllib3
import pandas as pd
import xml.dom.minidom
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def parse_event_results(response_text):
    """Parses ELT response into a DataFrame"""
    root = ET.fromstring(response_text)
    records = []
    for elem in root.iter():
        if elem.tag.endswith('}EventLoss') or elem.tag == 'EventLoss':
            record = {}
            for child in elem:
                tag = child.tag.split(
                    '}')[-1] if '}' in child.tag else child.tag
                record[tag] = child.text
                if record:
                    records.append(record)
                    return pd.DataFrame(records)


def parse_annual_results(response_text):
    """Parses EP Curve response into a DataFrame"""
    root = ET.fromstring(response_text)
    records = []
    for elem in root.iter():
        if elem.tag.endswith('}AnnualEPData') or elem.tag == 'AnnualEPData':
            record = {}
            for child in elem:
                tag = child.tag.split(
                    '}')[-1] if '}' in child.tag else child.tag
                record[tag] = child.text
                if record:
                    records.append(record)
                    return pd.DataFrame(records)


def parse_summary_results(response_text):
    """Parses Loss Summary response into a DataFrame"""
    root = ET.fromstring(response_text)
    records = []
    for elem in root.iter():
        if elem.tag.endswith('}SummaryEPDistribution') or elem.tag == 'SummaryEPDistribution':
            record = {}
            for child in elem:
                tag = child.tag.split(
                    '}')[-1] if '}' in child.tag else child.tag
                record[tag] = child.text
                if record:
                    records.append(record)
                    return pd.DataFrame(records)


def extract_all_loss_data(analysis_sid, output_folder="."):
    """Extracts all loss data for a given analysis SID"""

    print(f"\nExtracting loss data for Analysis SID: {analysis_sid}")
    print("="*50)

# 1. ELT
    print("\n1. Fetching Event Loss Table (ELT)...")
    response = send_soap_request(
        get_loss_analysis_event_results(
            BUSINESS_UNIT_SID, SQL_INSTANCE_SID, analysis_sid)
    )
    if response.status_code == 200:
        df_elt = parse_event_results(response.text)
        df_elt.to_csv(f"{output_folder}/elt_{analysis_sid}.csv", index=False)
        print(f"    ELT saved  {len(df_elt)} records")
    else:
        print(f"    Failed: {response.status_code}")

# 2. EP Curves
    print("\n2. Fetching EP Curves (Annual Results)...")
    response = send_soap_request(
        get_loss_analysis_annual_results(
            BUSINESS_UNIT_SID, SQL_INSTANCE_SID, analysis_sid)
    )
    if response.status_code == 200:
        df_ep = parse_annual_results(response.text)
        df_ep.to_csv(
            f"{output_folder}/ep_curves_{analysis_sid}.csv", index=False)
        print(f"    EP Curves saved  {len(df_ep)} records")
    else:
        print(f"    Failed: {response.status_code}")

# 3. Loss Summary
    print("\n3. Fetching Loss Summary...")
    response = send_soap_request(
        get_loss_analysis_summary_results(
            BUSINESS_UNIT_SID, SQL_INSTANCE_SID, analysis_sid)
    )
    if response.status_code == 200:
        df_summary = parse_summary_results(response.text)
        df_summary.to_csv(
            f"{output_folder}/loss_summary_{analysis_sid}.csv", index=False)
        print(f"    Loss Summary saved  {len(df_summary)} records")
    else:
        print(f"    Failed: {response.status_code}")


print("\n" + "="*50)
print("Extraction complete!")

# Run for analysis SID 63
if __name__ == "__main__":
    extract_all_loss_data(63)
