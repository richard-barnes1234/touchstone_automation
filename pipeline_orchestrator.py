# pipeline_orchestrator.py — Full automatic pipeline orchestrator

import os
import shutil
import time
import logging
from datetime import datetime

# ─── LOGGING SETUP ────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ─── FOLDERS ──────────────────────────────────────────────
INBOX_FOLDER      = "inbox"
PROCESSING_FOLDER = "processing"
OUTBOX_FOLDER     = "outbox"
FAILED_FOLDER     = "failed"

def move_file(src, dest_folder):
    """Moves a file to a destination folder"""
    filename = os.path.basename(src)
    dest = os.path.join(dest_folder, filename)
    shutil.move(src, dest)
    return dest

def get_sender_from_filename(filename):
    """
    In real mailbox mode this comes from the email.
    For testing we simulate sender from filename prefix.
    e.g. john.doe_ClientSOV.csv → sender = john.doe
    """
    name = os.path.splitext(filename)[0]
    if "_" in name:
        return name.split("_")[0].replace(".", "@", 1) + ".com"
    return "analyst@crcgroup.com"

def send_notification(recipient, subject, body):
    """
    Simulates sending an email notification.
    In production this will use Microsoft Graph API.
    For testing it writes to a notifications log file.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"\n{'='*60}\nTO      : {recipient}\nSUBJECT : {subject}\nTIME    : {timestamp}\n{'-'*60}\n{body}\n{'='*60}\n"
    log.info(f"NOTIFICATION → {recipient} | {subject}")
    with open("notifications.log", "a") as f:
        f.write(msg)

def process_sov_group(csv_files, sender):
    """
    Processes a group of SOV files from one sender.
    Validates all, uploads all, runs models, combines results, generates report.
    """
    log.info(f"Processing {len(csv_files)} SOV file(s) from {sender}")

    # ── STEP 1: VALIDATE ALL FILES ────────────────────────
    log.info("Step 1 — Validating SOV files...")
    from validate_sov import validate_sov

    validation_errors = {}
    valid_files = []

    for f in csv_files:
        log.info(f"  Validating: {os.path.basename(f)}")
        is_valid, df = validate_sov(f)
        if is_valid:
            valid_files.append((f, df))
            log.info(f"  ✓ {os.path.basename(f)} passed validation")
        else:
            validation_errors[os.path.basename(f)] = "File could not be read or is empty"
            log.warning(f"  ✗ {os.path.basename(f)} failed validation")

    if validation_errors:
        error_details = "\n".join([
            f"  • {fname}: {reason}"
            for fname, reason in validation_errors.items()
        ])
        send_notification(
            recipient=sender,
            subject="Touchstone Automation — SOV Validation Failed",
            body=f"Hi,\n\nWe received your SOV file(s) but found the following issues:\n\n{error_details}\n\nPlease fix the issues and resubmit.\n\nTouchstone Automation"
        )
        log.warning("Validation failed — pipeline stopped. Sender notified.")
        return False

    log.info(f"  ✓ All {len(valid_files)} file(s) passed validation")

    # ── STEP 2: UPLOAD TO TOUCHSTONE ──────────────────────
    log.info("Step 2 — Uploading SOV files to Touchstone...")
    exposure_set_sids = []

    for filepath, df in valid_files:
        filename = os.path.basename(filepath)
        set_name = f"AUTO_{os.path.splitext(filename)[0]}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        log.info(f"  Creating exposure set: {set_name}")

        # ── SANDBOX GUARD ──
        # Uncomment when sandbox is confirmed:
        # from create_exposure_set import create_exposure_set
        # from submit_import_csv import submit_import_csv
        # from poll_activity import poll_until_complete
        # sid = create_exposure_set(set_name)
        # if not sid:
        #     log.error(f"Failed to create exposure set for {filename}")
        #     continue
        # activity_sid = submit_import_csv(filepath, sid)
        # poll_until_complete(activity_sid)
        # exposure_set_sids.append(sid)

        # SIMULATION for testing:
        simulated_sid = str(hash(set_name) % 99999)
        exposure_set_sids.append(simulated_sid)
        log.info(f"  [SIMULATED] Exposure Set SID: {simulated_sid}")

    log.info(f"  ✓ {len(exposure_set_sids)} exposure set(s) ready")

    # ── STEP 3: RUN MODELS ────────────────────────────────
    log.info("Step 3 — Triggering catastrophe model runs...")
    analysis_sids = []

    for sid in exposure_set_sids:
        log.info(f"  Submitting analysis for ExposureSetSid: {sid}")

        # ── SANDBOX GUARD ──
        # Uncomment when sandbox is confirmed:
        # analysis_sid = submit_detailed_loss_analysis(sid)
        # analysis_sids.append(analysis_sid)

        # SIMULATION for testing:
        simulated_analysis_sid = 63  # use our known working SID
        analysis_sids.append(simulated_analysis_sid)
        log.info(f"  [SIMULATED] Analysis SID: {simulated_analysis_sid}")

    log.info(f"  ✓ {len(analysis_sids)} model run(s) submitted")

    # ── STEP 4: POLL UNTIL COMPLETE ───────────────────────
    log.info("Step 4 — Waiting for model runs to complete...")

    # ── SANDBOX GUARD ──
    # In production poll each analysis_sid here
    # For testing simulate completion
    log.info("  [SIMULATED] All model runs complete")

    # ── STEP 5: EXTRACT RESULTS ───────────────────────────
    log.info("Step 5 — Extracting results from Touchstone...")
    import pandas as pd
    from extract_loss_data import (
        parse_event_results,
        parse_annual_results,
        parse_summary_results
    )
    from api_client import send_soap_request
    from soap_templates import (
        get_loss_analysis_event_results,
        get_loss_analysis_annual_results,
        get_loss_analysis_summary_results
    )
    from config import BUSINESS_UNIT_SID, SQL_INSTANCE_SID

    all_elts     = []
    all_ep       = []
    all_summaries = []

    for analysis_sid in analysis_sids:
        log.info(f"  Pulling results for AnalysisSid: {analysis_sid}")

        resp = send_soap_request(
            get_loss_analysis_event_results(BUSINESS_UNIT_SID, SQL_INSTANCE_SID, analysis_sid)
        )
        if resp.status_code == 200:
            df = parse_event_results(resp.text)
            df["AnalysisSid"] = analysis_sid
            all_elts.append(df)
            log.info(f"  ✓ ELT: {len(df)} records")

        resp = send_soap_request(
            get_loss_analysis_annual_results(BUSINESS_UNIT_SID, SQL_INSTANCE_SID, analysis_sid)
        )
        if resp.status_code == 200:
            df = parse_annual_results(resp.text)
            df["AnalysisSid"] = analysis_sid
            all_ep.append(df)
            log.info(f"  ✓ EP Curves: {len(df)} records")

        resp = send_soap_request(
            get_loss_analysis_summary_results(BUSINESS_UNIT_SID, SQL_INSTANCE_SID, analysis_sid)
        )
        if resp.status_code == 200:
            df = parse_summary_results(resp.text)
            df["AnalysisSid"] = analysis_sid
            all_summaries.append(df)
            log.info(f"  ✓ Loss Summary: {len(df)} records")

    # ── STEP 6: COMBINE RESULTS ───────────────────────────
    log.info("Step 6 — Combining results...")
    df_elt     = pd.concat(all_elts,      ignore_index=True) if all_elts      else pd.DataFrame()
    df_ep      = pd.concat(all_ep,        ignore_index=True) if all_ep        else pd.DataFrame()
    df_summary = pd.concat(all_summaries, ignore_index=True) if all_summaries else pd.DataFrame()
    log.info(f"  ✓ ELT combined      : {len(df_elt)} records")
    log.info(f"  ✓ EP combined       : {len(df_ep)} records")
    log.info(f"  ✓ Summary combined  : {len(df_summary)} records")

    # ── STEP 7: GENERATE REPORT ───────────────────────────
    log.info("Step 7 — Generating report...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_name = f"TouchstoneReport_{timestamp}"
    report_path = os.path.join(OUTBOX_FOLDER, f"{report_name}.xlsx")

    with pd.ExcelWriter(report_path, engine="openpyxl") as writer:
        if not df_elt.empty:
            df_elt.to_excel(writer, sheet_name="ELT", index=False)
        if not df_ep.empty:
            df_ep.to_excel(writer, sheet_name="EP Curves", index=False)
        if not df_summary.empty:
            df_summary.to_excel(writer, sheet_name="Loss Summary", index=False)

    log.info(f"  ✓ Report saved: {report_path}")

    # ── STEP 8: NOTIFY SENDER ────────────────────────────
    sov_list = "\n".join([f"  • {os.path.basename(f)}" for f, _ in valid_files])
    send_notification(
        recipient=sender,
        subject="Touchstone Automation — Your Report is Ready",
        body=f"Hi,\n\nYour Touchstone report has been generated successfully.\n\nSOV files processed:\n{sov_list}\n\nReport: {report_name}.xlsx\n\nThis report includes:\n  • Event Loss Table (ELT)\n  • EP Curves\n  • Loss Summary\n\nTouchstone Automation"
    )

    log.info("Pipeline complete!")
    return True

def process_inbox():
    """Scans inbox folder and processes any CSV files found"""
    csv_files = [
        os.path.join(INBOX_FOLDER, f)
        for f in os.listdir(INBOX_FOLDER)
        if f.lower().endswith(".csv")
    ]

    if not csv_files:
        return

    log.info(f"Found {len(csv_files)} CSV file(s) in inbox")

    # Move all to processing
    processing_files = []
    for f in csv_files:
        dest = move_file(f, PROCESSING_FOLDER)
        processing_files.append(dest)
        log.info(f"  Moved to processing: {os.path.basename(dest)}")

    # Get sender from first file (in mailbox mode this comes from email)
    sender = get_sender_from_filename(os.path.basename(processing_files[0]))
    log.info(f"  Sender: {sender}")

    # Run pipeline
    success = process_sov_group(processing_files, sender)

    # Move processed files to outbox or failed
    dest_folder = OUTBOX_FOLDER if success else FAILED_FOLDER
    for f in processing_files:
        if os.path.exists(f):
            move_file(f, dest_folder)

def run_watcher(interval=15):
    """Watches inbox folder every N seconds"""
    log.info("="*60)
    log.info("  TOUCHSTONE AUTOMATION PIPELINE — STARTED")
    log.info(f"  Watching folder: {os.path.abspath(INBOX_FOLDER)}")
    log.info(f"  Checking every {interval} seconds")
    log.info("="*60)

    while True:
        try:
            process_inbox()
        except Exception as e:
            log.error(f"Pipeline error: {e}")
        time.sleep(interval)

if __name__ == "__main__":
    run_watcher(interval=15)