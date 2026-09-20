import csv
import os
import subprocess
import sys
import uuid
from datetime import datetime


PIPELINE_STEPS = [
    ("Synthetic Data Generation", "src/generate_synthetic_data.py"),
    ("Bronze Ingestion", "src/ingestion/bronze_ingestion.py"),
    ("Data Quality Checks", "src/validation/data_quality.py"),
    ("Silver Transformation", "src/transformation/silver_transformation.py"),
    ("Gold Transformation", "src/transformation/gold_transformation.py"),
    ("SQL Warehouse Load", "src/analytics/load_sql_warehouse.py"),
]


LOG_DIR = "logs"
AUDIT_LOG_PATH = os.path.join(
    LOG_DIR,
    "pipeline_audit.csv",
)

os.makedirs(LOG_DIR, exist_ok=True)

def create_execution_id():
    return str(uuid.uuid4())

def write_audit_log(
    execution_id,
    step_name,
    status,
    start_time,
    end_time,
    duration_seconds,
    error_message="",
):
    file_exists = os.path.exists(
        AUDIT_LOG_PATH
    )

    with open(
        AUDIT_LOG_PATH,
        mode="a",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(
                [
                    "execution_id",
                    "step_name",
                    "status",
                    "start_time",
                    "end_time",
                    "duration_seconds",
                    "error_message",
                ]
            )

        writer.writerow(
            [
                execution_id,
                step_name,
                status,
                start_time,
                end_time,
                duration_seconds,
                error_message,
            ]
        )

def run_step(
    execution_id,
    step_name,
    script_path,
):
    print("\n" + "=" * 60)
    print(f"Starting: {step_name}")
    print("=" * 60)

    start_time = datetime.now()

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
        )

        end_time = datetime.now()

        duration_seconds = (
            end_time - start_time
        ).total_seconds()

        print(result.stdout)

        if result.returncode != 0:
            error_message = result.stderr.strip()

            print(
                f"FAILED: {step_name}"
            )

            print(error_message)

            write_audit_log(
                execution_id,
                step_name,
                "FAILED",
                start_time,
                end_time,
                duration_seconds,
                error_message,
            )

            return False

        write_audit_log(
            execution_id,
            step_name,
            "SUCCESS",
            start_time,
            end_time,
            duration_seconds,
        )

        print(
            f"COMPLETED: {step_name}"
        )

        return True

    except Exception as error:
        end_time = datetime.now()

        duration_seconds = (
            end_time - start_time
        ).total_seconds()

        write_audit_log(
            execution_id,
            step_name,
            "FAILED",
            start_time,
            end_time,
            duration_seconds,
            str(error),
        )

        print(
            f"FAILED: {step_name}"
        )

        print(str(error))

        return False

def main():
    execution_id = create_execution_id()

    print(
        "Starting Healthcare RCM Data Pipeline"
    )

    print(
        f"Execution ID: {execution_id}"
    )

    for step_name, script_path in PIPELINE_STEPS:

        success = run_step(
            execution_id,
            step_name,
            script_path,
        )

        if not success:
            print(
                "\nPipeline stopped due to failure."
            )

            sys.exit(1)

    print("\n" + "=" * 60)
    print(
        "PIPELINE COMPLETED SUCCESSFULLY"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()