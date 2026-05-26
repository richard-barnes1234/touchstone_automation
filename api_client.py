import requests
from requests_ntlm import HttpNtlmAuth
from config import TOUCHSTONE_URL, USERNAME, PASSWORD, DOMAIN


def get_auth():
    """
    Returns an NTLM authentication object for use with requests.
    """
    return HttpNtlmAuth(f"{DOMAIN}\\{USERNAME}", PASSWORD)


def send_soap_request(soap_body):
    """
    Sends a SOAP request and returns the response.
    """
    headers = {"Content-Type": "application/soap+xml; charset=utf-8"}
    auth = get_auth()
    response = requests.post(
        TOUCHSTONE_URL,
        data=soap_body,
        headers=headers,
        auth=auth,
        verify=False,  # Disable SSL verification for corporate network
    )
    return response
