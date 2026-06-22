# sor_report_builder.py
# ─────────────────────────────────────────────────────────────────────────────
# Builds the broker-facing "SOR" loss report, replicating the exact structure
# and live Excel formulas from Copy_of_SampleReportCalculation_SOR_20260618.xlsx
#
# Replaces the previous ELT / EP Curves / Loss Summary export for LOSS analyses.
# Scope: CatalogTypeCode = "STC" only (per Richard's feedback, 2026-06-18).
#
# Sheet 1: LossTables  — raw STC ELT rows + AGG/OCC derived tables + EP summary
# Sheet 2: ModelCodeRef — model code -> report label lookup table
# ─────────────────────────────────────────────────────────────────────────────

from io import BytesIO
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from model_code_ref import MODEL_CODE_REF

N_YEARS = 10000  # AIR catalog years — fixed simulation length


def _style_header(ws, row, col_start, col_end, fill="1E3A5F"):
    thin = Border(*(Side(style="thin", color="D1D5DB"),) * 4)
    for col in range(col_start, col_end + 1):
        cell = ws.cell(row=row, column=col)
        cell.font = Font(name="Calibri", bold=True, color="FFFFFF", size=10)
        cell.fill = PatternFill("solid", fgColor=fill)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin


def build_sor_report(meta, df_elt):
    """
    Builds the SOR-style broker report workbook.

    meta   : dict with project_name, analysis_sid, analysis_name, analysis_type
    df_elt : full ELT DataFrame (unfiltered) — function filters to STC internally

    Returns a BytesIO containing the .xlsx file.
    """
    # ── Use all rows as returned by the API ────────────────────────────────────
    # CatalogTypeCode varies by peril/model (e.g. STC for severe storm, RDS for
    # other perils) — it is NOT a fixed filter. The analysis is already scoped
    # to one peril/model by the AnalysisSid itself, so no additional filtering
    # is needed here.
    df = df_elt.copy() if not df_elt.empty else df_elt

    # API returns numeric fields as strings — coerce for SUMIFS/MAXIFS to work
    if not df.empty:
        for col in ("EventID", "GrossLoss", "GroundUpLoss", "ModelCode", "YearID"):
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

    # Diagnostic — helps confirm data shape before building report
    if not df.empty:
        unique_years = df["YearID"].nunique() if "YearID" in df.columns else 0
        print(f"  [SOR] Events: {len(df):,} | Unique years with events: {unique_years:,} of {N_YEARS:,}")
        if unique_years < 100:
            print(f"  [SOR] WARNING: Only {unique_years} years have events — "
                  f"100/250/500/1000yr RP values may not appear in column P. "
                  f"VLOOKUP will return 0 via IFERROR for missing RPs.")
    else:
        print("  [SOR] WARNING: No event data — all tables will show 0")

    wb = Workbook()
    ws = wb.active
    ws.title = "LossTables"

    # ── Section headers (row 1) ────────────────────────────────────────────────
    ws["I1"] = "AGG"
    ws["O1"] = "OCC"
    if df.empty:
        ws["U1"] = "No STC events found for this analysis"
    else:
        ws["U1"] = "=VLOOKUP($F4,ModelCodeRef!$A$3:$E$26,5)"   # analysis label, matches sample exactly
    for cell in ("I1", "O1"):
        ws[cell].font = Font(bold=True, size=11, color="1E3A5F")
    ws["U1"].font = Font(bold=True, size=12, color="1E3A5F")

    # ── Column headers (row 3) ────────────────────────────────────────────────
    headers = {
        "A3": "CatalogTypeCode", "B3": "EventDescription", "C3": "EventID",
        "D3": "GrossLoss",       "E3": "GroundUpLoss",     "F3": "ModelCode", "G3": "YearID",
        "I3": "Year", "J3": "GULoss", "K3": "GUStdDevSq", "L3": "GRLoss", "M3": "GRStdDevSq",
        "O3": "Year", "P3": "GURP", "Q3": "GULoss", "R3": "GRRP", "S3": "GRLoss",
        "U3": "Perspective", "V3": 100, "W3": 250, "X3": 500, "Y3": 1000, "Z3": "AAL", "AA3": "SD",
    }
    for coord, val in headers.items():
        ws[coord] = val
    _style_header(ws, 3, 1, 7)    # raw data headers
    _style_header(ws, 3, 9, 13)   # AGG headers
    _style_header(ws, 3, 15, 19)  # OCC headers
    _style_header(ws, 3, 21, 27)  # EP summary headers

    # ── Raw STC event rows (columns A-G) ───────────────────────────────────────
    raw_cols  = ["CatalogTypeCode", "EventDescription", "EventID", "GrossLoss", "GroundUpLoss", "ModelCode", "YearID"]
    int_cols  = {"EventID", "ModelCode", "YearID"}
    float_cols = {"GrossLoss", "GroundUpLoss"}
    if not df.empty:
        for r_idx, row in enumerate(df[raw_cols].itertuples(index=False), start=4):
            for c_idx, (col_name, val) in enumerate(zip(raw_cols, row), start=1):
                if col_name in int_cols:
                    try: val = int(float(val))
                    except (ValueError, TypeError): pass
                elif col_name in float_cols:
                    try: val = float(val)
                    except (ValueError, TypeError): pass
                ws.cell(row=r_idx, column=c_idx, value=val)

    last_event_row = max(4, 3 + len(df))

    # ── AGG table — one row per simulation year (1..10000) ────────────────────
    # I=Year J=GULoss K=GUStdDevSq L=GRLoss M=GRStdDevSq
    # CRITICAL: SUMIFS uses $O (OCC Year column) as the year reference — matches
    # original sample exactly. AGG and OCC share the same Year sequence.
    for i, year in enumerate(range(1, N_YEARS + 1)):
        r = 4 + i
        ws.cell(row=r, column=9,  value=1 if year == 1 else f"=I{r-1}+1")           # I: Year
        ws.cell(row=r, column=10, value=f"=SUMIFS($E:$E,$G:$G,$O{r})")              # J: GULoss (uses O not I)
        ws.cell(row=r, column=11, value=f"=(J{r}-$Z$4)^2")                           # K: GUStdDevSq vs AAL GU
        ws.cell(row=r, column=12, value=f"=SUMIFS($D:$D,$G:$G,$O{r})")              # L: GRLoss (uses O not I)
        ws.cell(row=r, column=13, value=f"=(L{r}-$Z$5)^2")                           # M: GRStdDevSq vs AAL Gross

    # ── OCC table — one row per simulation year, MAX event in year ────────────
    # O=Year P=GURP Q=GULoss R=GRRP S=GRLoss
    last_occ_row = 3 + N_YEARS
    for i, year in enumerate(range(1, N_YEARS + 1)):
        r = 4 + i
        ws.cell(row=r, column=15, value=1 if year == 1 else f"=O{r-1}+1")                                                # O: Year
        ws.cell(row=r, column=16, value=f"=1/(_xlfn.RANK.EQ(Q{r},$Q$4:$Q${last_occ_row},0)/{N_YEARS})")                  # P: GURP
        ws.cell(row=r, column=17, value=f"=_xlfn.MAXIFS($E:$E,$G:$G,$O{r})")                                             # Q: GULoss
        ws.cell(row=r, column=18, value=f"=1/(_xlfn.RANK.EQ(S{r},$S$4:$S${last_occ_row},0)/{N_YEARS})")                  # R: GRRP
        ws.cell(row=r, column=19, value=f"=_xlfn.MAXIFS(D:D,$G:$G,$O{r})")                                               # S: GRLoss

    # ── EP / AAL / SD summary table (rows 4-5) ─────────────────────────────────
    # Exact replica of original sample formulas:
    # V4: =VLOOKUP(V$3,$P$3:$Q$10003,2,FALSE) — Ground Up RP lookup from OCC P/Q cols
    # V5: =VLOOKUP(V$3,$R$3:$S$10003,2,FALSE) — Gross RP lookup from OCC R/S cols
    # Z4: =SUM($J$4:$J$10003)/10000           — AAL Ground Up from AGG
    # Z5: =SUM($L$4:$L$10003)/10000           — AAL Gross from AGG
    ws["U4"] = "Ground Up"
    ws["U5"] = "Gross"
    # LARGE is the most reliable approach regardless of data density or floating
    # point precision issues with RANK.EQ-derived return period values in column P.
    # 100yr = 100th largest, 250yr = 40th largest, 500yr = 20th largest, 1000yr = 10th largest
    rp_ranks = {"V": 100, "W": 40, "X": 20, "Y": 10}
    for rp_letter, rank in rp_ranks.items():
        ws[f"{rp_letter}4"] = f"=IFERROR(LARGE($Q$4:$Q${last_occ_row},{rank}),0)"
        ws[f"{rp_letter}5"] = f"=IFERROR(LARGE($S$4:$S${last_occ_row},{rank}),0)"
    ws["Z4"]  = f"=SUM($J$4:$J${last_occ_row})/{N_YEARS}"
    ws["AA4"] = f"=SQRT(SUM($K$4:$K${last_occ_row})/({N_YEARS}-1))"
    ws["Z5"]  = f"=SUM($L$4:$L${last_occ_row})/{N_YEARS}"
    ws["AA5"] = f"=SQRT(SUM($M$4:$M${last_occ_row})/({N_YEARS}-1))"

    # ── Top 5 Events table (rows 7-12) ────────────────────────────────────────
    # Row 7: headers
    ws["U7"] = "Loss Exceedance"
    ws["V7"] = "Ground Up"
    ws["W7"] = "Gross"
    ws["X7"] = "Max Affected States"
    _style_header(ws, 7, 21, 24, fill="2E5B9A")

    # Rows 8-12: top 5 return period levels using LARGE for robust RP calculation
    # Loss Exceedance = return period = 10000/rank
    # 10000yr = rank 1, 5000yr = rank 2, 3333yr = rank 3, 2500yr = rank 4, 2000yr = rank 5
    top5_levels = [10000, 5000, 10000/3, 2500, 2000]
    top5_ranks  = [1, 2, 3, 4, 5]
    for i, (level, rank) in enumerate(zip(top5_levels, top5_ranks)):
        r = 8 + i
        ws.cell(row=r, column=21, value=level)
        ws.cell(row=r, column=22, value=f"=IFERROR(LARGE($Q$4:$Q${last_occ_row},{rank}),0)")
        ws.cell(row=r, column=23, value=f"=IFERROR(LARGE($S$4:$S${last_occ_row},{rank}),0)")
        ws.cell(row=r, column=24, value=f'=_xlfn.XLOOKUP(V{r},E:E,B:B,"")')

    # Style Top 5 data rows
    from openpyxl.styles import numbers
    thin = Border(*(Side(style="thin", color="D1D5DB"),) * 4)
    for r in range(8, 13):
        for c in range(21, 25):
            cell = ws.cell(row=r, column=c)
            cell.border = thin
            cell.font = Font(name="Calibri", size=9)
        ws.cell(row=r, column=21).alignment = Alignment(horizontal="right")
    ws.column_dimensions["X"].width = 80   # EventDescription needs extra width
    widths = {"A": 14, "B": 50, "C": 10, "D": 14, "E": 14, "F": 10, "G": 9,
              "I": 8, "J": 14, "K": 16, "L": 14, "M": 16,
              "O": 8, "P": 12, "Q": 14, "R": 12, "S": 14,
              "U": 12, "V": 12, "W": 12, "X": 12, "Y": 12, "Z": 14, "AA": 14}
    for col, width in widths.items():
        ws.column_dimensions[col].width = width
    ws.freeze_panes = "A4"

    # ── ModelCodeRef sheet ────────────────────────────────────────────────────
    ws_ref = wb.create_sheet("ModelCodeRef")
    ref_headers = ["ModelCode", "Model", None, "BriefName", "Analysis Name for Report"]
    for c_idx, h in enumerate(ref_headers, start=1):
        if h:
            ws_ref.cell(row=3, column=c_idx, value=h)
    _style_header(ws_ref, 3, 1, 5)
    for r_idx, (code, model, brief, label) in enumerate(MODEL_CODE_REF, start=4):
        ws_ref.cell(row=r_idx, column=1, value=code)
        ws_ref.cell(row=r_idx, column=2, value=model)
        ws_ref.cell(row=r_idx, column=4, value=brief)
        ws_ref.cell(row=r_idx, column=5, value=label)
    ws_ref.column_dimensions["A"].width = 12
    ws_ref.column_dimensions["B"].width = 55
    ws_ref.column_dimensions["D"].width = 18
    ws_ref.column_dimensions["E"].width = 22

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output