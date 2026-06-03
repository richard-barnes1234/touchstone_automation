# test_raw_fields.py
# Prints the raw XML fields returned by GetDetailedLossAnalyses

import urllib3
import xml.etree.ElementTree as ET
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from api_client import send_soap_request
from config import BUSINESS_UNIT_SID, SQL_INSTANCE_SID

soap_body = f"""<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
        xmlns:a="http://www.w3.org/2005/08/addressing">
   <s:Header>
      <a:Action s:mustUnderstand="1">AIR.Services.LossAnalysisService.Api/ILossAnalysisService/GetDetailedLossAnalyses</a:Action>
      <a:MessageID>urn:uuid:f23aa50c-9a41-4932-bd0e-51a37913fde1</a:MessageID>
      <a:ReplyTo><a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address></a:ReplyTo>
      <a:To s:mustUnderstand="1">https://crcins-na-prod-touchstoneapi.air-worldwide.com/FEP/AirServiceFacade.svc</a:To>
   </s:Header>
   <s:Body>
      <GetDetailedLossAnalyses xmlns="AIR.Services.LossAnalysisService.Api">
         <request xmlns:b="AIR.Services.LossAnalysis.Api"
                  xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
            <BusinessUnitSid xmlns="AIR.Services.Common.Api">{BUSINESS_UNIT_SID}</BusinessUnitSid>
            <LicenseUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</LicenseUid>
            <RequestUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</RequestUid>
            <SqlInstanceSid xmlns="AIR.Services.Common.Api">{SQL_INSTANCE_SID}</SqlInstanceSid>
            <b:ProjectSid>16726</b:ProjectSid>
         </request>
      </GetDetailedLossAnalyses>
   </s:Body>
</s:Envelope>"""

response = send_soap_request(soap_body)
root = ET.fromstring(response.text)

# Find first DetailedLossAnalysis and print ALL its child tags and values
for elem in root.iter():
    if elem.tag.endswith('}DetailedLossAnalysis'):
        print("RAW FIELDS FROM API:")
        print("-" * 40)
        for child in elem:
            tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            print(f"  {tag}: {child.text}")
        break  # first one only