# app.py — Touchstone Automation Dashboard (Redesigned)

import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Touchstone Automation",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ── Global reset ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 2rem 2.5rem 2rem 2.5rem;
    max-width: 1200px;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0D1B2A;
    border-right: 1px solid #1E3448;
}
section[data-testid="stSidebar"] * {
    color: #A8BFCF !important;
}
section[data-testid="stSidebar"] .stRadio label {
    color: #A8BFCF !important;
    font-size: 14px !important;
    padding: 8px 12px !important;
    border-radius: 6px !important;
    transition: all 0.2s !important;
    cursor: pointer !important;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    background: #1E3448 !important;
    color: #E8F4FD !important;
}
section[data-testid="stSidebar"] [data-testid="stRadioLabel"] {
    gap: 0 !important;
}

/* ── Page header ── */
.page-header {
    padding: 1.5rem 0 1rem 0;
    border-bottom: 1px solid #E2EAF4;
    margin-bottom: 1.5rem;
}
.page-header h1 {
    font-size: 1.6rem;
    font-weight: 600;
    color: #0D1B2A;
    margin: 0;
    letter-spacing: -0.02em;
}
.page-header p {
    font-size: 0.875rem;
    color: #6B7E8F;
    margin: 0.25rem 0 0 0;
}

/* ── Cards ── */
.card {
    background: #FFFFFF;
    border: 1px solid #E2EAF4;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(13,27,42,0.04);
}
.card-title {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #6B7E8F;
    margin-bottom: 0.5rem;
}
.card-value {
    font-size: 1.75rem;
    font-weight: 600;
    color: #0D1B2A;
    line-height: 1;
}
.card-sub {
    font-size: 0.8rem;
    color: #6B7E8F;
    margin-top: 0.35rem;
}

/* ── Metric cards ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.metric-card {
    background: #fff;
    border: 1px solid #E2EAF4;
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 1px 3px rgba(13,27,42,0.04);
}
.metric-card .label {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #6B7E8F;
    margin-bottom: 0.4rem;
}
.metric-card .value {
    font-size: 1.1rem;
    font-weight: 600;
    color: #0D1B2A;
}
.metric-card .sub {
    font-size: 0.75rem;
    color: #6B7E8F;
    margin-top: 0.2rem;
}
.metric-card.green { border-left: 3px solid #22C55E; }
.metric-card.blue  { border-left: 3px solid #3B82F6; }
.metric-card.amber { border-left: 3px solid #F59E0B; }
.metric-card.gray  { border-left: 3px solid #CBD5E1; }

/* ── Status badges ── */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
}
.badge-green  { background: #DCFCE7; color: #166534; }
.badge-blue   { background: #DBEAFE; color: #1E40AF; }
.badge-amber  { background: #FEF3C7; color: #92400E; }
.badge-gray   { background: #F1F5F9; color: #475569; }
.badge-red    { background: #FEE2E2; color: #991B1B; }

/* ── Info blocks ── */
.info-row {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}
.info-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.6rem 0.9rem;
    background: #F8FAFC;
    border: 1px solid #E2EAF4;
    border-radius: 7px;
    font-size: 0.85rem;
    color: #374151;
}
.info-item .info-label {
    font-weight: 500;
    color: #6B7E8F;
    min-width: 140px;
    font-size: 0.8rem;
}
.info-item .info-value {
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    color: #0D1B2A;
}

/* ── Section headers ── */
.section-header {
    font-size: 0.85rem;
    font-weight: 600;
    color: #374151;
    margin: 1.25rem 0 0.75rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #F1F5F9;
}

/* ── Buttons ── */
.stButton > button {
    background: #1E40AF !important;
    color: #fff !important;
    border: none !important;
    border-radius: 7px !important;
    padding: 0.5rem 1.25rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em !important;
    transition: all 0.15s !important;
    box-shadow: 0 1px 2px rgba(30,64,175,0.2) !important;
}
.stButton > button:hover {
    background: #1D3FA0 !important;
    box-shadow: 0 3px 8px rgba(30,64,175,0.25) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:disabled {
    background: #CBD5E1 !important;
    color: #94A3B8 !important;
    box-shadow: none !important;
    transform: none !important;
}

/* ── Alerts ── */
.stSuccess > div {
    background: #F0FDF4 !important;
    border: 1px solid #BBF7D0 !important;
    border-radius: 8px !important;
    color: #166534 !important;
}
.stError > div {
    background: #FFF1F2 !important;
    border: 1px solid #FECDD3 !important;
    border-radius: 8px !important;
    color: #9F1239 !important;
}
.stInfo > div {
    background: #EFF6FF !important;
    border: 1px solid #BFDBFE !important;
    border-radius: 8px !important;
    color: #1E40AF !important;
}
.stWarning > div {
    background: #FFFBEB !important;
    border: 1px solid #FDE68A !important;
    border-radius: 8px !important;
    color: #92400E !important;
}

/* ── File table ── */
.file-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.65rem 1rem;
    border-radius: 7px;
    border: 1px solid #E2EAF4;
    margin-bottom: 0.5rem;
    background: #fff;
}
.file-name {
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    color: #374151;
}
.file-size {
    font-size: 0.78rem;
    color: #9CA3AF;
}

/* ── Sidebar logo area ── */
.sidebar-logo {
    padding: 1.5rem 1rem 1rem 1rem;
    border-bottom: 1px solid #1E3448;
    margin-bottom: 0.5rem;
}
.sidebar-logo h2 {
    font-size: 1rem;
    font-weight: 600;
    color: #E8F4FD !important;
    margin: 0;
    letter-spacing: -0.01em;
}
.sidebar-logo p {
    font-size: 0.72rem;
    color: #4A6FA5 !important;
    margin: 0.2rem 0 0 0;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid #E2EAF4;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
    font-weight: 500;
    color: #6B7E8F;
    padding: 0.6rem 1.2rem;
    border-bottom: 2px solid transparent;
}
.stTabs [aria-selected="true"] {
    color: #1E40AF !important;
    border-bottom: 2px solid #1E40AF !important;
}

/* ── Dataframe ── */
.stDataFrame {
    border: 1px solid #E2EAF4 !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}

/* ── Number input ── */
.stNumberInput input {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.9rem !important;
    border-radius: 7px !important;
    border: 1px solid #E2EAF4 !important;
}

/* ── Text input ── */
.stTextInput input {
    border-radius: 7px !important;
    border: 1px solid #E2EAF4 !important;
    font-size: 0.875rem !important;
}

/* ── File uploader ── */
.stFileUploader {
    border: 2px dashed #CBD5E1 !important;
    border-radius: 10px !important;
    padding: 1rem !important;
}

/* ── Divider ── */
hr { border-color: #F1F5F9 !important; }

/* ── Checkbox ── */
.stCheckbox label {
    font-size: 0.875rem !important;
    color: #374151 !important;
}
</style>
""", unsafe_allow_html=True)

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <h2>⚡ Touchstone</h2>
        <p>Automation Platform</p>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "",
        [
            "📊  Dashboard",
            "📁  Exposure Sets",
            "📈  Loss Data",
            "📤  SOV Upload",
            "📄  Reports"
        ],
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='padding: 0.75rem 1rem; background: #1E3448; border-radius: 8px; margin: 0 0.5rem;'>
        <div style='font-size:0.7rem; color:#4A6FA5; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.4rem;'>Environment</div>
        <div style='font-size:0.78rem; color:#A8BFCF;'>crcins-na-prod</div>
        <div style='font-size:0.72rem; color:#4A6FA5; margin-top:0.2rem;'>AIR Cloud • NTLM Auth</div>
    </div>
    """, unsafe_allow_html=True)

# ─── DASHBOARD ────────────────────────────────────────────────────────────────
if page == "📊  Dashboard":
    st.markdown("""
    <div class="page-header">
        <h1>Dashboard</h1>
        <p>Touchstone AIR Cloud automation pipeline overview</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="metric-grid">
        <div class="metric-card green">
            <div class="label">API Connection</div>
            <div class="value">Live</div>
            <div class="sub">NTLM authenticated</div>
        </div>
        <div class="metric-card blue">
            <div class="label">Business Unit</div>
            <div class="value">SID 1</div>
            <div class="sub">DefaultUW — Active</div>
        </div>
        <div class="metric-card blue">
            <div class="label">SQL Instance</div>
            <div class="value">SID 1</div>
            <div class="sub">P19TS1DB01</div>
        </div>
        <div class="metric-card amber">
            <div class="label">Data Source</div>
            <div class="value">SID 2</div>
            <div class="sub">AIRExposure</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown('<div class="section-header">API Configuration</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-row">
            <div class="info-item">
                <span class="info-label">Endpoint</span>
                <span class="info-value">crcins-na-prod-touchstoneapi.air-worldwide.com</span>
            </div>
            <div class="info-item">
                <span class="info-label">Service</span>
                <span class="info-value">FEP/AirServiceFacade.svc</span>
            </div>
            <div class="info-item">
                <span class="info-label">User</span>
                <span class="info-value">automationservice@crcins.air</span>
            </div>
            <div class="info-item">
                <span class="info-label">Authentication</span>
                <span class="info-value">NTLM (Windows)</span>
            </div>
            <div class="info-item">
                <span class="info-label">Protocol</span>
                <span class="info-value">SOAP 1.2 + WS-Addressing</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-header">Output Files</div>', unsafe_allow_html=True)
        output_files = [f for f in os.listdir(".") if f.endswith((".csv", ".xlsx", ".pdf"))]
        if output_files:
            for f in output_files:
                size = os.path.getsize(f)
                size_str = f"{size:,} B" if size < 1024 else f"{size//1024:,} KB"
                st.markdown(f"""
                <div class="file-row">
                    <span class="file-name">📄 {f}</span>
                    <span class="file-size">{size_str}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No output files yet.")

# ─── EXPOSURE SETS ────────────────────────────────────────────────────────────
elif page == "📁  Exposure Sets":
    st.markdown("""
    <div class="page-header">
        <h1>Exposure Sets</h1>
        <p>Retrieve and browse active exposure portfolios from Touchstone</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔄  Fetch from Touchstone"):
            with st.spinner("Connecting to API..."):
                try:
                    import urllib3
                    urllib3.disable_warnings()
                    from extract_exposure_sets import extract_exposure_sets_data
                    df = extract_exposure_sets_data()
                    if df is not None:
                        st.success(f"✓ {len(df)} exposure sets retrieved")
                    else:
                        st.error("No data returned")
                except Exception as e:
                    st.error(f"Failed: {e}")

    if os.path.exists("exposure_sets.xlsx"):
        df = pd.read_excel("exposure_sets.xlsx")
        st.markdown(f"""
        <div class="card">
            <div class="card-title">Total Exposure Sets</div>
            <div class="card-value">{len(df):,}</div>
            <div class="card-sub">Active portfolios in AIRExposure database</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-header">Exposure Set Records</div>', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, height=400)

        col1, col2 = st.columns([1, 4])
        with col1:
            st.download_button(
                "⬇  Download Excel",
                open("exposure_sets.xlsx", "rb").read(),
                "exposure_sets.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info("No exposure sets loaded yet. Click **Fetch from Touchstone** to retrieve data.")

# ─── LOSS DATA ────────────────────────────────────────────────────────────────
elif page == "📈  Loss Data":
    st.markdown("""
    <div class="page-header">
        <h1>Loss Data Extraction</h1>
        <p>Extract ELT, EP curves and loss summaries for completed analyses</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Analysis Configuration</div>', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns([1.5, 1, 1, 1])
        with col1:
            analysis_sid = st.number_input(
                "Analysis SID",
                min_value=1,
                value=63,
                help="Enter the Analysis SID to extract"
            )
        with col2:
            run_elt = st.checkbox("Event Loss Table", value=True)
        with col3:
            run_ep = st.checkbox("EP Curves", value=True)
        with col4:
            run_summary = st.checkbox("Loss Summary", value=True)

        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀  Extract Loss Data"):
        with st.spinner("Extracting data from Touchstone API..."):
            try:
                import urllib3
                urllib3.disable_warnings()
                from extract_loss_data import extract_all_loss_data
                extract_all_loss_data(analysis_sid)
                st.success("✓ Extraction complete — results saved to CSV files below")
            except Exception as e:
                st.error(f"Extraction failed: {e}")

    st.markdown('<div class="section-header">Results</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["Event Loss Table (ELT)", "EP Curves", "Loss Summary"])

    with tab1:
        elt_file = f"elt_{analysis_sid}.csv"
        if os.path.exists(elt_file):
            df = pd.read_csv(elt_file)
            st.markdown(f'<span class="badge badge-green">{len(df)} records</span>', unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True)
            st.download_button("⬇  Download ELT", df.to_csv(index=False), elt_file, "text/csv")
        else:
            st.info("No ELT data available. Run extraction above.")

    with tab2:
        ep_file = f"ep_curves_{analysis_sid}.csv"
        if os.path.exists(ep_file):
            df = pd.read_csv(ep_file)
            st.markdown(f'<span class="badge badge-blue">{len(df)} records</span>', unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True)
            st.download_button("⬇  Download EP Curves", df.to_csv(index=False), ep_file, "text/csv")
        else:
            st.info("No EP Curves data available. Run extraction above.")

    with tab3:
        summary_file = f"loss_summary_{analysis_sid}.csv"
        if os.path.exists(summary_file):
            df = pd.read_csv(summary_file)
            st.markdown(f'<span class="badge badge-amber">{len(df)} records</span>', unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True)
            st.download_button("⬇  Download Summary", df.to_csv(index=False), summary_file, "text/csv")
        else:
            st.info("No Loss Summary data available. Run extraction above.")

# ─── SOV UPLOAD ───────────────────────────────────────────────────────────────
elif page == "📤  SOV Upload":
    st.markdown("""
    <div class="page-header">
        <h1>SOV Upload</h1>
        <p>Validate and upload Statement of Values files to Touchstone</p>
    </div>
    """, unsafe_allow_html=True)

    st.warning("⚠  Sandbox confirmation pending — upload is currently disabled")

    uploaded_file = st.file_uploader(
        "Drop your SOV CSV file here or click to browse",
        type=["csv"],
        help="Statement of Values CSV in Touchstone import format"
    )

    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="card">
                <div class="card-title">Total Rows</div>
                <div class="card-value">{len(df):,}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="card">
                <div class="card-title">Columns</div>
                <div class="card-value">{len(df.columns)}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            null_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100)
            st.markdown(f"""
            <div class="card">
                <div class="card-title">Overall Null %</div>
                <div class="card-value">{null_pct:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="section-header">File Preview</div>', unsafe_allow_html=True)
        st.dataframe(df.head(10), use_container_width=True)

        st.markdown('<div class="section-header">Column Quality</div>', unsafe_allow_html=True)
        col_summary = pd.DataFrame({
            "Column": df.columns,
            "Non-Null": df.count().values,
            "Null %": (df.isnull().mean() * 100).round(1).values,
            "Sample": [str(df[c].dropna().iloc[0]) if df[c].dropna().shape[0] > 0 else "—" for c in df.columns]
        })
        st.dataframe(col_summary, use_container_width=True)

        st.markdown('<div class="section-header">Upload Configuration</div>', unsafe_allow_html=True)
        exposure_set_name = st.text_input(
            "Exposure Set Name",
            placeholder="e.g. ClientName_2026"
        )

        st.button(
            "🚀  Upload to Touchstone",
            disabled=True,
            help="Disabled — awaiting sandbox confirmation"
        )

# ─── REPORTS ──────────────────────────────────────────────────────────────────
elif page == "📄  Reports":
    st.markdown("""
    <div class="page-header">
        <h1>Reports</h1>
        <p>Download generated output files and reports</p>
    </div>
    """, unsafe_allow_html=True)

    st.info("Automated Excel and PDF report generation will be available in Module 5.")

    st.markdown('<div class="section-header">Available Files</div>', unsafe_allow_html=True)
    all_files = [f for f in os.listdir(".") if f.endswith((".csv", ".xlsx", ".pdf"))]

    if all_files:
        for f in all_files:
            size = os.path.getsize(f)
            size_str = f"{size:,} B" if size < 1024 else f"{size//1024:,} KB"
            ext = f.split(".")[-1].upper()
            badge_class = "badge-green" if ext == "CSV" else "badge-blue" if ext == "XLSX" else "badge-red"

            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"""
                <div style="padding:0.5rem 0; border-bottom:1px solid #F1F5F9;">
                    <span style="font-family:'DM Mono',monospace;font-size:0.85rem;color:#374151;">{f}</span>
                    &nbsp;&nbsp;<span class="badge {badge_class}">{ext}</span>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div style="padding:0.5rem 0;font-size:0.8rem;color:#9CA3AF;">{size_str}</div>', unsafe_allow_html=True)
            with col3:
                with open(f, "rb") as file:
                    st.download_button(
                        "⬇ Download",
                        file,
                        f,
                        key=f"dl_{f}"
                    )
    else:
        st.info("No output files available yet. Run an extraction to generate files.")