# db_client.py — SQL Server connection and query engine for AIRResult
# ─────────────────────────────────────────────────────────────────────────────
# Connects to P19TS1DB01\PRIMARYSQL2019 using Windows Authentication.
# All queries are read-only. No data is modified.
# ─────────────────────────────────────────────────────────────────────────────

import pyodbc
import pandas as pd

SERVER   = "P19TS1DB01\\PRIMARYSQL2019"
DATABASE = "AIRResult"

# ── Connection ────────────────────────────────────────────────────────────────

def get_connection():
    """Returns a pyodbc connection using Windows Authentication"""
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"Trusted_Connection=yes;"
    )
    return pyodbc.connect(conn_str, timeout=30)


# ── Fetch available Result SIDs ───────────────────────────────────────────────

def get_available_result_sids():
    """
    Fetches all available Result SIDs from AIRResult database.
    Looks for tables matching t{number}_LOSS_ByEvent pattern.
    Returns a list of integer Result SIDs.
    """
    query = """
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_NAME LIKE 't[0-9]%_LOSS_ByEvent'
        ORDER BY TABLE_NAME DESC
    """
    try:
        conn = get_connection()
        df = pd.read_sql(query, conn)
        conn.close()

        # Extract the SID number from table name e.g. t99002_LOSS_ByEvent → 99002
        sids = []
        for name in df["TABLE_NAME"]:
            parts = name.split("_")
            sid_str = parts[0].replace("t", "")
            if sid_str.isdigit():
                sids.append(int(sid_str))

        return sorted(sids, reverse=True)

    except Exception as e:
        raise Exception(f"Failed to fetch Result SIDs: {e}")


# ── Fetch loss by event (ELT) ─────────────────────────────────────────────────

def get_loss_by_event(result_sid):
    """
    Fetches ELT data for a given Result SID.
    Table: t{result_sid}_LOSS_ByEvent
    """
    table = f"t{result_sid}_LOSS_ByEvent"
    query = f"SELECT * FROM [AIRResult].[dbo].[{table}]"
    try:
        conn = get_connection()
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        raise Exception(f"Failed to fetch ELT for Result SID {result_sid}: {e}")


# ── Fetch annual EP summary ───────────────────────────────────────────────────

def get_loss_annual_ep_summary(result_sid):
    """
    Fetches Annual EP Summary for a given Result SID.
    Table: t{result_sid}_LOSS_AnnualEPSummary
    """
    table = f"t{result_sid}_LOSS_AnnualEPSummary"
    query = f"SELECT * FROM [AIRResult].[dbo].[{table}]"
    try:
        conn = get_connection()
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        raise Exception(f"Failed to fetch EP Summary for Result SID {result_sid}: {e}")


# ── Fetch loss by location ────────────────────────────────────────────────────

def get_loss_by_location(result_sid):
    """
    Fetches loss by location for a given Result SID.
    Table: t{result_sid}_LOSS_ByLocation
    """
    table = f"t{result_sid}_LOSS_ByLocation"
    query = f"SELECT * FROM [AIRResult].[dbo].[{table}]"
    try:
        conn = get_connection()
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        raise Exception(f"Failed to fetch Loss by Location for Result SID {result_sid}: {e}")


# ── Check which tables exist for a Result SID ────────────────────────────────

def get_available_tables(result_sid):
    """
    Returns list of all tables available for a given Result SID.
    Useful to know which datasets exist before querying.
    """
    query = f"""
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_NAME LIKE 't{result_sid}_%'
        ORDER BY TABLE_NAME
    """
    try:
        conn = get_connection()
        df = pd.read_sql(query, conn)
        conn.close()
        return df["TABLE_NAME"].tolist()
    except Exception as e:
        raise Exception(f"Failed to fetch tables for Result SID {result_sid}: {e}")


# ── Test ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Testing SQL connection...")
    try:
        sids = get_available_result_sids()
        print(f"✓ Connected — {len(sids)} Result SIDs found")
        print(f"  Most recent: {sids[:5]}")
    except Exception as e:
        print(f"✗ Failed: {e}")