# poll_activity.py — Polls GetActivity until a job completes

import urllib3
import time
import xml.etree.ElementTree as ET
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from api_client import send_soap_request
from config import BUSINESS_UNIT_SID, SQL_INSTANCE_SID

def get_activity_status(activity_sid):
    """Gets the current status of an activity"""

    soap_body = f"""<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
            xmlns:a="http://www.w3.org/2005/08/addressing">
   <s:Header>
      <a:Action s:mustUnderstand="1">AIR.Services.ActivityMonitorService.Api/IActivityManagementService/GetActivity</a:Action>
      <a:MessageID>urn:uuid:f23aa50c-9a41-4932-bd0e-51a37913fde1</a:MessageID>
      <a:ReplyTo><a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address></a:ReplyTo>
      <a:To s:mustUnderstand="1">https://crcins-na-prod-touchstoneapi.air-worldwide.com/FEP/AirServiceFacade.svc</a:To>
   </s:Header>
   <s:Body>
      <GetActivity xmlns="AIR.Services.ActivityMonitorService.Api">
         <request xmlns:b="AIR.Services.ActivityManagement.Api"
                  xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
            <BusinessUnitSid xmlns="AIR.Services.Common.Api">{BUSINESS_UNIT_SID}</BusinessUnitSid>
            <LicenseUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</LicenseUid>
            <RequestUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</RequestUid>
            <SqlInstanceSid xmlns="AIR.Services.Common.Api">{SQL_INSTANCE_SID}</SqlInstanceSid>
            <b:ActivitySid>{activity_sid}</b:ActivitySid>
         </request>
      </GetActivity>
   </s:Body>
</s:Envelope>"""

    response = send_soap_request(soap_body)

    if response.status_code == 200:
        root = ET.fromstring(response.text)
        for elem in root.iter():
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            if tag == 'StatusCode' and elem.text:
                return elem.text
    return "Unknown"

def poll_until_complete(activity_sid, interval=10, timeout=600):
    """Polls GetActivity every interval seconds until complete or timeout"""

    print(f"\n  Polling activity SID: {activity_sid}")
    print(f"  Checking every {interval} seconds (timeout: {timeout}s)")
    print(f"  {'─'*40}")

    elapsed = 0
    while elapsed < timeout:
        status = get_activity_status(activity_sid)
        print(f"  [{elapsed:>4}s] Status: {status}")

        if status in ["Completed", "Complete"]:
            print(f"\n  ✓ Job completed successfully!")
            return True
        elif status in ["Failed", "Error", "Cancelled"]:
            print(f"\n  ✗ Job failed with status: {status}")
            return False

        time.sleep(interval)
        elapsed += interval

    print(f"\n  ✗ Timeout reached after {timeout} seconds")
    return False

if __name__ == "__main__":
    # Test — only run when sandbox is confirmed
    # poll_until_complete("12345")
    print("PollActivity ready — awaiting sandbox confirmation to run")