# test_connection.py  Tests API connectivity

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from api_client import send_soap_request
from config import BUSINESS_UNIT_SID, SQL_INSTANCE_SID

soap_body = f"""<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" 
            xmlns:a="http://www.w3.org/2005/08/addressing">
      <s:Header>
            <a:Action s:mustUnderstand="1">AIR.Services.SecurityService.Api/ISecurityService/GetBusinessUnits</a:Action>
            <a:MessageID>urn:uuid:12345678-1234-1234-1234-123456789012</a:MessageID>
            <a:ReplyTo>
                  <a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address>
            </a:ReplyTo>
            <a:To s:mustUnderstand="1">https://crcins-na-prod-touchstoneapi.air-worldwide.com/FEP/AirServiceFacade.svc</a:To>
      </s:Header>
      <s:Body>
            <GetBusinessUnit xmlns="AIR.Services.SecurityService.Api">
          <request xmlns:b="AIR.Services.Common.Api" 
                  xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
            <b:LicenseUid>00000000-0000-0000-0000-000000000000</b:LicenseUid>
            <b:RequestUid>00000000-0000-0000-0000-000000000000</b:RequestUid>
          </request>
            </GetBusinessUnit>
      </s:Body>
</s:Envelope>"""  

print("Testing API connectivity...")
response = send_soap_request(soap_body)
print(f"Response status code: {response.status_code}")

if response.status_code == 200:
    print("Connection successful.") 
    from parse_response import parse_xml
    parse_xml(response.text)  # Parse and print the XML response

else:
    print("X Connection Failed!")
    print(response.text)
