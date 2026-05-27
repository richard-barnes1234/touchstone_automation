# submit_import_csv.py — Uploads SOV CSV to Touchstone

import urllib3
import pandas as pd
import base64
import xml.etree.ElementTree as ET
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from api_client import send_soap_request
from config import BUSINESS_UNIT_SID, SQL_INSTANCE_SID, DATA_SOURCE_SID

def parse_import_response(response_text):
    """Parses import response and extracts activity SID or errors"""
    root = ET.fromstring(response_text)
    result = {"success": False, "activity_sid": None, "errors": []}

    for elem in root.iter():
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag

        if tag == 'ActivitySid' and elem.text:
            result["activity_sid"] = elem.text

        if tag == 'Code' and elem.text:
            if elem.text == 'Success':
                result["success"] = True

        if tag == 'Message' and elem.text:
            if elem.text and len(elem.text) > 2:
                result["errors"].append(elem.text)

    return result

def submit_import_csv(sov_filepath, exposure_set_sid):
    """Submits a SOV CSV file to Touchstone for import"""

    print(f"\nSubmitting SOV import...")
    print(f"  File          : {sov_filepath}")
    print(f"  ExposureSetSid: {exposure_set_sid}")

    # Read and encode CSV as base64
    with open(sov_filepath, "rb") as f:
        csv_data = base64.b64encode(f.read()).decode("utf-8")

    soap_body = f"""<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
            xmlns:a="http://www.w3.org/2005/08/addressing">
   <s:Header>
      <a:Action s:mustUnderstand="1">AIR.Services.DataImportService.Api/IDataImportService/SubmitImportCsv</a:Action>
      <a:MessageID>urn:uuid:fc3d6b69-b7a9-474a-ab36-41e116a2a6d7</a:MessageID>
      <a:ReplyTo><a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address></a:ReplyTo>
      <a:To s:mustUnderstand="1">https://crcins-na-prod-touchstoneapi.air-worldwide.com/FEP/AirServiceFacade.svc</a:To>
   </s:Header>
   <s:Body>
      <SubmitImportCsv xmlns="AIR.Services.DataImportService.Api">
         <request xmlns:b="AIR.Services.DataImport.Api"
                  xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
            <BusinessUnitSid xmlns="AIR.Services.Common.Api">{BUSINESS_UNIT_SID}</BusinessUnitSid>
            <LicenseUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</LicenseUid>
            <RequestUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</RequestUid>
            <SqlInstanceSid xmlns="AIR.Services.Common.Api">{SQL_INSTANCE_SID}</SqlInstanceSid>
            <b:Currency>USD</b:Currency>
            <b:GeocoderType>AIRGeocoder</b:GeocoderType>
            <b:Priority>Normal</b:Priority>
            <b:DataSourceSid>{DATA_SOURCE_SID}</b:DataSourceSid>
            <b:DateFormat>MM/DD/YYYY</b:DateFormat>
            <b:ImportType>Replace</b:ImportType>
            <b:ExposureSetSid>{exposure_set_sid}</b:ExposureSetSid>
            <b:CsvData>{csv_data}</b:CsvData>
         </request>
      </SubmitImportCsv>
   </s:Body>
</s:Envelope>"""

    response = send_soap_request(soap_body)
    print(f"  Status Code: {response.status_code}")

    if response.status_code == 200:
        result = parse_import_response(response.text)

        if result["success"]:
            print(f"  ✓ Import submitted — Activity SID: {result['activity_sid']}")
            return result["activity_sid"]
        else:
            print(f"  ✗ Import rejected by API")
            print(f"\n  Errors from API:")
            for err in result["errors"]:
                print(f"    — {err}")
            return None
    else:
        print(f"  ✗ Request failed: {response.status_code}")
        print(response.text[:500])
        return None

if __name__ == "__main__":
    # Test — only run when sandbox is confirmed
    # submit_import_csv("sample_sov.csv", "12345")
    print("SubmitImportCsv ready — awaiting sandbox confirmation to run")