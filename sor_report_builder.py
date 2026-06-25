# sor_report_builder.py — Richard's sample structure + Option 5 optimization
from io import BytesIO
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from datetime import datetime
from model_code_ref import MODEL_CODE_REF
from model_lookup import get_model_description

N_YEARS = 10000


def _thin():
    return Border(*(Side(style="thin", color="D1D5DB"),) * 4)


def _style_header(ws, row, col_start, col_end, fill="1E3A5F"):
    for col in range(col_start, col_end + 1):
        cell = ws.cell(row=row, column=col)
        cell.font      = Font(name="Calibri", bold=True, color="FFFFFF", size=10)
        cell.fill      = PatternFill("solid", fgColor=fill)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border    = _thin()


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


def _prepare_df(df_elt):
    """Filter to STC, coerce numeric types. Handles actual API column names."""
    if df_elt is None or df_elt.empty:
        return pd.DataFrame()
    df = df_elt.copy()
    # Normalise column names
    col_map = {}
    for col in df.columns:
        cl = col.lower().replace(" ", "").replace("_", "")
        if cl == "grossloss" and "sd" not in cl:       col_map[col] = "GrossLoss"
        elif cl == "grounduploss" and "sd" not in cl:  col_map[col] = "GroundUpLoss"
        elif cl == "eventid":                           col_map[col] = "EventID"
        elif cl == "modelcode":                         col_map[col] = "ModelCode"
        elif cl == "yearid":                            col_map[col] = "YearID"
        elif cl == "catalogtypecode":                   col_map[col] = "CatalogTypeCode"
        elif cl == "eventdescription":                  col_map[col] = "EventDescription"
    if col_map:
        df = df.rename(columns=col_map)
    if "CatalogTypeCode" in df.columns:
        df = df[df["CatalogTypeCode"] == "STC"].copy()
    for col in ("EventID", "GrossLoss", "GroundUpLoss", "ModelCode", "YearID"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    required = [c for c in ["YearID", "GroundUpLoss", "GrossLoss"] if c in df.columns]
    if required:
        df = df.dropna(subset=required)
    unique_years = df["YearID"].nunique() if not df.empty else 0
    n_years      = int(df["YearID"].max()) if not df.empty else N_YEARS
    print(f"  [SOR] Events: {len(df):,} | Unique years: {unique_years:,} of {n_years:,}")
    if df.empty:
        print("  [SOR] WARNING: No STC events — analysis may use RDS/HIS catalog only")
    return df


def _build_loss_sheet(wb, df, meta):
    """Builds the LossTables sheet. Sheet named after model label."""
    n_years = int(df["YearID"].max()) if not df.empty else N_YEARS

    # Model label for sheet name and U1
    model_label = ""
    if not df.empty and "ModelCode" in df.columns:
        first_code = df["ModelCode"].dropna().iloc[0] if not df["ModelCode"].dropna().empty else None
        if first_code:
            from model_code_ref import get_report_label
            model_label = get_report_label(int(first_code)) or get_model_description(int(first_code))

    sheet_name = (model_label or meta.get("analysis_name", "LossTables"))[:31].strip() or "LossTables"
    ws = wb.create_sheet(title=sheet_name)
    last_occ_row = 3 + n_years

    # ── Row 1: section headers ────────────────────────────────────────────────
    ws["I1"] = "AGG"
    ws["O1"] = "OCC"
    ws["I1"].font = Font(bold=True, size=11, color="1E3A5F")
    ws["O1"].font = Font(bold=True, size=11, color="1E3A5F")
    ws["U1"] = "=VLOOKUP($F4,ModelCodeRef!$A$3:$E$26,5)" if not df.empty \
               else "No STC events — analysis may use RDS/HIS catalog only"
    ws["U1"].font = Font(bold=True, size=12, color="1E3A5F")

    # ── Row 3: column headers ─────────────────────────────────────────────────
    headers = {
        "A3":"CatalogTypeCode","B3":"EventDescription","C3":"EventID",
        "D3":"GrossLoss","E3":"GroundUpLoss","F3":"ModelCode","G3":"YearID",
        "I3":"Year","J3":"GULoss","K3":"GUStdDevSq","L3":"GRLoss","M3":"GRStdDevSq",
        "O3":"Year","P3":"GURP","Q3":"GULoss","R3":"GRRP","S3":"GRLoss",
        "U3":"Perspective","V3":100,"W3":250,"X3":500,"Y3":1000,"Z3":"AAL","AA3":"SD",
    }
    for coord, val in headers.items():
        ws[coord] = val
    _style_header(ws, 3, 1, 7)
    _style_header(ws, 3, 9, 13)
    _style_header(ws, 3, 15, 19)
    _style_header(ws, 3, 21, 27)

    # ── Raw STC event rows (cols A-G) ─────────────────────────────────────────
    raw_cols   = ["CatalogTypeCode","EventDescription","EventID",
                  "GrossLoss","GroundUpLoss","ModelCode","YearID"]
    int_cols   = {"EventID","ModelCode","YearID"}
    float_cols = {"GrossLoss","GroundUpLoss"}
    if not df.empty:
        avail = [c for c in raw_cols if c in df.columns]
        for r_idx, row in enumerate(df[avail].itertuples(index=False), start=4):
            for c_idx, (col_name, val) in enumerate(zip(avail, row), start=1):
                if col_name in int_cols:
                    try: val = int(float(val))
                    except: pass
                elif col_name in float_cols:
                    try: val = float(val)
                    except: pass
                ws.cell(row=r_idx, column=c_idx, value=val)

    # ── Option 5: Only write AGG/OCC rows for years that have events ──────────
    # Years with no events → SUMIFS/MAXIFS returns 0 anyway.
    # Skipping zero-event years reduces writes from 10,000 to ~2,000-4,000.
    # LARGE() in EP summary works correctly — it scans the whole column range
    # regardless of how many rows have data.
    event_years = set(df["YearID"].dropna().astype(int).unique()) if not df.empty else set()
    years_to_write = sorted(event_years) if event_years else list(range(1, n_years + 1))

    for year in years_to_write:
        r = 3 + year   # YearID 1 → row 4, YearID 10000 → row 10003
        # AGG (cols I-M)
        ws.cell(row=r, column=9,  value=year)
        ws.cell(row=r, column=10, value=f"=SUMIFS($E:$E,$G:$G,$O{r})")
        ws.cell(row=r, column=11, value=f"=(J{r}-$Z$4)^2")
        ws.cell(row=r, column=12, value=f"=SUMIFS($D:$D,$G:$G,$O{r})")
        ws.cell(row=r, column=13, value=f"=(L{r}-$Z$5)^2")
        # OCC (cols O-S)
        ws.cell(row=r, column=15, value=year)
        ws.cell(row=r, column=16, value=f"=1/(_xlfn.RANK.EQ(Q{r},$Q$4:$Q${last_occ_row},0)/{n_years})")
        ws.cell(row=r, column=17, value=f"=_xlfn.MAXIFS($E:$E,$G:$G,$O{r})")
        ws.cell(row=r, column=18, value=f"=1/(_xlfn.RANK.EQ(S{r},$S$4:$S${last_occ_row},0)/{n_years})")
        ws.cell(row=r, column=19, value=f"=_xlfn.MAXIFS(D:D,$G:$G,$O{r})")

    print(f"  [SOR] Wrote {len(years_to_write):,} AGG/OCC rows "
          f"(skipped {n_years - len(years_to_write):,} zero-event years)")

    # ── EP/AAL/SD summary (rows 4-5) ─────────────────────────────────────────
    ws["U4"] = "Ground Up"
    ws["U5"] = "Gross"
    rp_ranks = {"V": 100, "W": 40, "X": 20, "Y": 10}
    for rp_letter, rank in rp_ranks.items():
        ws[f"{rp_letter}4"] = f"=IFERROR(LARGE($Q$4:$Q${last_occ_row},{rank}),0)"
        ws[f"{rp_letter}5"] = f"=IFERROR(LARGE($S$4:$S${last_occ_row},{rank}),0)"
    ws["Z4"]  = f"=SUM($J$4:$J${last_occ_row})/{n_years}"
    ws["AA4"] = f"=SQRT(SUM($K$4:$K${last_occ_row})/({n_years}-1))"
    ws["Z5"]  = f"=SUM($L$4:$L${last_occ_row})/{n_years}"
    ws["AA5"] = f"=SQRT(SUM($M$4:$M${last_occ_row})/({n_years}-1))"

    # ── Top 5 events table (rows 7-12) ───────────────────────────────────────
    ws["U7"] = "Loss Exceedance"
    ws["V7"] = "Ground Up"
    ws["W7"] = "Gross"
    ws["X7"] = "Max Affected States"
    _style_header(ws, 7, 21, 24, fill="2E5B9A")
    thin = _thin()
    for i, (level, rank) in enumerate(zip([10000, 5000, 10000/3, 2500, 2000], [1,2,3,4,5])):
        r = 8 + i
        ws.cell(row=r, column=21, value=level)
        ws.cell(row=r, column=22, value=f"=IFERROR(LARGE($Q$4:$Q${last_occ_row},{rank}),0)")
        ws.cell(row=r, column=23, value=f"=IFERROR(LARGE($S$4:$S${last_occ_row},{rank}),0)")
        ws.cell(row=r, column=24, value=f'=_xlfn.XLOOKUP(V{r},E:E,B:B,"")')
        for col in range(21, 25):
            ws.cell(row=r, column=col).border = thin
            ws.cell(row=r, column=col).font   = Font(name="Calibri", size=9)

    # ── Column widths ─────────────────────────────────────────────────────────
    for col, w in {"A":14,"B":50,"C":10,"D":14,"E":14,"F":10,"G":9,
                   "I":8,"J":14,"K":16,"L":14,"M":16,
                   "O":8,"P":12,"Q":14,"R":12,"S":14,
                   "U":16,"V":14,"W":14,"X":80,"Y":14,"Z":14,"AA":14}.items():
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "A4"
    return ws


def build_sor_report(meta, df_elt):
    """Single-analysis SOR report. Returns BytesIO."""
    df = _prepare_df(df_elt)
    wb = Workbook()
    wb.remove(wb.active)
    _build_loss_sheet(wb, df, meta)
    _add_model_code_ref(wb)
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output


def build_combined_sor_report(meta, analyses):
    """Multi-analysis combined workbook — one sheet per analysis."""
    wb = Workbook()
    wb.remove(wb.active)
    for analysis in analyses:
        sid   = analysis["sid"]
        atype = analysis["type"]
        sname = analysis.get("sheet_name", f"{atype}-{sid}")
        df    = analysis.get("df")
        if atype == "LOSS":
            df = df if isinstance(df, pd.DataFrame) else pd.DataFrame()
            _build_loss_sheet(wb, df, {**meta, "analysis_sid": sid,
                                        "analysis_name": analysis.get("name", sname)})
        elif atype == "HAZ":
            ws_haz = wb.create_sheet(title=sname[:31])
            ws_haz["A1"] = f"Hazard Analysis — SID {sid}"
            ws_haz["A1"].font = Font(name="Calibri", bold=True, size=14, color="1E3A5F")
    _add_model_code_ref(wb)
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output