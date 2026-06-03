# app.py — Touchstone Results Dashboard
# ─────────────────────────────────────────────────────────────────────────────
# Connects to AIRResult SQL database.
# Analysts select a Result SID, preview data, download Excel report.
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

st.set_page_config(
    page_title="Touchstone Results",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem; max-width: 1300px; }

section[data-testid="stSidebar"] {
    background: #0D1B2A;
    border-right: 1px solid #1E3448;
}
section[data-testid="stSidebar"] * { color: #A8BFCF !important; }
section[data-testid="stSidebar"] .stRadio label {
    font-size: 14px !important;
    padding: 8px 12px !important;
    border-radius: 6px !important;
    cursor: pointer !important;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    background: #1E3448 !important;
    color: #E8F4FD !important;
}

.page-header {
    padding: 1.5rem 0 1rem 0;
    border-bottom: 1px solid #E2EAF4;
    margin-bottom: 1.5rem;
}
.page-header h1 { font-size: 1.6rem; font-weight: 600; color: #0D1B2A; margin: 0; }
.page-header p  { font-size: 0.875rem; color: #6B7E8F; margin: 0.25rem 0 0 0; }

.card {
    background: #fff;
    border: 1px solid #E2EAF4;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(13,27,42,0.04);
}
.card-title { font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: #6B7E8F; margin-bottom: 0.5rem; }
.card-value { font-size: 1.75rem; font-weight: 600; color: #0D1B2A; line-height: 1; }
.card-sub   { font-size: 0.8rem; color: #6B7E8F; margin-top: 0.35rem; }

.metric-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1.5rem; }
.metric-card {
    background: #fff;
    border: 1px solid #E2EAF4;
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 1px 3px rgba(13,27,42,0.04);
}
.metric-card.blue  { border-left: 3px solid #3B82F6; }
.metric-card.green { border-left: 3px solid #22C55E; }
.metric-card.amber { border-left: 3px solid #F59E0B; }
.metric-card .label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: #6B7E8F; margin-bottom: 0.4rem; }
.metric-card .value { font-size: 1.5rem; font-weight: 600; color: #0D1B2A; }
.metric-card .sub   { font-size: 0.75rem; color: #6B7E8F; margin-top: 0.2rem; }

.badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 600; }
.badge-green { background: #DCFCE7; color: #166534; }
.badge-blue  { background: #DBEAFE; color: #1E40AF; }
.badge-amber { background: #FEF3C7; color: #92400E; }
.badge-gray  { background: #F1F5F9; color: #475569; }

.sid-card {
    background: #F8FAFC;
    border: 1px solid #E2EAF4;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    cursor: pointer;
    transition: all 0.15s;
    font-family: 'DM Mono', monospace;
    font-size: 0.875rem;
    color: #374151;
}
.sid-card:hover { background: #EFF6FF; border-color: #BFDBFE; }
.sid-card.selected { background: #EFF6FF; border-color: #3B82F6; border-left: 3px solid #3B82F6; }

.section-header {
    font-size: 0.85rem; font-weight: 600; color: #374151;
    margin: 1.25rem 0 0.75rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #F1F5F9;
}

.stButton > button {
    background: #1E40AF !important; color: #fff !important;
    border: none !important; border-radius: 7px !important;
    padding: 0.5rem 1.25rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.875rem !important; font-weight: 500 !important;
}
.stButton > button:hover { background: #1D3FA0 !important; }

.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
    border-radius: 6px 6px 0 0 !important;
    font-size: 0.85rem !important;
    padding: 8px 16px !important;
}
</style>
""", unsafe_allow_html=True)


# ── Sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 1.5rem 1rem 1rem 1rem;">
        <div style="font-size:1.1rem;font-weight:600;color:#E8F4FD;letter-spacing:-0.01em;">
            Touchstone
        </div>
        <div style="font-size:0.75rem;color:#4A6580;margin-top:2px;">
            Results Dashboard
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "",
        ["🏠  Home", "📊  Results", "📋  History"],
        label_visibility="collapsed"
    )

    st.markdown("""
    <div style="position:absolute;bottom:1.5rem;left:1rem;right:1rem;">
        <div style="font-size:0.7rem;color:#2D4559;border-top:1px solid #1E3448;padding-top:0.75rem;">
            AIRResult · P19TS1DB01
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Excel formatter ───────────────────────────────────────────────────────────
def format_sheet(ws):
    """Applies professional formatting to a worksheet"""
    HEADER_BG   = "1F3864"
    HEADER_FONT = "FFFFFF"
    ALT_ROW_BG  = "EAF0FB"
    BORDER_CLR  = "B8CCE4"

    thin = Border(
        left=Side(style="thin", color=BORDER_CLR),
        right=Side(style="thin", color=BORDER_CLR),
        top=Side(style="thin", color=BORDER_CLR),
        bottom=Side(style="thin", color=BORDER_CLR),
    )

    for cell in ws[1]:
        cell.font      = Font(name="Arial", bold=True, color=HEADER_FONT, size=10)
        cell.fill      = PatternFill("solid", fgColor=HEADER_BG)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border    = thin
    ws.row_dimensions[1].height = 30

    for row_idx, row in enumerate(ws.iter_rows(min_row=2), start=2):
        bg = ALT_ROW_BG if row_idx % 2 == 0 else "FFFFFF"
        for cell in row:
            cell.font      = Font(name="Arial", size=9)
            cell.fill      = PatternFill("solid", fgColor=bg)
            cell.alignment = Alignment(horizontal="left", vertical="center")
            cell.border    = thin

    for col_idx, col_cells in enumerate(ws.columns, start=1):
        max_len = max((len(str(c.value)) for c in col_cells if c.value), default=10)
        ws.column_dimensions[get_column_letter(col_idx)].width = min(max_len + 4, 40)

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions


def build_excel_report(result_sid, datasets):
    """
    Builds a formatted Excel workbook from the fetched datasets.
    Returns bytes for download.
    """
    wb = Workbook()

    # Cover sheet
    ws_cover = wb.active
    ws_cover.title = "Summary"
    ws_cover["A1"] = "Touchstone Results Report"
    ws_cover["A1"].font = Font(name="Arial", bold=True, size=16, color="1F3864")
    ws_cover["A3"] = "Result SID"
    ws_cover["B3"] = result_sid
    ws_cover["A4"] = "Generated"
    ws_cover["B4"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws_cover["A6"] = "Sheets"
    row = 7
    for name, df in datasets.items():
        if df is not None and not df.empty:
            ws_cover[f"A{row}"] = f"  • {name}"
            ws_cover[f"B{row}"] = f"{len(df):,} records"
            row += 1

    for col in ["A", "B"]:
        ws_cover.column_dimensions[col].width = 30

    # Data sheets
    for sheet_name, df in datasets.items():
        if df is not None and not df.empty:
            ws = wb.create_sheet(title=sheet_name[:31])
            # Write headers
            for col_idx, col_name in enumerate(df.columns, start=1):
                ws.cell(row=1, column=col_idx, value=col_name)
            # Write data
            for row_idx, row_data in enumerate(df.itertuples(index=False), start=2):
                for col_idx, value in enumerate(row_data, start=1):
                    ws.cell(row=row_idx, column=col_idx, value=value)
            format_sheet(ws)

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()


# ── Log history ───────────────────────────────────────────────────────────────
def log_pull(result_sid, row_counts):
    """Appends a record to pull history in session state"""
    if "history" not in st.session_state:
        st.session_state.history = []
    st.session_state.history.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "result_sid": result_sid,
        "elt_rows": row_counts.get("ELT", 0),
        "ep_rows": row_counts.get("EP Summary", 0),
        "location_rows": row_counts.get("By Location", 0),
    })


# ════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ════════════════════════════════════════════════════════════════════════════
if page == "🏠  Home":
    st.markdown("""
    <div class="page-header">
        <h1>Touchstone Results Dashboard</h1>
        <p>Pull catastrophe model results directly from AIRResult database — no manual SQL required</p>
    </div>
    """, unsafe_allow_html=True)

    # Connection status
    st.markdown('<div class="section-header">System Status</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔌  Test Connection"):
            with st.spinner("Connecting to SQL Server..."):
                try:
                    from db_client import get_connection
                    conn = get_connection()
                    conn.close()
                    st.session_state["db_connected"] = True
                except Exception as e:
                    st.session_state["db_connected"] = False
                    st.session_state["db_error"] = str(e)

    connected = st.session_state.get("db_connected")
    if connected is True:
        st.success("✓ Connected to P19TS1DB01\\PRIMARYSQL2019 — AIRResult database accessible")
    elif connected is False:
        st.error(f"✗ Connection failed — {st.session_state.get('db_error', 'Unknown error')}")
    else:
        st.info("Click **Test Connection** to verify database connectivity")

    # How to use
    st.markdown('<div class="section-header">How to use</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
        <ol style="margin:0;padding-left:1.2rem;font-size:0.875rem;color:#374151;line-height:2;">
            <li>Go to <strong>Results</strong> in the sidebar</li>
            <li>Select a Result SID from the list or type one manually</li>
            <li>Click <strong>Fetch Results</strong></li>
            <li>Preview the data across three tabs</li>
            <li>Click <strong>Download Excel</strong> to get your formatted report</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    # Session stats
    history = st.session_state.get("history", [])
    st.markdown('<div class="section-header">This session</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card blue">
            <div class="label">Reports pulled</div>
            <div class="value">{len(history)}</div>
            <div class="sub">This session</div>
        </div>
        <div class="metric-card green">
            <div class="label">Database</div>
            <div class="value">AIRResult</div>
            <div class="sub">P19TS1DB01</div>
        </div>
        <div class="metric-card amber">
            <div class="label">Server</div>
            <div class="value">PRIMARYSQL2019</div>
            <div class="sub">Windows Auth</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE: RESULTS
# ════════════════════════════════════════════════════════════════════════════
elif page == "📊  Results":
    st.markdown("""
    <div class="page-header">
        <h1>Pull Results</h1>
        <p>Select a Result SID to fetch ELT, EP Summary, and Location data from Touchstone</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Step 1: Select Result SID ─────────────────────────────────────────────
    st.markdown('<div class="section-header">Step 1 — Select Result SID</div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        # Load available SIDs
        if "available_sids" not in st.session_state:
            st.session_state.available_sids = []

        if st.button("🔄  Load Available Result SIDs"):
            with st.spinner("Scanning AIRResult database..."):
                try:
                    from db_client import get_available_result_sids
                    sids = get_available_result_sids()
                    st.session_state.available_sids = sids
                    st.success(f"✓ Found {len(sids)} Result SIDs")
                except Exception as e:
                    st.error(f"Failed: {e}")

        sids = st.session_state.available_sids

        if sids:
            # Searchable selectbox
            selected_sid = st.selectbox(
                "Choose from available Result SIDs",
                options=sids,
                format_func=lambda x: f"Result SID: {x}",
                help="Most recent results shown first"
            )
        else:
            # Manual entry fallback
            selected_sid = st.number_input(
                "Or enter Result SID manually",
                min_value=1,
                value=99002,
                help="Enter the Result SID from Touchstone"
            )
            st.caption("Click **Load Available Result SIDs** to browse all available results")

        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        # Show tables available for selected SID
        if selected_sid:
            st.markdown(f"""
            <div class="card">
                <div class="card-title">Selected Result SID</div>
                <div class="card-value">{selected_sid}</div>
                <div class="card-sub">Tables: t{selected_sid}_LOSS_ByEvent · t{selected_sid}_LOSS_AnnualEPSummary · t{selected_sid}_LOSS_ByLocation</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Step 2: Fetch ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Step 2 — Fetch Results</div>', unsafe_allow_html=True)

    if st.button("🚀  Fetch Results", type="primary"):
        with st.spinner(f"Fetching data for Result SID {selected_sid}..."):
            from db_client import get_loss_by_event, get_loss_annual_ep_summary, get_loss_by_location

            results = {}
            errors  = {}

            # ELT
            try:
                df_elt = get_loss_by_event(selected_sid)
                results["ELT"] = df_elt
            except Exception as e:
                errors["ELT"] = str(e)
                results["ELT"] = pd.DataFrame()

            # EP Summary
            try:
                df_ep = get_loss_annual_ep_summary(selected_sid)
                results["EP Summary"] = df_ep
            except Exception as e:
                errors["EP Summary"] = str(e)
                results["EP Summary"] = pd.DataFrame()

            # By Location
            try:
                df_loc = get_loss_by_location(selected_sid)
                results["By Location"] = df_loc
            except Exception as e:
                errors["By Location"] = str(e)
                results["By Location"] = pd.DataFrame()

            st.session_state["last_results"]    = results
            st.session_state["last_result_sid"] = selected_sid

            # Log it
            log_pull(selected_sid, {k: len(v) for k, v in results.items() if not v.empty})

            if errors:
                for dataset, err in errors.items():
                    st.warning(f"⚠ {dataset}: {err}")

            total = sum(len(v) for v in results.values() if not v.empty)
            if total > 0:
                st.success(f"✓ Fetched {total:,} total records for Result SID {selected_sid}")

    # ── Step 3: Preview & Download ────────────────────────────────────────────
    if "last_results" in st.session_state:
        results    = st.session_state["last_results"]
        result_sid = st.session_state["last_result_sid"]

        st.markdown('<div class="section-header">Step 3 — Preview & Download</div>', unsafe_allow_html=True)

        # Summary metrics
        df_elt = results.get("ELT", pd.DataFrame())
        df_ep  = results.get("EP Summary", pd.DataFrame())
        df_loc = results.get("By Location", pd.DataFrame())

        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-card blue">
                <div class="label">ELT records</div>
                <div class="value">{len(df_elt):,}</div>
                <div class="sub">Loss by event</div>
            </div>
            <div class="metric-card green">
                <div class="label">EP Summary records</div>
                <div class="value">{len(df_ep):,}</div>
                <div class="sub">Annual EP summary</div>
            </div>
            <div class="metric-card amber">
                <div class="label">Location records</div>
                <div class="value">{len(df_loc):,}</div>
                <div class="sub">Loss by location</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Tabs for preview
        tab1, tab2, tab3 = st.tabs([
            f"📋 ELT  ({len(df_elt):,} rows)",
            f"📈 EP Summary  ({len(df_ep):,} rows)",
            f"📍 By Location  ({len(df_loc):,} rows)"
        ])

        with tab1:
            if not df_elt.empty:
                st.markdown(f'<span class="badge badge-blue">{len(df_elt):,} records</span>', unsafe_allow_html=True)
                st.dataframe(df_elt, use_container_width=True, height=400)
            else:
                st.info("No ELT data available for this Result SID")

        with tab2:
            if not df_ep.empty:
                st.markdown(f'<span class="badge badge-green">{len(df_ep):,} records</span>', unsafe_allow_html=True)
                st.dataframe(df_ep, use_container_width=True, height=400)
            else:
                st.info("No EP Summary data available for this Result SID")

        with tab3:
            if not df_loc.empty:
                st.markdown(f'<span class="badge badge-amber">{len(df_loc):,} records</span>', unsafe_allow_html=True)
                st.dataframe(df_loc, use_container_width=True, height=400)
            else:
                st.info("No Location data available for this Result SID")

        # Download
        st.markdown('<div class="section-header">Download Report</div>', unsafe_allow_html=True)

        col1, col2 = st.columns([1, 3])
        with col1:
            has_data = any(not v.empty for v in results.values())
            if has_data:
                excel_bytes = build_excel_report(result_sid, {
                    "ELT":         df_elt,
                    "EP Summary":  df_ep,
                    "By Location": df_loc
                })
                filename = f"Touchstone_Results_{result_sid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                st.download_button(
                    label="⬇  Download Excel Report",
                    data=excel_bytes,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("No data to download")


# ════════════════════════════════════════════════════════════════════════════
# PAGE: HISTORY
# ════════════════════════════════════════════════════════════════════════════
elif page == "📋  History":
    st.markdown("""
    <div class="page-header">
        <h1>Pull History</h1>
        <p>Record of all results fetched this session</p>
    </div>
    """, unsafe_allow_html=True)

    history = st.session_state.get("history", [])

    if history:
        df_history = pd.DataFrame(history)
        df_history.columns = ["Timestamp", "Result SID", "ELT Rows", "EP Rows", "Location Rows"]
        st.dataframe(df_history, use_container_width=True, height=400)

        st.markdown(f"""
        <div class="card">
            <div class="card-title">Session Total</div>
            <div class="card-value">{len(history)}</div>
            <div class="card-sub">Result SIDs pulled this session</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No results pulled yet this session. Go to **Results** to fetch data.")