# app.py — Touchstone Automation Dashboard

import streamlit as st
import pandas as pd
import os

# Page config
st.set_page_config(
    page_title="Touchstone Automation",
    page_icon="🏢",
    layout="wide"
)

# Header
st.title("🏢 Touchstone AIR Cloud Automation")
st.markdown("**Automated data extraction and reporting pipeline**")
st.divider()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    [
        "📊 Dashboard",
        "📁 Exposure Sets",
        "📈 Loss Data Extraction",
        "📤 SOV Upload",
        "📄 Reports"
    ]
)

# ─── DASHBOARD PAGE ───────────────────────────────────────
if page == "📊 Dashboard":
    st.header("📊 Dashboard")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Module 1", "Complete ✅", "API Connected")
    with col2:
        st.metric("Module 2", "In Progress 🔄", "Data Extraction")
    with col3:
        st.metric("Module 3", "Up Next ⏳", "Data Parsing")
    with col4:
        st.metric("Module 4-7", "Pending ⏸", "Reports & Deploy")

    st.divider()

    st.subheader("API Connection Status")
    col1, col2 = st.columns(2)
    with col1:
        st.info("🔗 **Endpoint:** crcins-na-prod-touchstoneapi.air-worldwide.com")
        st.info("👤 **User:** automationservice")
        st.info("🔐 **Auth:** NTLM")

    with col2:
        st.info("🏢 **Business Unit SID:** 1")
        st.info("🗄 **SQL Instance SID:** 1")
        st.info("📂 **Data Source SID:** 2 (AIRExposure)")

    st.divider()

    st.subheader("Recent Output Files")
    output_files = [f for f in os.listdir(".") if f.endswith(".csv") or f.endswith(".xlsx")]
    if output_files:
        for f in output_files:
            size = os.path.getsize(f)
            st.write(f"📄 `{f}` — {size} bytes")
    else:
        st.write("No output files yet.")

# ─── EXPOSURE SETS PAGE ───────────────────────────────────
elif page == "📁 Exposure Sets":
    st.header("📁 Exposure Sets")

    if st.button("🔄 Fetch Exposure Sets from Touchstone"):
        with st.spinner("Connecting to Touchstone API..."):
            try:
                import urllib3
                urllib3.disable_warnings()
                from extract_exposure_sets import extract_exposure_sets_data
                st.success("✓ Connected successfully!")
            except Exception as e:
                st.error(f"Connection failed: {e}")

    # Show existing CSV if available
    if os.path.exists("exposure_sets.csv"):
        st.subheader("Loaded Exposure Sets")
        df = pd.read_csv("exposure_sets.csv")
        st.write(f"**{len(df)} exposure sets found**")
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "⬇ Download CSV",
            df.to_csv(index=False),
            "exposure_sets.csv",
            "text/csv"
        )
    else:
        st.info("No exposure sets loaded yet. Click the button above to fetch.")

# ─── LOSS DATA PAGE ───────────────────────────────────────
elif page == "📈 Loss Data Extraction":
    st.header("📈 Loss Data Extraction")

    st.subheader("Select Analysis")
    analysis_sid = st.number_input(
        "Analysis SID",
        min_value=1,
        value=63,
        help="Enter the Analysis SID to extract loss data for"
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        run_elt = st.checkbox("Event Loss Table (ELT)", value=True)
    with col2:
        run_ep = st.checkbox("EP Curves", value=True)
    with col3:
        run_summary = st.checkbox("Loss Summary", value=True)

    if st.button("🚀 Extract Loss Data"):
        with st.spinner("Extracting data from Touchstone..."):
            try:
                import urllib3
                urllib3.disable_warnings()
                from extract_loss_data import extract_all_loss_data
                extract_all_loss_data(analysis_sid)
                st.success("✓ Extraction complete!")
            except Exception as e:
                st.error(f"Extraction failed: {e}")

    st.divider()
    st.subheader("Extracted Results")

    tab1, tab2, tab3 = st.tabs(["ELT", "EP Curves", "Loss Summary"])

    with tab1:
        elt_file = f"elt_{analysis_sid}.csv"
        if os.path.exists(elt_file):
            df = pd.read_csv(elt_file)
            st.write(f"**{len(df)} records**")
            st.dataframe(df, use_container_width=True)
            st.download_button("⬇ Download ELT", df.to_csv(index=False), elt_file, "text/csv")
        else:
            st.info("No ELT data loaded yet.")

    with tab2:
        ep_file = f"ep_curves_{analysis_sid}.csv"
        if os.path.exists(ep_file):
            df = pd.read_csv(ep_file)
            st.write(f"**{len(df)} records**")
            st.dataframe(df, use_container_width=True)
            st.download_button("⬇ Download EP Curves", df.to_csv(index=False), ep_file, "text/csv")
        else:
            st.info("No EP Curves data loaded yet.")

    with tab3:
        summary_file = f"loss_summary_{analysis_sid}.csv"
        if os.path.exists(summary_file):
            df = pd.read_csv(summary_file)
            st.write(f"**{len(df)} records**")
            st.dataframe(df, use_container_width=True)
            st.download_button("⬇ Download Summary", df.to_csv(index=False), summary_file, "text/csv")
        else:
            st.info("No Loss Summary data loaded yet.")

# ─── SOV UPLOAD PAGE ──────────────────────────────────────
elif page == "📤 SOV Upload":
    st.header("📤 SOV Upload")

    st.warning("⚠ Sandbox confirmation pending — upload is disabled until confirmed.")

    st.subheader("Upload SOV File")
    uploaded_file = st.file_uploader(
        "Choose a SOV CSV file",
        type=["csv"],
        help="Upload your Statement of Values CSV file"
    )

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.success(f"✓ File loaded — {len(df)} rows, {len(df.columns)} columns")

        st.subheader("File Preview")
        st.dataframe(df.head(10), use_container_width=True)

        st.subheader("Column Summary")
        col_summary = pd.DataFrame({
            "Column": df.columns,
            "Non-Null Count": df.count().values,
            "Null %": (df.isnull().mean() * 100).round(1).values,
            "Sample Value": [str(df[c].dropna().iloc[0]) if df[c].dropna().shape[0] > 0 else "N/A" for c in df.columns]
        })
        st.dataframe(col_summary, use_container_width=True)

        exposure_set_name = st.text_input(
            "Exposure Set Name",
            placeholder="e.g. TestClient_2026"
        )

        st.button(
            "🚀 Upload to Touchstone",
            disabled=True,
            help="Disabled — awaiting sandbox confirmation"
        )

# ─── REPORTS PAGE ─────────────────────────────────────────
elif page == "📄 Reports":
    st.header("📄 Reports")
    st.info("Report generation will be available in Module 5.")

    st.subheader("Available Output Files")
    all_files = [f for f in os.listdir(".") if f.endswith((".csv", ".xlsx", ".pdf"))]
    if all_files:
        for f in all_files:
            size = os.path.getsize(f)
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📄 `{f}` — {size:,} bytes")
            with col2:
                with open(f, "rb") as file:
                    st.download_button(
                        "⬇ Download",
                        file,
                        f,
                        key=f
                    )
    else:
        st.info("No output files available yet.")