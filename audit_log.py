# audit_log.py
# ─────────────────────────────────────────────────────────────────────────────
# Logs every Touchstone API call with: timestamp, environment, account used,
# operation called, target SID, status code, and duration.
#
# Writes to a rotating local file. In production this should also forward
# to Application Insights / Log Analytics (see send_to_app_insights below).
# ─────────────────────────────────────────────────────────────────────────────

import os
import json
import time
from datetime import datetime, timezone
from functools import wraps

from config import APP_ENV, ACCOUNT_NAME

LOG_DIR  = os.environ.get("AUDIT_LOG_DIR", "logs")
LOG_FILE = os.path.join(LOG_DIR, "touchstone_api_audit.log")

os.makedirs(LOG_DIR, exist_ok=True)


def _write_log(entry: dict):
    """Appends one JSON line to the audit log file."""
    line = json.dumps(entry, default=str)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    # Also print to console/stdout — Azure App Service captures this in Log Stream
    print(f"  [AUDIT] {line}")


def log_api_call(operation, target_sid=None, status_code=None, duration_ms=None, error=None, extra=None):
    """
    Logs a single Touchstone API call.

    operation    : e.g. 'GetProjects', 'GetDetailedLossAnalyses', 'GetLossAnalysisEventResults'
    target_sid   : ProjectSid or AnalysisSid being queried, if applicable
    status_code  : HTTP status returned
    duration_ms  : how long the call took
    error        : error message if the call failed
    extra        : any additional context (dict)
    """
    entry = {
        "timestamp":    datetime.now(timezone.utc).isoformat(),
        "environment":  APP_ENV,
        "account":      ACCOUNT_NAME,
        "operation":    operation,
        "target_sid":   target_sid,
        "status_code":  status_code,
        "duration_ms":  duration_ms,
        "success":      error is None and (status_code is None or status_code == 200),
        "error":        error,
    }
    if extra:
        entry.update(extra)
    _write_log(entry)
    return entry


def audited_call(operation_name):
    """
    Decorator — wraps any function that makes a Touchstone API call
    and automatically logs its execution, duration, and outcome.

    Usage:
        @audited_call("GetProjects")
        def get_all_projects():
            ...

        @audited_call("GetDetailedLossAnalyses")
        def get_analyses_for_project(project_sid, project_name):
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            start = time.time()
            target_sid = args[0] if args else kwargs.get("project_sid") or kwargs.get("analysis_sid")
            try:
                result = fn(*args, **kwargs)
                duration_ms = round((time.time() - start) * 1000, 1)
                log_api_call(
                    operation=operation_name,
                    target_sid=target_sid,
                    status_code=200,
                    duration_ms=duration_ms,
                )
                return result
            except Exception as e:
                duration_ms = round((time.time() - start) * 1000, 1)
                log_api_call(
                    operation=operation_name,
                    target_sid=target_sid,
                    status_code=getattr(e, "status_code", None),
                    duration_ms=duration_ms,
                    error=str(e),
                )
                raise
        return wrapper
    return decorator


def get_recent_logs(n=50):
    """Returns the last n audit log entries — useful for an admin dashboard view."""
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    entries = [json.loads(l) for l in lines[-n:] if l.strip()]
    return list(reversed(entries))  # most recent first


def get_usage_summary():
    """
    Returns aggregate stats — calls per environment, per operation,
    error rate. Useful for a monitoring panel.
    """
    if not os.path.exists(LOG_FILE):
        return {}
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        entries = [json.loads(l) for l in f if l.strip()]

    summary = {"total_calls": len(entries), "by_environment": {}, "by_operation": {}, "errors": 0}
    for e in entries:
        env = e.get("environment", "unknown")
        op  = e.get("operation", "unknown")
        summary["by_environment"][env] = summary["by_environment"].get(env, 0) + 1
        summary["by_operation"][op]    = summary["by_operation"].get(op, 0) + 1
        if not e.get("success", True):
            summary["errors"] += 1
    return summary


if __name__ == "__main__":
    # Quick test
    log_api_call("GetProjects", status_code=200, duration_ms=842.3)
    log_api_call("GetDetailedLossAnalyses", target_sid="19731", status_code=200, duration_ms=312.1)
    log_api_call("GetLossAnalysisEventResults", target_sid="137230", status_code=500, error="Timeout")

    print("\nRecent logs:")
    for entry in get_recent_logs(5):
        print(f"  {entry['timestamp']} | {entry['environment']} | {entry['account']} | {entry['operation']} | {entry['status_code']}")

    print("\nUsage summary:")
    print(json.dumps(get_usage_summary(), indent=2))