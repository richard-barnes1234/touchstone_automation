$env:APP_ENV 

$env:TOUCHSTONE_URL = "https://crcins-na-prod-touchstoneapi.air-worldwide.com/FRP/AirServiceFacade.svc"
$env:TOUCHSTONE_DOMAIN = "crcins.air"
$env:TOUCHSTONE_SQL_INSTANCE_SID = "1"
$env:TOUCHSTONE_BUSINESS_UNIT_SID = "1"
$env:TOUCHSTONE_DATA_SOURCE_SID = "2"

$env:TOUCHTONE_DEV_USERNAME  = "automation-dev"
$env:TOUCHSTONE_DEV_PASSWORD = "wiT&qBr2rfY@V4Ey"

$env:TOUCHSTONE_UAT_USERNAME = "automationservice"
$env:TTONE_UAT_PASSWORD      = "tBaecj*6Iep$N3^C"

$env:TOUCHSTONE_PROD_USERNAME = "automation-prod"
$env:TOUCHSTONE_PROD_PASSWORD = "jnsAowoM1ws!qYUt"

Write-Host "Environment variables set for APP_ENV=$env:app-env" -ForegroundColor Green