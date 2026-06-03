# get_analysis_sids.py — Fetches all projects and their completed analysis SIDs

import urllib3
import xml.etree.ElementTree as ET
import pandas as pd
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from api_client import send_soap_request
from config import BUSINESS_UNIT_SID, SQL_INSTANCE_SID

# ─── STEP 1: GET ALL PROJECTS ─────────────────────────────
def get_all_projects():
    soap_body = f"""<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
            xmlns:a="http://www.w3.org/2005/08/addressing">
   <s:Header>
      <a:Action s:mustUnderstand="1">AIR.Services.ProjectManagementService.Api/IProjectManagementService/GetProjects</a:Action>
      <a:MessageID>urn:uuid:f23aa50c-9a41-4932-bd0e-51a37913fde1</a:MessageID>
      <a:ReplyTo><a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address></a:ReplyTo>
      <a:To s:mustUnderstand="1">https://crcins-na-prod-touchstoneapi.air-worldwide.com/FEP/AirServiceFacade.svc</a:To>
   </s:Header>
   <s:Body>
      <GetProjects xmlns="AIR.Services.ProjectManagementService.Api">
         <request xmlns:b="AIR.Services.ProjectManagement.Api"
                  xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
            <BusinessUnitSid xmlns="AIR.Services.Common.Api">{BUSINESS_UNIT_SID}</BusinessUnitSid>
            <LicenseUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</LicenseUid>
            <RequestUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</RequestUid>
            <SqlInstanceSid xmlns="AIR.Services.Common.Api">{SQL_INSTANCE_SID}</SqlInstanceSid>
         </request>
      </GetProjects>
   </s:Body>
</s:Envelope>"""

    print("Fetching all projects...")
    response = send_soap_request(soap_body)

    if response.status_code != 200:
        print(f"  X Failed: {response.status_code}")
        return []

    root = ET.fromstring(response.text)
    projects = []

    for elem in root.iter():
        if elem.tag.endswith('}Project'):
            project = {}
            for child in elem:
                tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                project[tag] = child.text
            if project.get('Sid'):
                projects.append({
                    'ProjectSid'  : project.get('Sid'),
                    'ProjectName' : project.get('Name'),
                    'ResultCount' : project.get('ResultSetCount', 0),
                    'StateCode'   : project.get('StateCode')
                })

    print(f"  + {len(projects)} projects found")
    return projects


# ─── STEP 2: GET LOSS ANALYSES FOR A PROJECT ──────────────
def get_analyses_for_project(project_sid, project_name):
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
            <b:ProjectSid>{project_sid}</b:ProjectSid>
         </request>
      </GetDetailedLossAnalyses>
   </s:Body>
</s:Envelope>"""

    response = send_soap_request(soap_body)
    if response.status_code != 200:
        return []

    root = ET.fromstring(response.text)
    analyses = []

    for elem in root.iter():
        if elem.tag.endswith('}DetailedLossAnalysis'):
            analysis = {}
            for child in elem:
                tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                analysis[tag] = child.text

            status = analysis.get('ActivityStatusCode', '')
            sid    = analysis.get('Sid', '')
            name   = analysis.get('Name', '')

            if status == 'Completed' and sid:
                analyses.append({
                    'ProjectSid'   : project_sid,
                    'ProjectName'  : project_name,
                    'AnalysisSid'  : sid,
                    'AnalysisName' : name,
                    'AnalysisType' : 'LOSS',
                    'Status'       : status,
                    'Completed'    : analysis.get('Completed')
                })

    return analyses


# ─── STEP 3: GET HAZARD ANALYSES FOR A PROJECT ────────────
def get_hazard_analyses_for_project(project_sid, project_name):
    soap_body = f"""<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
            xmlns:a="http://www.w3.org/2005/08/addressing">
   <s:Header>
      <a:Action s:mustUnderstand="1">AIR.Services.HazardAnalysisService.Api/IHazardAnalysisService/GetHazardAnalyses</a:Action>
      <a:MessageID>urn:uuid:f23aa50c-9a41-4932-bd0e-51a37913fde1</a:MessageID>
      <a:ReplyTo><a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address></a:ReplyTo>
      <a:To s:mustUnderstand="1">https://crcins-na-prod-touchstoneapi.air-worldwide.com/FEP/AirServiceFacade.svc</a:To>
   </s:Header>
   <s:Body>
      <GetHazardAnalyses xmlns="AIR.Services.HazardAnalysisService.Api">
         <request xmlns:b="AIR.Services.HazardAnalysis.Api"
                  xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
            <BusinessUnitSid xmlns="AIR.Services.Common.Api">{BUSINESS_UNIT_SID}</BusinessUnitSid>
            <LicenseUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</LicenseUid>
            <RequestUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</RequestUid>
            <SqlInstanceSid xmlns="AIR.Services.Common.Api">{SQL_INSTANCE_SID}</SqlInstanceSid>
            <b:ProjectSid>{project_sid}</b:ProjectSid>
         </request>
      </GetHazardAnalyses>
   </s:Body>
</s:Envelope>"""

    response = send_soap_request(soap_body)
    if response.status_code != 200:
        return []

    root = ET.fromstring(response.text)
    analyses = []

    for elem in root.iter():
        if elem.tag.endswith('}HazardAnalysis'):
            analysis = {}
            for child in elem:
                tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                analysis[tag] = child.text

            status = analysis.get('ActivityStatusCode', '')
            sid    = analysis.get('Sid', '')

            if sid:
                analyses.append({
                    'ProjectSid'   : project_sid,
                    'ProjectName'  : project_name,
                    'AnalysisSid'  : sid,
                    'AnalysisName' : f"HAZ-{sid}",
                    'AnalysisType' : 'HAZ',
                    'Status'       : status,
                    'Completed'    : analysis.get('Completed')
                })

    return analyses


# ─── STEP 4: GET ALL COMPLETED ANALYSES ───────────────────
def get_all_completed_analyses():
    print("\n" + "="*55)
    print("  FETCHING ALL COMPLETED ANALYSES")
    print("="*55)

    projects = get_all_projects()

    if not projects:
        print("  X No projects found")
        return pd.DataFrame()

    active_projects = [
        p for p in projects
        if p['StateCode'] == 'Active'
        and int(p['ResultCount'] or 0) > 0
    ]
    print(f"  Active projects with results: {len(active_projects)}")

    all_analyses = []
    for i, project in enumerate(active_projects, 1):
        print(f"  [{i}/{len(active_projects)}] {project['ProjectName']} (SID: {project['ProjectSid']})")

        # Loss analyses
        analyses = get_analyses_for_project(project['ProjectSid'], project['ProjectName'])
        print(f"    -> {len(analyses)} loss analyses (LOSS)")
        all_analyses.extend(analyses)

        # Hazard analyses
        haz_analyses = get_hazard_analyses_for_project(project['ProjectSid'], project['ProjectName'])
        print(f"    -> {len(haz_analyses)} hazard analyses (HAZ)")
        all_analyses.extend(haz_analyses)

    df = pd.DataFrame(all_analyses)
    print(f"\n  + Total analyses found: {len(df)}")
    print("="*55)
    return df


if __name__ == "__main__":
    df = get_all_completed_analyses()
    if not df.empty:
        print(f"\n{df[['ProjectName','AnalysisSid','AnalysisName','AnalysisType','Completed']].to_string()}")
        df.to_csv("all_analyses.csv", index=False)
        print(f"\n+ Saved to all_analyses.csv")