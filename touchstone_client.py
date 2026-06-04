# touchstone_client.py
# Fetches all Analysis SIDs and names from Touchstone SOAP API.

import xml.etree.ElementTree as ET
import pandas as pd
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from api_client import send_soap_request
from config import BUSINESS_UNIT_SID, SQL_INSTANCE_SID
from soap_templates import (
    get_detailed_loss_analyses,
    get_loss_analysis_event_results,
    get_loss_analysis_annual_results,
    get_loss_analysis_summary_results,
    get_hazard_analysis_results,
)


def get_analysis_sids():
    """
    Calls GetDetailedLossAnalyses.
    Returns a list of dicts: [ { "AnalysisSid": 63, "Name": "DefaultUW" }, ... ]
    """
    soap     = get_detailed_loss_analyses(BUSINESS_UNIT_SID, SQL_INSTANCE_SID)
    response = send_soap_request(soap)

    if response.status_code != 200:
        raise Exception(f"API call failed — status {response.status_code}")

    root    = ET.fromstring(response.text)
    results = []

    for elem in root.iter():
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
        if tag == 'DetailedLossAnalysis':
            sid  = None
            name = None
            for child in elem:
                child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                if child_tag == 'Sid':
                    sid = child.text
                elif child_tag == 'Name':
                    name = child.text
            if sid:
                results.append({
                    "AnalysisSid": int(sid),
                    "Name":        name or f"Analysis {sid}"
                })

    if not results:
        all_tags = sorted({
            elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            for elem in root.iter()
        })
        raise Exception(f"No analyses found. Tags in response: {all_tags}")

    results.sort(key=lambda x: x["AnalysisSid"], reverse=True)
    return results


def get_all_loss_data(analysis_sid):
    """Fetches ELT, EP Curves, Loss Summary for a given AnalysisSid"""

    def _parse(response_text, element_tag):
        root    = ET.fromstring(response_text)
        records = []
        for elem in root.iter():
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            if tag == element_tag:
                record = {}
                for child in elem:
                    child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                    record[child_tag] = child.text
                if record:
                    records.append(record)
        return pd.DataFrame(records)

    results = {}

    try:
        r = send_soap_request(get_loss_analysis_event_results(BUSINESS_UNIT_SID, SQL_INSTANCE_SID, analysis_sid))
        results['ELT'] = _parse(r.text, 'EventLoss') if r.status_code == 200 else pd.DataFrame()
    except:
        results['ELT'] = pd.DataFrame()

    try:
        r = send_soap_request(get_loss_analysis_annual_results(BUSINESS_UNIT_SID, SQL_INSTANCE_SID, analysis_sid))
        results['EP Curves'] = _parse(r.text, 'AnnualEPData') if r.status_code == 200 else pd.DataFrame()
    except:
        results['EP Curves'] = pd.DataFrame()

    try:
        r = send_soap_request(get_loss_analysis_summary_results(BUSINESS_UNIT_SID, SQL_INSTANCE_SID, analysis_sid))
        results['Loss Summary'] = _parse(r.text, 'SummaryEPDistribution') if r.status_code == 200 else pd.DataFrame()
    except:
        results['Loss Summary'] = pd.DataFrame()

    return results


def get_hazard_results(analysis_sid):
    """
    Fetches hazard analysis results for a given HazardAnalysisSid.
    Returns a dict of DataFrames keyed by hazard category.
    """

    def _parse(response_text):
        """
        Parses HAZ response — groups records by their parent element tag
        so each hazard category becomes its own DataFrame.
        """
        root       = ET.fromstring(response_text)
        categories = {}

        # Known HAZ result element tags
        haz_tags = {
            'EarthquakeHazard', 'HurricaneHazard', 'FloodHazard',
            'SevereThunderstormHazard', 'ExposureAttributeProfile',
            'HazardResult', 'LocationHazard'
        }

        for elem in root.iter():
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            if tag in haz_tags:
                record = {}
                for child in elem:
                    child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                    record[child_tag] = child.text
                if record:
                    if tag not in categories:
                        categories[tag] = []
                    categories[tag].append(record)

        # If no known tags found do a broad sweep
        if not categories:
            all_tags = set()
            for elem in root.iter():
                t = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                all_tags.add(t)
            print(f"    ⚠ No HAZ elements found. All tags: {sorted(all_tags)}")

        return {k: pd.DataFrame(v) for k, v in categories.items()}

    try:
        soap     = get_hazard_analysis_results(BUSINESS_UNIT_SID, SQL_INSTANCE_SID, analysis_sid)
        response = send_soap_request(soap)
        if response.status_code == 200:
            results = _parse(response.text)
            print(f"    ✓ HAZ results: {list(results.keys())}")
            return results
        else:
            print(f"    ✗ HAZ fetch failed — status {response.status_code}")
            return {}
    except Exception as e:
        print(f"    ✗ HAZ fetch error: {e}")
        return {}


if __name__ == "__main__":
    print("Fetching Analysis SIDs from Touchstone...")
    try:
        analyses = get_analysis_sids()
        print(f"✓ {len(analyses)} analyses found\n")
        for a in analyses[:10]:
            print(f"  SID {a['AnalysisSid']:>6}  —  {a['Name']}")
        if len(analyses) > 10:
            print(f"  ... and {len(analyses) - 10} more")
    except Exception as e:
        print(f"✗ Failed: {e}")