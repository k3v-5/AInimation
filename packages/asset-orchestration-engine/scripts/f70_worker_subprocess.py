import sys
import os
import time
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.long_running_job_recovery import (
    LongRunningJobAPI, JobType, JobState, JobPriority
)

def run_worker():
    parser = argparse.ArgumentParser()
    parser.add_argument("--job-id", type=str, required=True)
    parser.add_argument("--storage-dir", type=str, required=True)
    parser.add_argument("--crash-at", type=str, default="NONE")
    parser.add_argument("--resume-from-checkpoint", type=str, default="")
    args = parser.parse_args()

    api = LongRunningJobAPI(storage_dir=args.storage_dir)
    job = api._service.store.get_job(args.job_id)
    if not job:
        job = api.create_and_start_job(
            job_type=JobType.FULL_PIPELINE,
            asset_id="F70_Recovery_Test_Asset",
            semantic_id="f70.recovery.test.asset",
            worker_id="SUBPROCESS_WORKER_01",
            job_id=args.job_id
        )

    # Step 1: Workspace setup
    if not args.resume_from_checkpoint or args.resume_from_checkpoint in ["NONE"]:
        time.sleep(0.05)
        api.create_checkpoint(args.job_id, "INIT", "CP1_WORKSPACE", "HASH_CP1", progress_percent=10.0)

    # Step 2 & 3: Base Geometry
    if not args.resume_from_checkpoint or args.resume_from_checkpoint in ["NONE", "CP1_WORKSPACE"]:
        time.sleep(0.05)
        api.create_checkpoint(args.job_id, "GEOMETRY", "CP2_BASE_GEOMETRY", "HASH_CP2", progress_percent=30.0)

    # Step 4, 5, 6: Components, Modifier, Material
    if not args.resume_from_checkpoint or args.resume_from_checkpoint in ["NONE", "CP1_WORKSPACE", "CP2_BASE_GEOMETRY"]:
        time.sleep(0.05)
        api.create_checkpoint(args.job_id, "MATERIAL", "CP3_MATERIAL_CREATED", "HASH_CP3", progress_percent=55.0)
        sys.stdout.write("CHECKPOINT_CP3_CONFIRMED\n")
        sys.stdout.flush()

        if args.crash_at == "CP3":
            # Signal parent and hang in infinite loop so parent kills it abruptly
            while True:
                time.sleep(0.1)

    # Step 7 & 8: State Save & Validation
    if not args.resume_from_checkpoint or args.resume_from_checkpoint in ["NONE", "CP1_WORKSPACE", "CP2_BASE_GEOMETRY", "CP3_MATERIAL_CREATED"]:
        time.sleep(0.05)
        api.create_checkpoint(args.job_id, "VALIDATION", "CP4_ASSET_VALIDATED", "HASH_CP4", progress_percent=75.0)

    # Step 9 & 10: Output Generation
    if not args.resume_from_checkpoint or args.resume_from_checkpoint in ["NONE", "CP1_WORKSPACE", "CP2_BASE_GEOMETRY", "CP3_MATERIAL_CREATED", "CP4_ASSET_VALIDATED"]:
        time.sleep(0.05)
        api.create_checkpoint(args.job_id, "OUTPUT", "CP5_OUTPUT_GENERATED", "HASH_CP5", progress_percent=90.0)

    # Step 11: Final Commit & Complete
    api.create_checkpoint(args.job_id, "COMMIT", "CP6_COMMITTED", "HASH_CP6", progress_percent=100.0)
    api.complete_job(args.job_id)
    sys.stdout.write("JOB_EXECUTION_COMPLETED_SUCCESSFULLY\n")
    sys.stdout.flush()

if __name__ == "__main__":
    run_worker()
