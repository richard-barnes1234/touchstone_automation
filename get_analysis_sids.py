# get_analysis_sids.py — Fetches all projects and their completed analysis SIDs

import urllib3
import xml.etree.ElementTree as ET
import pandas as pd
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from api_client import send_soap_request
from config import BUSINESS_UNIT_SID, SQL_INSTANCE_SID
from soap_templates import get_projects, get_detailed_loss_analyses, get_hazard_analyses

# ─── STEP 1: GET ALL PROJECTS ─────────────────────────────
def get_all_projects():
    soap_body = get_projects(BUSINESS_UNIT_SID, SQL_INSTANCE_SID)
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
    soap_body = get_detailed_loss_analyses(BUSINESS_UNIT_SID, SQL_INSTANCE_SID, project_sid)
    response  = send_soap_request(soap_body)
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
                    'Completed'    : analysis.get('Completed'),
                })

    return analyses


# ─── STEP 3: GET HAZARD ANALYSES FOR A PROJECT ────────────
def get_hazard_analyses_for_project(project_sid, project_name):
    soap_body = get_hazard_analyses(BUSINESS_UNIT_SID, SQL_INSTANCE_SID, project_sid)
    response  = send_soap_request(soap_body)
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