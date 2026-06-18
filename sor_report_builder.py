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
    # ── Filter to STC only ────────────────────────────────────────────────────
    df = df_elt[df_elt["CatalogTypeCode"] == "STC"].copy() if not df_elt.empty else df_elt

    # API returns numeric fields as strings — coerce for SUMIFS/MAXIFS to work
    if not df.empty:
        for col in ("EventID", "GrossLoss", "GroundUpLoss", "ModelCode", "YearID"):
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

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
    raw_cols = ["CatalogTypeCode", "EventDescription", "EventID", "GrossLoss", "GroundUpLoss", "ModelCode", "YearID"]
    if not df.empty:
        for r_idx, row in enumerate(df[raw_cols].itertuples(index=False), start=4):
            for c_idx, val in enumerate(row, start=1):
                ws.cell(row=r_idx, column=c_idx, value=val)

    last_event_row = max(4, 3 + len(df))

    # ── AGG table — one row per simulation year (1..10000) ────────────────────
    # I=Year J=GULoss K=GUStdDevSq L=GRLoss M=GRStdDevSq
    for i, year in enumerate(range(1, N_YEARS + 1)):
        r = 4 + i
        ws.cell(row=r, column=9,  value=1 if year == 1 else f"=I{r-1}+1")            # I: Year
        ws.cell(row=r, column=10, value=f"=SUMIFS($E:$E,$G:$G,$I{r})")               # J: GULoss
        ws.cell(row=r, column=11, value=f"=(J{r}-$Z$4)^2")                            # K: GUStdDevSq
        ws.cell(row=r, column=12, value=f"=SUMIFS($D:$D,$G:$G,$I{r})")               # L: GRLoss
        ws.cell(row=r, column=13, value=f"=(L{r}-$Z$5)^2")                            # M: GRStdDevSq

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
    ws["U4"] = "Ground Up"
    ws["U5"] = "Gross"
    for rp_col, rp_letter in zip((100, 250, 500, 1000), ("V", "W", "X", "Y")):
        ws[f"{rp_letter}4"] = f"=IFERROR(VLOOKUP({rp_letter}$3,$P$3:$Q${last_occ_row},2,FALSE),0)"   # Ground Up RP lookup
        ws[f"{rp_letter}5"] = f"=IFERROR(VLOOKUP({rp_letter}$3,$R$3:$S${last_occ_row},2,FALSE),0)"   # Gross RP lookup
    ws["Z4"] = f"=SUM($J$4:$J${last_occ_row})/{N_YEARS}"
    ws["AA4"] = f"=SQRT(SUM($K$4:$K${last_occ_row})/{N_YEARS - 1})"
    ws["Z5"] = f"=SUM($L$4:$L${last_occ_row})/{N_YEARS}"
    ws["AA5"] = f"=SQRT(SUM($M$4:$M${last_occ_row})/{N_YEARS - 1})"

    # ── Column widths ──────────────────────────────────────────────────────────
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