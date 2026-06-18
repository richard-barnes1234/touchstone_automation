@echo off
REM set_env.bat
REM Run this in cmd.exe (NOT PowerShell) before starting the server:
REM   set_env.bat
REM Then in the SAME window run:
REM   python server.py

set APP_ENV=dev

set TOUCHSTONE_URL=https://crcins-na-prod-touchstoneapi.air-worldwide.com/FEP/AirServiceFacade.svc
set TOUCHSTONE_DOMAIN=crcins.air
set TOUCHSTONE_SQL_INSTANCE_SID=1
set TOUCHSTONE_BUSINESS_UNIT_SID=1
set TOUCHSTONE_DATA_SOURCE_SID=2

set TOUCHSTONE_DEV_USERNAME=automation-dev
set TOUCHSTONE_DEV_PASSWORD=wiT^&qBr2rfY@V4Ey

set TOUCHSTONE_UAT_USERNAME=automationservice
set TOUCHSTONE_UAT_PASSWORD=tBaecj*6Iep$N3^C
set TOUCHSTONE_PROD_USERNAME=automation-prod
set TOUCHSTONE_PROD_PASSWORD=jnsAowoM1ws!qYUt

echo Environment variables set for APP_ENV=%APP_ENV%