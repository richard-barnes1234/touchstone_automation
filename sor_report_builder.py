# sor_report_builder.py
# ─────────────────────────────────────────────────────────────────────────────
# Builds the broker-facing SOR loss report using Jennifer's calculation method:
#
#   AEP (Aggregate Exceedance Probability)
#       → Sum ALL event losses per year
#       → Sort descending by sum → rank = row order
#       → Return Period = N_years / rank
#       → AEP AAL = sum of all event losses / N_years
#
#   OEP (Occurrence Exceedance Probability)
#       → Max single event loss per year
#       → Sort GU and Gross INDEPENDENTLY (different sort orders possible)
#       → Return Period = N_years / rank
#       → OEP AAL = sum of max losses / N_years
#
#   N_years detected from data (max YearID) — handles 10,000 / 500,000 etc.
#
# All calculations done in Python/pandas → static values written to Excel.
# No live formulas needed for the calculation tables.
# ─────────────────────────────────────────────────────────────────────────────

from io import BytesIO
import pandas as pd
import numpy as np
import openpyxl
from copy import copy
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, numbers
from openpyxl.utils import get_column_letter

from model_code_ref import MODEL_CODE_REF, get_report_label
from model_lookup import get_model_description


# ── Styling helpers ───────────────────────────────────────────────────────────

def _thin():
    return Border(*(Side(style="thin", color="D1D5DB"),) * 4)

def _style_header(ws, row, col_start, col_end, fill="1E3A5F"):
    for col in range(col_start, col_end + 1):
        cell = ws.cell(row=row, column=col)
        cell.font      = Font(name="Calibri", bold=True, color="FFFFFF", size=10)
        cell.fill      = PatternFill("solid", fgColor=fill)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border    = _thin()

def _write_header_row(ws, row, headers, fill="1E3A5F"):
    """Write a list of header strings starting at col 1."""
    for c_idx, h in enumerate(headers, start=1):
        ws.cell(row=row, column=c_idx, value=h)
    _style_header(ws, row, 1, len(headers), fill)

def _style_data_row(ws, row, n_cols, alternate=False):
    bg = "F0F4F8" if alternate else "FFFFFF"
    for col in range(1, n_cols + 1):
        cell = ws.cell(row=row, column=col)
        cell.font      = Font(name="Calibri", size=9)
        cell.fill      = PatternFill("solid", fgColor=bg)
        cell.alignment = Alignment(horizontal="right", vertical="center")
        cell.border    = _thin()

def _num(ws, row, col, value, fmt="#,##0", alternate=False):
    cell = ws.cell(row=row, column=col, value=value)
    cell.number_format = fmt
    cell.font          = Font(name="Calibri", size=9)
    cell.fill          = PatternFill("solid", fgColor="F0F4F8" if alternate else "FFFFFF")
    cell.alignment     = Alignment(horizontal="right", vertical="center")
    cell.border        = _thin()
    return cell

def _label(ws, row, col, value, bold=False, color="1A1814", size=9, fill="FFFFFF"):
    cell = ws.cell(row=row, column=col, value=value)
    cell.font      = Font(name="Calibri", bold=bold, color=color, size=size)
    cell.fill      = PatternFill("solid", fgColor=fill)
    cell.alignment = Alignment(horizontal="left", vertical="center")
    cell.border    = _thin()
    return cell


# ── Core calculation engine ───────────────────────────────────────────────────

def _calculate(df):
    """
    Given a filtered STC ELT DataFrame, compute all AEP/OEP tables.
    Returns a dict with all computed results.
    """
    # Detect N_years from max YearID (handles 10k, 500k etc.)
    n_years = int(df["YearID"].max()) if not df.empty else 10000
    print(f"  [SOR] N_years detected: {n_years:,} | Events: {len(df):,}")

    if df.empty:
        return {
            "n_years": n_years,
            "aep_gu": pd.DataFrame(), "aep_gr": pd.DataFrame(),
            "oep_gu": pd.DataFrame(), "oep_gr": pd.DataFrame(),
            "aep_aal_gu": 0, "aep_aal_gr": 0,
            "oep_aal_gu": 0, "oep_aal_gr": 0,
            "raw": df, "model_label": "",
        }

    # ── AEP — sum all losses per year ────────────────────────────────────────
    agg = df.groupby("YearID").agg(
        GULoss=("GroundUpLoss", "sum"),
        GRLoss=("GrossLoss",    "sum"),
    ).reset_index()

    # Sort GU descending for AEP GU
    aep_gu = agg[["YearID","GULoss"]].sort_values("GULoss", ascending=False).reset_index(drop=True)
    aep_gu["Rank"]         = aep_gu.index + 1
    aep_gu["ReturnPeriod"] = n_years / aep_gu["Rank"]

    # Sort GR descending independently for AEP GR
    aep_gr = agg[["YearID","GRLoss"]].sort_values("GRLoss", ascending=False).reset_index(drop=True)
    aep_gr["Rank"]         = aep_gr.index + 1
    aep_gr["ReturnPeriod"] = n_years / aep_gr["Rank"]

    # AEP AAL = total of all event losses / n_years
    aep_aal_gu = df["GroundUpLoss"].sum() / n_years
    aep_aal_gr = df["GrossLoss"].sum()    / n_years

    # ── OEP — max single event per year ──────────────────────────────────────
    occ = df.groupby("YearID").agg(
        GUMax=("GroundUpLoss", "max"),
        GRMax=("GrossLoss",    "max"),
    ).reset_index()

    # Sort GU max descending for OEP GU
    oep_gu = occ[["YearID","GUMax"]].sort_values("GUMax", ascending=False).reset_index(drop=True)
    oep_gu["Rank"]         = oep_gu.index + 1
    oep_gu["ReturnPeriod"] = n_years / oep_gu["Rank"]

    # Sort GR max descending independently for OEP GR
    oep_gr = occ[["YearID","GRMax"]].sort_values("GRMax", ascending=False).reset_index(drop=True)
    oep_gr["Rank"]         = oep_gr.index + 1
    oep_gr["ReturnPeriod"] = n_years / oep_gr["Rank"]

    # OEP AAL = sum of max losses per year / n_years
    oep_aal_gu = occ["GUMax"].sum() / n_years
    oep_aal_gr = occ["GRMax"].sum() / n_years

    # Model label
    model_label = ""
    if "ModelCode" in df.columns:
        first_code = df["ModelCode"].dropna().iloc[0] if not df["ModelCode"].dropna().empty else None
        if first_code:
            model_label = get_report_label(int(first_code)) or get_model_description(int(first_code))

    return {
        "n_years":    n_years,
        "aep_gu":     aep_gu,
        "aep_gr":     aep_gr,
        "oep_gu":     oep_gu,
        "oep_gr":     oep_gr,
        "aep_aal_gu": aep_aal_gu,
        "aep_aal_gr": aep_aal_gr,
        "oep_aal_gu": oep_aal_gu,
        "oep_aal_gr": oep_aal_gr,
        "raw":         df,
        "model_label": model_label,
    }


def _get_rp_loss(df_sorted, rp_col, loss_col, target_rp, n_years):
    """
    Find the loss at a given return period from a sorted DataFrame.
    Uses the row where ReturnPeriod >= target_rp (largest rank still qualifying).
    Falls back to LARGE-equivalent: rank = floor(n_years / target_rp).
    """
    rank = int(n_years / target_rp)
    if rank < 1:
        return 0
    if rank <= len(df_sorted):
        return float(df_sorted.iloc[rank - 1][loss_col])
    return 0


# ── Sheet builder ─────────────────────────────────────────────────────────────

def _build_loss_sheet(ws, calc, meta):
    """
    Layout matching Jennifer's template exactly:

    Row 1  : Section labels — AEP (merged) | OEP (merged) | AEP AAL | OEP AAL
    Row 2  : Column headers — Row Labels | Sum GU Loss | Sum GR Loss | Max GU Loss | Max GR Loss | Order | Return Period
    Rows 3+: Data — one row per year (only years with events), sorted by OEP GU descending
             Return period highlighted at key values (10000=yellow, 5000, 1000, 500=highlighted)
    AAL table sits to the right of the main table
    """
    n_years     = calc["n_years"]
    aep_gu      = calc["aep_gu"]
    aep_gr      = calc["aep_gr"]
    oep_gu      = calc["oep_gu"]
    oep_gr      = calc["oep_gr"]
    model_label = calc["model_label"] or meta.get("analysis_name", "")

    # ── Column positions (matching Jennifer's template) ───────────────────────
    # A=RowLabels B=SumGU C=SumGR D=MaxGU E=MaxGR F=Order G=ReturnPeriod
    # H=gap  I=AEP_GU_AAL J=AEP_GR_AAL K=gap L=OEP_GU_AAL M=OEP_GR_AAL
    C_LABEL      = 1   # A: Row Labels (YearID)
    C_AEP_GU     = 2   # B: Sum of GroundUpLoss
    C_AEP_GR     = 3   # C: Sum of GrossLoss
    C_OEP_GU     = 4   # D: Max of GroundUpLoss
    C_OEP_GR     = 5   # E: Max of GrossLoss
    C_ORDER      = 6   # F: Order (rank)
    C_RP         = 7   # G: Return Period
    C_AAL_AEP_GU = 9   # I: AEP GU AAL
    C_AAL_AEP_GR = 10  # J: AEP GR AAL
    C_AAL_OEP_GU = 12  # L: OEP GU AAL
    C_AAL_OEP_GR = 13  # M: OEP GR AAL



    # ── Build merged data table ───────────────────────────────────────────────
    # One row per year with events, sorted by OEP GU descending
    if not oep_gu.empty:
        merged = oep_gu[["YearID", "GUMax", "Rank", "ReturnPeriod"]].copy()
        merged.columns = ["YearID", "OEP_GU", "Order", "ReturnPeriod"]
        # Add OEP GR by YearID
        oep_gr_map = dict(zip(oep_gr["YearID"], oep_gr["GRMax"]))
        merged["OEP_GR"] = merged["YearID"].map(oep_gr_map).fillna(0)
        # Add AEP GU and GR by YearID
        aep_gu_map = dict(zip(aep_gu["YearID"], aep_gu["GULoss"]))
        aep_gr_map = dict(zip(aep_gr["YearID"], aep_gr["GRLoss"]))
        merged["AEP_GU"] = merged["YearID"].map(aep_gu_map).fillna(0)
        merged["AEP_GR"] = merged["YearID"].map(aep_gr_map).fillna(0)
        # Sort by OEP GU descending, reassign Order and RP
        merged = merged.sort_values("OEP_GU", ascending=False).reset_index(drop=True)
        merged["Order"]        = merged.index + 1
        merged["ReturnPeriod"] = n_years / merged["Order"]
    else:
        merged = pd.DataFrame(columns=["YearID","AEP_GU","AEP_GR",
                                        "OEP_GU","OEP_GR","Order","ReturnPeriod"])

    # ── Row 1: Section label headers (merged cells) ───────────────────────────
    sections = [
        (C_LABEL,      C_AEP_GR,     "AEP", "1E3A5F"),
        (C_OEP_GU,     C_RP,         "OEP", "2E5B9A"),
        (C_AAL_AEP_GU, C_AAL_AEP_GR, "AEP", "1E3A5F"),
        (C_AAL_OEP_GU, C_AAL_OEP_GR, "OEP", "2E5B9A"),
    ]
    for c_start, c_end, label, fill in sections:
        cell = ws.cell(row=1, column=c_start, value=label)
        cell.font      = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
        cell.fill      = PatternFill("solid", fgColor=fill)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border    = _thin()
        if c_end > c_start:
            ws.merge_cells(start_row=1, start_column=c_start,
                           end_row=1,   end_column=c_end)

    # ── Row 2: Column headers ─────────────────────────────────────────────────
    col_headers = {
        C_LABEL:      ("Row Labels",           "1E3A5F"),
        C_AEP_GU:     ("Sum of GroundUpLoss",  "1E3A5F"),
        C_AEP_GR:     ("Sum of GrossLoss",     "1E3A5F"),
        C_OEP_GU:     ("Max of GroundUpLoss",  "2E5B9A"),
        C_OEP_GR:     ("Max of GrossLoss",     "2E5B9A"),
        C_ORDER:      ("Order",                "2E5B9A"),
        C_RP:         ("Return Period",         "2E5B9A"),
        C_AAL_AEP_GU: ("GU AAL",               "1E3A5F"),
        C_AAL_AEP_GR: ("GR AAL",               "1E3A5F"),
        C_AAL_OEP_GU: ("GU AAL",               "2E5B9A"),
        C_AAL_OEP_GR: ("GR AAL",               "2E5B9A"),
    }
    for col, (label, fill) in col_headers.items():
        cell = ws.cell(row=2, column=col, value=label)
        cell.font      = Font(name="Calibri", bold=True, color="FFFFFF", size=9)
        cell.fill      = PatternFill("solid", fgColor=fill)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border    = _thin()
    ws.row_dimensions[2].height = 30

    # ── Rows 3+: Data rows ────────────────────────────────────────────────────
    for i, row in merged.iterrows():
        r      = 3 + i
        rp_val = round(row["ReturnPeriod"], 1)
        bg = "F0F4F8" if i % 2 == 1 else "FFFFFF"

        values = {
            C_LABEL:  int(row["YearID"]),
            C_AEP_GU: round(row["AEP_GU"]),
            C_AEP_GR: round(row["AEP_GR"]),
            C_OEP_GU: round(row["OEP_GU"]),
            C_OEP_GR: round(row["OEP_GR"]),
            C_ORDER:  int(row["Order"]),
            C_RP:     rp_val,
        }
        fmts = {
            C_LABEL: "#,##0", C_AEP_GU: "#,##0", C_AEP_GR: "#,##0",
            C_OEP_GU: "#,##0", C_OEP_GR: "#,##0",
            C_ORDER: "#,##0", C_RP: "#,##0.0",
        }
        for col, val in values.items():
            cell = ws.cell(row=r, column=col, value=val)
            cell.font          = Font(name="Calibri", size=9)
            cell.fill          = PatternFill("solid", fgColor=bg)
            cell.alignment     = Alignment(horizontal="right", vertical="center")
            cell.border        = _thin()
            cell.number_format = fmts[col]

    # ── AAL values — row 3 only, cols I-M ────────────────────────────────────
    aal_data = {
        C_AAL_AEP_GU: (round(calc["aep_aal_gu"]), "1E3A5F"),
        C_AAL_AEP_GR: (round(calc["aep_aal_gr"]), "1E3A5F"),
        C_AAL_OEP_GU: (round(calc["oep_aal_gu"]), "2E5B9A"),
        C_AAL_OEP_GR: (round(calc["oep_aal_gr"]), "2E5B9A"),
    }
    for col, (val, fill) in aal_data.items():
        cell = ws.cell(row=3, column=col, value=val)
        cell.font          = Font(name="Calibri", bold=True, color="FFFFFF", size=9)
        cell.fill          = PatternFill("solid", fgColor=fill)
        cell.alignment     = Alignment(horizontal="right", vertical="center")
        cell.border        = _thin()
        cell.number_format = "#,##0"

    # ── Column widths ─────────────────────────────────────────────────────────
    col_widths = {
        "A": 10, "B": 18, "C": 16,
        "D": 18, "E": 16,
        "F": 8,  "G": 14,
        "H": 2,
        "I": 14, "J": 14,
        "K": 2,
        "L": 14, "M": 14,
    }
    for col, width in col_widths.items():
        ws.column_dimensions[col].width = width

    ws.row_dimensions[1].height = 20
    ws.freeze_panes = "A3"


# ── ModelCodeRef sheet ────────────────────────────────────────────────────────

def _add_model_code_ref(wb):
    if "ModelCodeRef" in wb.sheetnames:
        return
    ws = wb.create_sheet("ModelCodeRef")
    headers = ["ModelCode", "Model", None, "BriefName", "Analysis Name for Report"]
    for c_idx, h in enumerate(headers, start=1):
        if h:
            ws.cell(row=3, column=c_idx, value=h)
    _style_header(ws, 3, 1, 5)
    for r_idx, (code, model, brief, label) in enumerate(MODEL_CODE_REF, start=4):
        ws.cell(row=r_idx, column=1, value=code)
        ws.cell(row=r_idx, column=2, value=model)
        ws.cell(row=r_idx, column=4, value=brief)
        ws.cell(row=r_idx, column=5, value=label)
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 55
    ws.column_dimensions["D"].width = 18
    ws.column_dimensions["E"].width = 22


# ── Public API ─────────────────────────────────────────────────────────────────

def _prepare_df(df_elt):
    """Filter to STC, coerce numeric types."""
    if df_elt is None or df_elt.empty:
        return pd.DataFrame()
    if 'CatalogTypeCode' in df_elt.columns:
        df = df_elt[df_elt['CatalogTypeCode'] == 'STC'].copy()
    else:
        df = df_elt.copy()
    for col in ("EventID", "GrossLoss", "GroundUpLoss", "ModelCode", "YearID"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["YearID", "GroundUpLoss", "GrossLoss"])
    if df.empty:
        print("  [SOR] WARNING: No STC events after filtering — analysis may use RDS/HIS catalog only")
    return df


def build_sor_report(meta, df_elt):
    """
    Builds a single-analysis SOR broker report.
    Returns BytesIO containing .xlsx file.
    """
    df   = _prepare_df(df_elt)
    calc = _calculate(df)

    wb = Workbook()
    ws = wb.active
    # Name the sheet after the model label, fallback to "LossTables"
    sheet_name = (calc["model_label"] or meta.get("analysis_name", "LossTables"))[:31].strip()
    ws.title = sheet_name if sheet_name else "LossTables"

    _build_loss_sheet(ws, calc, meta)
    _add_model_code_ref(wb)

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output


def build_combined_sor_report(meta, analyses):
    """
    Builds a combined multi-peril workbook.
    analyses: list of dicts {sid, name, type, df, sheet_name}
    """
    wb = Workbook()
    ws_summary = wb.active
    ws_summary.title = "Summary"

    # Summary header
    ws_summary["A1"] = meta.get("project_name", "Combined Report")
    ws_summary["A1"].font = Font(name="Calibri", bold=True, size=16, color="1E3A5F")
    ws_summary["A3"] = "Generated"
    ws_summary["B3"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws_summary["A3"].font = Font(name="Calibri", bold=True, size=10)

    sum_headers = ["#", "Analysis SID", "Type", "Peril / Label", "Sheet", "Events", "Status"]
    _write_header_row(ws_summary, 5, sum_headers)

    thin = _thin()
    for row_idx, analysis in enumerate(analyses, start=1):
        sid     = analysis["sid"]
        atype   = analysis["type"]
        df_raw  = analysis.get("df")
        sname   = analysis.get("sheet_name", f"{atype}-{sid}")

        if atype == "LOSS":
            df   = _prepare_df(df_raw)
            calc = _calculate(df)
            label       = calc["model_label"] or analysis.get("name", f"LOSS-{sid}")
            event_count = f"{len(df):,} STC events"
            status      = "OK" if not df.empty else "No STC data"

            # Create analysis sheet
            ws = wb.create_sheet(title=sname[:31])
            _build_loss_sheet(ws, calc, {**meta, "analysis_sid": sid,
                                          "analysis_name": analysis.get("name", sname)})

        elif atype == "HAZ":
            label       = analysis.get("name", f"HAZ-{sid}")
            haz_data    = df_raw if isinstance(df_raw, dict) else {}
            total       = sum(len(v) for v in haz_data.values()) if haz_data else 0
            event_count = f"{total:,} records"
            status      = "OK" if total > 0 else "No data"

            ws = wb.create_sheet(title=sname[:31])
            ws["A1"] = f"Hazard Analysis — SID {sid}"
            ws["A1"].font = Font(name="Calibri", bold=True, size=14, color="1E3A5F")
            row_start = 3
            for cat_name, cat_df in haz_data.items():
                if cat_df is None or cat_df.empty:
                    continue
                ws.cell(row=row_start, column=1, value=cat_name).font = Font(bold=True, size=11, color="2E5B9A")
                row_start += 1
                _write_header_row(ws, row_start, list(cat_df.columns))
                row_start += 1
                for _, data_row in cat_df.iterrows():
                    for c_idx, val in enumerate(data_row, start=1):
                        ws.cell(row=row_start, column=c_idx, value=val)
                    row_start += 1
                row_start += 1
        else:
            label = event_count = status = "—"

        # Write summary row
        r = 5 + row_idx
        for c_idx, v in enumerate([row_idx, sid, atype, label, sname, event_count, status], start=1):
            cell = ws_summary.cell(row=r, column=c_idx, value=v)
            cell.border = thin
            cell.font   = Font(name="Calibri", size=10,
                               color=("065F46" if status == "OK" else "991B1B") if c_idx == 7 else "1A1814",
                               bold=(c_idx == 7))

    for col, width in zip("ABCDEFG", [5, 14, 8, 35, 20, 18, 12]):
        ws_summary.column_dimensions[col].width = width

    _add_model_code_ref(wb)

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output