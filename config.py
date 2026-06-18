# config.py
# ─────────────────────────────────────────────────────────────────────────────
# Multi-environment credential management.
# APP_ENV determines which Touchstone service account is used.
#
# Local development : APP_ENV=dev   → uses automation-dev
# Staging/validation : APP_ENV=uat  → uses automationservice (existing, repurposed)
# Production (Azure) : APP_ENV=prod → uses automation-prod
# ─────────────────────────────────────────────────────────────────────────────

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ── Determine environment ─────────────────────────────────────────────────────
APP_ENV = os.environ.get("APP_ENV", "dev").lower()  # dev | uat | prod

if APP_ENV not in ("dev", "uat", "prod"):
    raise EnvironmentError(f"Invalid APP_ENV '{APP_ENV}' — must be 'dev', 'uat', or 'prod'")


# ── Touchstone API base settings (same across environments) ──────────────────
TOUCHSTONE_URL = os.environ.get(
    "TOUCHSTONE_URL",
    "https://crcins-na-prod-touchstoneapi.air-worldwide.com/FEP/AirServiceFacade.svc"
)
DOMAIN = os.environ.get("TOUCHSTONE_DOMAIN", "crcins.air")

SQL_INSTANCE_SID  = int(os.environ.get("TOUCHSTONE_SQL_INSTANCE_SID", "1"))
BUSINESS_UNIT_SID = int(os.environ.get("TOUCHSTONE_BUSINESS_UNIT_SID", "1"))
DATA_SOURCE_SID   = int(os.environ.get("TOUCHSTONE_DATA_SOURCE_SID",  "2"))


# ── Environment-specific credentials ───────────────────────────────────────────
# Each environment reads its own USERNAME/PASSWORD pair from env vars.
# This keeps all three credential sets isolated — dev never touches prod creds.

_CREDENTIAL_MAP = {
    "dev":  {
        "username_var": "automationservice",
        "password_var": "wiT&qBr2rfY@V4Ey",
        "account_name": "automation-dev",
    },
    "uat":  {
        "username_var": "automationservice",
        "password_var": "tBaecj*6Iep$N3^C",
        "account_name": "automationservice",   # existing account repurposed
    },
    "prod": {
        "username_var": "automationservice",
        "password_var": "jnsAowoM1ws!qYUt",
        "account_name": "automation-prod",
    },
}

_creds = _CREDENTIAL_MAP[APP_ENV]
USERNAME     = os.environ.get(_creds["username_var"])
PASSWORD     = os.environ.get(_creds["password_var"])
ACCOUNT_NAME = _creds["account_name"]   # used in audit logs to identify which account made the call

# ── Validate ────────────────────────────────────────────────────────────────
_missing = [k for k, v in {
    _creds["username_var"]: USERNAME,
    _creds["password_var"]: PASSWORD,
}.items() if not v]

if _missing:
    raise EnvironmentError(
        f"APP_ENV='{APP_ENV}' requires these environment variables: {', '.join(_missing)}\n"
        f"Set them in .env (local) or Azure App Service settings (production)."
    )

print(f"  ✓ Touchstone config loaded — environment: {APP_ENV.upper()} | account: {ACCOUNT_NAME}")