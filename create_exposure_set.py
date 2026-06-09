# create_exposure_set.py — Creates a new Exposure Set in Touchstone

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from api_client import send_soap_request
from config import BUSINESS_UNIT_SID, SQL_INSTANCE_SID, DATA_SOURCE_SID

def create_exposure_set(name, description=""):
    """Creates a new Exposure Set in Touchstone and returns its SID"""

    print(f"\nCreating Exposure Set: {name}")

    soap_body = f"""<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
            xmlns:a="http://www.w3.org/2005/08/addressing">
   <s:Header>
      <a:Action s:mustUnderstand="1">AIR.Services.DataSourceManagementService.Api/IDataSourceManagementService/CreateExposureSet</a:Action>
      <a:MessageID>urn:uuid:f23aa50c-9a41-4932-bd0e-51a37913fde1</a:MessageID>
      <a:ReplyTo><a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address></a:ReplyTo>
      <a:To s:mustUnderstand="1">https://crcins-na-prod-touchstoneapi.air-worldwide.com/FEP/AirServiceFacade.svc</a:To>
   </s:Header>
   <s:Body>
      <CreateExposureSet xmlns="AIR.Services.DataSourceManagementService.Api">
         <request xmlns:b="AIR.Services.DataSourceManagement.Api"
                  xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
            <BusinessUnitSid xmlns="AIR.Services.Common.Api">{BUSINESS_UNIT_SID}</BusinessUnitSid>
            <LicenseUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</LicenseUid>
            <RequestUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</RequestUid>
            <SqlInstanceSid xmlns="AIR.Services.Common.Api">{SQL_INSTANCE_SID}</SqlInstanceSid>
            <b:DataSourceSid>{DATA_SOURCE_SID}</b:DataSourceSid>
            <b:Name>{name}</b:Name>
            <b:Description>{description}</b:Description>
         </request>
      </CreateExposureSet>
   </s:Body>
</s:Envelope>"""

    response = send_soap_request(soap_body)
    print(f"  Status Code: {response.status_code}")

    if response.status_code == 200:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.text)
        # Find the ExposureSet SID in response
        for elem in root.iter():
            if elem.tag.endswith('}Sid') or elem.tag == 'Sid':
                sid = elem.text
                if sid and sid != '0':
                    print(f"  ✓ Exposure Set created — SID: {sid}")
                    return sid
    else:
        print(f"  ✗ Failed to create Exposure Set")
        print(response.text[:500])
        return None

if __name__ == "__main__":
    # Test — only run when sandbox is confirmed
    # create_exposure_set("Test_Automation_01", "Created by automation pipeline")
    print("CreateExposureSet ready — awaiting sandbox confirmation to run")