# touchstone_client.py
# Fetches all Analysis SIDs and names from Touchstone SOAP API.

import xml.etree.ElementTree as ET
import pandas as pd
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from api_client import send_soap_request
from config import BUSINESS_UNIT_SID, SQL_INSTANCE_SID
from model_lookup import enrich_with_model, get_unique_models
from audit_log import audited_call, log_api_call
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


@audited_call("GetAllLossData")
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
        df_elt = _parse(r.text, 'EventLoss') if r.status_code == 200 else pd.DataFrame()
        results['ELT'] = enrich_with_model(df_elt)
        print(f"    ELT columns: {list(results['ELT'].columns[:5])}")
    except Exception as e:
        print(f"    ELT error: {e}")
        results['ELT'] = pd.DataFrame()

    try:
        r = send_soap_request(get_loss_analysis_annual_results(BUSINESS_UNIT_SID, SQL_INSTANCE_SID, analysis_sid))
        df_ep = _parse(r.text, 'AnnualEPData') if r.status_code == 200 else pd.DataFrame()
        results['EP Curves'] = enrich_with_model(df_ep)
    except:
        results['EP Curves'] = pd.DataFrame()

    try:
        r = send_soap_request(get_loss_analysis_summary_results(BUSINESS_UNIT_SID, SQL_INSTANCE_SID, analysis_sid))
        df_summary = _parse(r.text, 'SummaryEPDistribution') if r.status_code == 200 else pd.DataFrame()
        results['Loss Summary'] = enrich_with_model(df_summary)
    except:
        results['Loss Summary'] = pd.DataFrame()

    return results


@audited_call("GetHazardResults")
def get_hazard_results(analysis_sid):
    """
    Fetches ALL paginated hazard analysis results for a given AnalysisSid.
    Returns a dict of DataFrames keyed by hazard category:
      EarthquakeResults, HurricaneResults, FloodResults,
      SevereThunderstormResults, TerrorismResults, LocationInfo
    """

    # Nested category tags inside each HazardAnalysisResult
    CATEGORY_TAGS = {
        'EarthquakeResults', 'HurricaneResults', 'FloodResults',
        'SevereThunderstormResults', 'TerrorismResults'
    }

    # Location-level fields to capture from HazardAnalysisResult directly
    LOCATION_TAGS = {
        'LocationID', 'ContractID', 'LocationInfo', 'Address',
        'City', 'PostalCode', 'Country', 'Latitude', 'Longitude',
        'GeoMatchLevel', 'TotalReplacementValue',
        'ReplacementValueA', 'ReplacementValueB',
        'ReplacementValueC', 'ReplacementValueD', 'AverageAnnualLoss'
    }

    def _parse_page(response_text):
        """Parses one page of HAZ results"""
        root       = ET.fromstring(response_text)
        categories = {cat: [] for cat in CATEGORY_TAGS}
        locations  = []

        for result_elem in root.iter():
            tag = result_elem.tag.split('}')[-1] if '}' in result_elem.tag else result_elem.tag
            if tag != 'HazardAnalysisResult':
                continue

            # Extract location-level fields
            loc_record = {}
            for child in result_elem:
                child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                if child_tag == 'LocationInfo':
                    # LocationInfo is a nested element — flatten its children
                    for sub in child:
                        sub_tag = sub.tag.split('}')[-1] if '}' in sub.tag else sub.tag
                        loc_record[sub_tag] = sub.text
                elif child_tag in LOCATION_TAGS:
                    loc_record[child_tag] = child.text
                elif child_tag in CATEGORY_TAGS:
                    # Parse category sub-fields
                    cat_record = {}
                    # Add location ID for joining
                    cat_record['LocationID'] = loc_record.get('LocationID') or next(
                        (c.text for c in result_elem
                         if (c.tag.split("}")[-1] if "}" in c.tag else c.tag) == "LocationID"), None
                    )
                    for sub in child:
                        sub_tag = sub.tag.split('}')[-1] if '}' in sub.tag else sub.tag
                        # Handle nested elements (e.g. IntensityByReturnPeriod)
                        if len(sub) > 0:
                            for nested in sub:
                                nested_tag = nested.tag.split('}')[-1] if '}' in nested.tag else nested.tag
                                cat_record[f"{sub_tag}_{nested_tag}"] = nested.text
                        else:
                            cat_record[sub_tag] = sub.text
                    if cat_record:
                        categories[child_tag].append(cat_record)

            if loc_record:
                locations.append(loc_record)

        # Get paging info
        page_info = {}
        for elem in root.iter():
            t = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            if t in ('PageCount', 'PageNumber', 'PageSize', 'TotalRecordCount'):
                page_info[t] = int(elem.text or 0)

        return categories, locations, page_info

    def _soap_page(page_number, page_size=100):
        """Builds SOAP request for a specific page"""
        return f"""<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
        xmlns:a="http://www.w3.org/2005/08/addressing">
  <s:Header>
    <a:Action s:mustUnderstand="1">AIR.Services.HazardAnalysisService.Api/IHazardAnalysisService/GetHazardAnalysisResults</a:Action>
    <a:MessageID>urn:uuid:f23aa50c-9a41-4932-bd0e-51a37913fde1</a:MessageID>
    <a:ReplyTo><a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address></a:ReplyTo>
    <a:To s:mustUnderstand="1">https://crcins-na-prod-touchstoneapi.air-worldwide.com/FEP/AirServiceFacade.svc</a:To>
  </s:Header>
  <s:Body>
    <GetHazardAnalysisResults xmlns="AIR.Services.HazardAnalysisService.Api">
      <request xmlns:b="AIR.Services.HazardAnalysis.Api"
               xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
        <BusinessUnitSid xmlns="AIR.Services.Common.Api">{BUSINESS_UNIT_SID}</BusinessUnitSid>
        <LicenseUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</LicenseUid>
        <RequestUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</RequestUid>
        <SqlInstanceSid xmlns="AIR.Services.Common.Api">{SQL_INSTANCE_SID}</SqlInstanceSid>
        <b:AnalysisSid>{analysis_sid}</b:AnalysisSid>
        <b:PageNumber>{page_number}</b:PageNumber>
        <b:PageSize>{page_size}</b:PageSize>
      </request>
    </GetHazardAnalysisResults>
  </s:Body>
</s:Envelope>"""

    try:
        all_categories = {cat: [] for cat in CATEGORY_TAGS}
        all_locations  = []

        # Fetch page 1 first to get total page count
        print(f"    Fetching HAZ page 1...")
        r = send_soap_request(_soap_page(1))
        if r.status_code != 200:
            print(f"    ✗ HAZ fetch failed — status {r.status_code}")
            return {}

        cats, locs, page_info = _parse_page(r.text)
        for k in CATEGORY_TAGS:
            all_categories[k].extend(cats.get(k, []))
        all_locations.extend(locs)

        total_pages = page_info.get('PageCount', 1)
        total_recs  = page_info.get('TotalRecordCount', 0)
        print(f"    Pages: {total_pages}  |  Total records: {total_recs:,}")

        # Fetch remaining pages
        for page in range(2, total_pages + 1):
            print(f"    Fetching HAZ page {page}/{total_pages}...")
            r = send_soap_request(_soap_page(page))
            if r.status_code != 200:
                print(f"    ✗ Page {page} failed")
                continue
            cats, locs, _ = _parse_page(r.text)
            for k in CATEGORY_TAGS:
                all_categories[k].extend(cats.get(k, []))
            all_locations.extend(locs)

        # Build result dict — only include non-empty categories
        results = {}
        if all_locations:
            results['Location Info'] = pd.DataFrame(all_locations)
        for cat, records in all_categories.items():
            if records:
                results[cat] = pd.DataFrame(records)

        print(f"    ✓ HAZ categories returned: {list(results.keys())}")
        return results

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