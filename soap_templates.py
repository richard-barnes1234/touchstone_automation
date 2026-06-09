TOUCHSTONE_URL = "https://crcins-na-prod-touchstoneapi.air-worldwide.com/FEP/AirServiceFacade.svc"


def get_exposure_sets(business_unit_sid, sql_instance_sid, data_source_sid):
    return f"""<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" 
                    xmlns:a="http://www.w3.org/2005/08/addressing">
<s:Header>
      <a:Action s:mustUnderstand="1">AIR.Services.DataSourceManagementService.Api/IDataSourceManagementService/GetExposureSets</a:Action>
      <a:MessageID>urn:uuid:f23aa50c-9a41-4932-bd0e-51a37913fde1</a:MessageID>
      <a:ReplyTo><a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address></a:ReplyTo>
      <a:To s:mustUnderstand="1">{TOUCHSTONE_URL}</a:To>
</s:Header>

<s:Body>
      <GetExposureSets xmlns="AIR.Services.DataSourceManagementService.Api">
        <request xmlns:b="AIR.Services.DataSourceManagement.Api" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
            <BusinessUnitSid xmlns="AIR.Services.Common.Api">{business_unit_sid}</BusinessUnitSid>
            <LicenseUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</LicenseUid>
            <RequestUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</RequestUid>
            <SqlInstanceSid xmlns="AIR.Services.Common.Api">{sql_instance_sid}</SqlInstanceSid>
            <b:DataSourceSid>{data_source_sid}</b:DataSourceSid>
         </request>
    </GetExposureSets>
   </s:Body>
</s:Envelope>"""


def get_detailed_loss_analyses(business_unit_sid, sql_instance_sid):
    """Fetches all available loss analyses from Touchstone"""
    return f"""<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
        xmlns:a="http://www.w3.org/2005/08/addressing">
  <s:Header>
    <a:Action s:mustUnderstand="1">AIR.Services.LossAnalysisService.Api/ILossAnalysisService/GetDetailedLossAnalyses</a:Action>
    <a:MessageID>urn:uuid:a1b2c3d4-e5f6-7890-abcd-ef1234567890</a:MessageID>
    <a:ReplyTo><a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address></a:ReplyTo>
    <a:To s:mustUnderstand="1">{TOUCHSTONE_URL}</a:To>
  </s:Header>
  <s:Body>
    <GetDetailedLossAnalyses xmlns="AIR.Services.LossAnalysisService.Api">
      <request xmlns:b="AIR.Services.LossAnalysis.Api"
               xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
        <BusinessUnitSid xmlns="AIR.Services.Common.Api">{business_unit_sid}</BusinessUnitSid>
        <LicenseUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</LicenseUid>
        <RequestUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</RequestUid>
        <SqlInstanceSid xmlns="AIR.Services.Common.Api">{sql_instance_sid}</SqlInstanceSid>
      </request>
    </GetDetailedLossAnalyses>
  </s:Body>
</s:Envelope>"""


def get_loss_analysis_event_results(business_unit_sid, sql_instance_sid, analysis_sid):
    return f"""<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" 
                    xmlns:a="http://www.w3.org/2005/08/addressing">
<s:Header>
      <a:Action s:mustUnderstand="1">AIR.Services.LossAnalysisService.Api/ILossAnalysisService/GetLossAnalysisEventResults</a:Action>
      <a:MessageID>urn:uuid:f23aa50c-9a41-4932-bd0e-51a37913fde1</a:MessageID>
      <a:ReplyTo><a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address></a:ReplyTo>
      <a:To s:mustUnderstand="1">{TOUCHSTONE_URL}</a:To>
</s:Header>

<s:Body>
      <GetLossAnalysisEventResults xmlns="AIR.Services.LossAnalysisService.Api">
        <request xmlns:b="AIR.Services.LossAnalysis.Api" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
            <BusinessUnitSid xmlns="AIR.Services.Common.Api">{business_unit_sid}</BusinessUnitSid>
            <LicenseUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</LicenseUid>
            <RequestUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</RequestUid>
            <SqlInstanceSid xmlns="AIR.Services.Common.Api">{sql_instance_sid}</SqlInstanceSid>
            <b:AnalysisSid>{analysis_sid}</b:AnalysisSid>
         </request>
    </GetLossAnalysisEventResults>
   </s:Body>
</s:Envelope>"""

def get_loss_analysis_annual_results(business_unit_sid, sql_instance_sid, analysis_sid):
    return f"""
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
    xmlns:a="http://www.w3.org/2005/08/addressing">
    <s:Header>
        <a:Action s:mustUnderstand="1">
            AIR.Services.LossAnalysisService.Api/ILossAnalysisService/GetLossAnalysisAnnualResults</a:Action>
        <a:MessageID>urn:uuid:f23aa50c-9a41-4932-bd0e-51a37913fde1</a:MessageID>
        <a:ReplyTo>
            <a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address>
        </a:ReplyTo>
        <a:To s:mustUnderstand="1">{TOUCHSTONE_URL}</a:To>
    </s:Header>
    <s:Body>
        <GetLossAnalysisAnnualResults xmlns="AIR.Services.LossAnalysisService.Api">
            <request xmlns:b="AIR.Services.LossAnalysis.Api"
                xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
                <BusinessUnitSid xmlns="AIR.Services.Common.Api">{business_unit_sid}</BusinessUnitSid>
                <LicenseUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</LicenseUid>
                <RequestUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</RequestUid>
                <SqlInstanceSid xmlns="AIR.Services.Common.Api">{sql_instance_sid}</SqlInstanceSid>
                <b:AnalysisSid>{analysis_sid}</b:AnalysisSid>
                <b:AnnualTypeFilter>Aggregate</b:AnnualTypeFilter>
                <b:PerspectiveFilter>GroundUp</b:PerspectiveFilter>
            </request>
        </GetLossAnalysisAnnualResults>
    </s:Body>
</s:Envelope>"""

def get_loss_analysis_summary_results(business_unit_sid, sql_instance_sid, analysis_sid):
    return f"""<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" 
                    xmlns:a="http://www.w3.org/2005/08/addressing">
 <s:Header>
       <a:Action s:mustUnderstand="1">AIR.Services.LossAnalysisService.Api/ILossAnalysisService/GetLossAnalysisSummaryResults</a:Action>
       <a:MessageID>urn:uuid:f23aa50c-9a41-4932-bd0e-51a37913fde1</a:MessageID>
       <a:ReplyTo><a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address></a:ReplyTo>
       <a:To s:mustUnderstand="1">{TOUCHSTONE_URL}</a:To>
 </s:Header>

  <s:Body>
        <GetLossAnalysisSummaryResults xmlns="AIR.Services.LossAnalysisService.Api">
            <request xmlns:b="AIR.Services.LossAnalysis.Api" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
                <BusinessUnitSid xmlns="AIR.Services.Common.Api">{business_unit_sid}</BusinessUnitSid>
                <LicenseUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</LicenseUid>
                <RequestUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</RequestUid>
                <SqlInstanceSid xmlns="AIR.Services.Common.Api">{sql_instance_sid}</SqlInstanceSid>
                <b:AnalysisSid>{analysis_sid}</b:AnalysisSid>
            </request>
        </GetLossAnalysisSummaryResults>
  </s:Body>
</s:Envelope>"""


def get_projects(business_unit_sid, sql_instance_sid):
    """Fetches all projects from Touchstone"""
    return f"""<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
        xmlns:a="http://www.w3.org/2005/08/addressing">
  <s:Header>
    <a:Action s:mustUnderstand="1">AIR.Services.ProjectManagementService.Api/IProjectManagementService/GetProjects</a:Action>
    <a:MessageID>urn:uuid:f23aa50c-9a41-4932-bd0e-51a37913fde1</a:MessageID>
    <a:ReplyTo><a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address></a:ReplyTo>
    <a:To s:mustUnderstand="1">{TOUCHSTONE_URL}</a:To>
  </s:Header>
  <s:Body>
    <GetProjects xmlns="AIR.Services.ProjectManagementService.Api">
      <request xmlns:b="AIR.Services.ProjectManagement.Api"
               xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
        <BusinessUnitSid xmlns="AIR.Services.Common.Api">{business_unit_sid}</BusinessUnitSid>
        <LicenseUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</LicenseUid>
        <RequestUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</RequestUid>
        <SqlInstanceSid xmlns="AIR.Services.Common.Api">{sql_instance_sid}</SqlInstanceSid>
      </request>
    </GetProjects>
  </s:Body>
</s:Envelope>"""


def get_detailed_loss_analyses(business_unit_sid, sql_instance_sid, project_sid):
    """Fetches all loss analyses for a given project"""
    return f"""<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
        xmlns:a="http://www.w3.org/2005/08/addressing">
  <s:Header>
    <a:Action s:mustUnderstand="1">AIR.Services.LossAnalysisService.Api/ILossAnalysisService/GetDetailedLossAnalyses</a:Action>
    <a:MessageID>urn:uuid:f23aa50c-9a41-4932-bd0e-51a37913fde1</a:MessageID>
    <a:ReplyTo><a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address></a:ReplyTo>
    <a:To s:mustUnderstand="1">{TOUCHSTONE_URL}</a:To>
  </s:Header>
  <s:Body>
    <GetDetailedLossAnalyses xmlns="AIR.Services.LossAnalysisService.Api">
      <request xmlns:b="AIR.Services.LossAnalysis.Api"
               xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
        <BusinessUnitSid xmlns="AIR.Services.Common.Api">{business_unit_sid}</BusinessUnitSid>
        <LicenseUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</LicenseUid>
        <RequestUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</RequestUid>
        <SqlInstanceSid xmlns="AIR.Services.Common.Api">{sql_instance_sid}</SqlInstanceSid>
        <b:ProjectSid>{project_sid}</b:ProjectSid>
      </request>
    </GetDetailedLossAnalyses>
  </s:Body>
</s:Envelope>"""


def get_hazard_analysis_results(business_unit_sid, sql_instance_sid, analysis_sid):
    """Fetches hazard analysis results for a given HazardAnalysisSid"""
    return f"""<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
        xmlns:a="http://www.w3.org/2005/08/addressing">
  <s:Header>
    <a:Action s:mustUnderstand="1">AIR.Services.HazardAnalysisService.Api/IHazardAnalysisService/GetHazardAnalysisResults</a:Action>
    <a:MessageID>urn:uuid:f23aa50c-9a41-4932-bd0e-51a37913fde1</a:MessageID>
    <a:ReplyTo><a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address></a:ReplyTo>
    <a:To s:mustUnderstand="1">{TOUCHSTONE_URL}</a:To>
  </s:Header>
  <s:Body>
    <GetHazardAnalysisResults xmlns="AIR.Services.HazardAnalysisService.Api">
      <request xmlns:b="AIR.Services.HazardAnalysis.Api"
               xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
        <BusinessUnitSid xmlns="AIR.Services.Common.Api">{business_unit_sid}</BusinessUnitSid>
        <LicenseUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</LicenseUid>
        <RequestUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</RequestUid>
        <SqlInstanceSid xmlns="AIR.Services.Common.Api">{sql_instance_sid}</SqlInstanceSid>
        <b:AnalysisSid>{analysis_sid}</b:AnalysisSid>
      </request>
    </GetHazardAnalysisResults>
  </s:Body>
</s:Envelope>"""


def get_hazard_analyses(business_unit_sid, sql_instance_sid, project_sid):
    """Fetches all hazard analyses for a given project"""
    return f"""<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
        xmlns:a="http://www.w3.org/2005/08/addressing">
  <s:Header>
    <a:Action s:mustUnderstand="1">AIR.Services.HazardAnalysisService.Api/IHazardAnalysisService/GetHazardAnalyses</a:Action>
    <a:MessageID>urn:uuid:f23aa50c-9a41-4932-bd0e-51a37913fde1</a:MessageID>
    <a:ReplyTo><a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address></a:ReplyTo>
    <a:To s:mustUnderstand="1">{TOUCHSTONE_URL}</a:To>
  </s:Header>
  <s:Body>
    <GetHazardAnalyses xmlns="AIR.Services.HazardAnalysisService.Api">
      <request xmlns:b="AIR.Services.HazardAnalysis.Api"
               xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
        <BusinessUnitSid xmlns="AIR.Services.Common.Api">{business_unit_sid}</BusinessUnitSid>
        <LicenseUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</LicenseUid>
        <RequestUid xmlns="AIR.Services.Common.Api">00000000-0000-0000-0000-000000000000</RequestUid>
        <SqlInstanceSid xmlns="AIR.Services.Common.Api">{sql_instance_sid}</SqlInstanceSid>
        <b:ProjectSid>{project_sid}</b:ProjectSid>
      </request>
    </GetHazardAnalyses>
  </s:Body>
</s:Envelope>"""