# sov_upload_pipeline.py — Full SOV upload pipeline
# Orchestrates: validate → create exposure set → upload CSV → poll until complete

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from validate_sov import validate_sov
from create_exposure_set import create_exposure_set
from submit_import_csv import submit_import_csv
from poll_activity import poll_until_complete

def run_sov_pipeline(sov_filepath, exposure_set_name, description=""):
    """
    Full SOV upload pipeline:
    1. Validate the SOV file
    2. Create a new Exposure Set
    3. Upload the CSV
    4. Poll until complete
    """

    print(f"\n{'='*55}")
    print(f"  TOUCHSTONE SOV UPLOAD PIPELINE")
    print(f"{'='*55}")
    print(f"  File : {sov_filepath}")
    print(f"  Name : {exposure_set_name}")
    print(f"{'='*55}")

    # Step 1 — Validate
    print(f"\n[STEP 1] Validating SOV file...")
    is_valid, df = validate_sov(sov_filepath)
    if not is_valid:
        print(f"\n✗ Pipeline stopped — SOV validation failed")
        return False

    # Step 2 — Create Exposure Set
    print(f"\n[STEP 2] Creating Exposure Set...")
    exposure_set_sid = create_exposure_set(exposure_set_name, description)
    if not exposure_set_sid:
        print(f"\n✗ Pipeline stopped — Could not create Exposure Set")
        return False

    # Step 3 — Upload CSV
    print(f"\n[STEP 3] Uploading SOV CSV...")
    activity_sid = submit_import_csv(sov_filepath, exposure_set_sid)
    if not activity_sid:
        print(f"\n✗ Pipeline stopped — CSV upload failed")
        print(f"  Check error messages above for invalid columns")
        return False

    # Step 4 — Poll until complete
    print(f"\n[STEP 4] Waiting for import to complete...")
    success = poll_until_complete(activity_sid)

    print(f"\n{'='*55}")
    if success:
        print(f"  ✓ PIPELINE COMPLETE")
        print(f"  Exposure Set SID : {exposure_set_sid}")
        print(f"  Activity SID     : {activity_sid}")
    else:
        print(f"  ✗ PIPELINE FAILED")
    print(f"{'='*55}\n")

    return success

if __name__ == "__main__":
    # Uncomment when sandbox is confirmed
    # run_sov_pipeline(
    #     sov_filepath="sample_sov.csv",
    #     exposure_set_name="Test_Automation_01",
    #     description="Created by automation pipeline"
    # )
    print("SOV Upload Pipeline ready — awaiting sandbox confirmation to run")