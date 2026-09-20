import os
import pandas as pd
import sys


BRONZE_DATA_DIR = os.path.join("data", "bronze")

def create_result(
    table_name,
    check_name,
    status,
    failed_records,
):
    return {
        "table_name": table_name,
        "check_name": check_name,
        "status": status,
        "failed_records": failed_records,
    }

def check_null_primary_key(
    df,
    table_name,
    primary_key,
):
    failed_count = df[primary_key].isna().sum()

    status = (
        "PASS"
        if failed_count == 0
        else "FAIL"
    )

    return create_result(
        table_name,
        f"null_{primary_key}",
        status,
        int(failed_count),
    )

def check_duplicate_primary_key(
    df,
    table_name,
    primary_key,
):
    failed_count = df[
        df.duplicated(
            subset=[primary_key],
            keep=False,
        )
    ].shape[0]

    status = (
        "PASS"
        if failed_count == 0
        else "FAIL"
    )

    return create_result(
        table_name,
        f"duplicate_{primary_key}",
        status,
        failed_count,
    )

def check_valid_date(
    df,
    table_name,
    column_name,
):
    converted = pd.to_datetime(
        df[column_name],
        errors="coerce",
    )

    failed_count = (
        converted.isna()
        & df[column_name].notna()
    ).sum()

    status = (
        "PASS"
        if failed_count == 0
        else "FAIL"
    )

    return create_result(
        table_name,
        f"invalid_date_{column_name}",
        status,
        int(failed_count),
    )
def check_non_negative(
    df,
    table_name,
    column_name,
):
    failed_count = (
        pd.to_numeric(
            df[column_name],
            errors="coerce",
        )
        < 0
    ).sum()

    status = (
        "PASS"
        if failed_count == 0
        else "FAIL"
    )

    return create_result(
        table_name,
        f"negative_{column_name}",
        status,
        int(failed_count),
    )
def check_allowed_values(
    df,
    table_name,
    column_name,
    allowed_values,
):
    failed_count = (
        ~df[column_name].isin(
            allowed_values
        )
        & df[column_name].notna()
    ).sum()

    status = (
        "PASS"
        if failed_count == 0
        else "FAIL"
    )

    return create_result(
        table_name,
        f"invalid_{column_name}",
        status,
        int(failed_count),
    )
VALID_CLAIM_STATUSES = [
    "SUBMITTED",
    "PENDING",
    "PAID",
    "DENIED",
]
def check_foreign_key(
    child_df,
    parent_df,
    table_name,
    child_column,
    parent_column,
):
    failed_count = (
        ~child_df[child_column].isin(
            parent_df[parent_column]
        )
        & child_df[child_column].notna()
    ).sum()

    status = (
        "PASS"
        if failed_count == 0
        else "FAIL"
    )

    return create_result(
        table_name,
        f"invalid_fk_{child_column}",
        status,
        int(failed_count),
    )

def load_bronze_data():
    patients_df = pd.read_csv(
        os.path.join(
            BRONZE_DATA_DIR,
            "patients.csv",
        )
    )

    providers_df = pd.read_csv(
        os.path.join(
            BRONZE_DATA_DIR,
            "providers.csv",
        )
    )

    encounters_df = pd.read_csv(
        os.path.join(
            BRONZE_DATA_DIR,
            "encounters.csv",
        )
    )

    claims_df = pd.read_csv(
        os.path.join(
            BRONZE_DATA_DIR,
            "claims.csv",
        )
    )

    claim_lines_df = pd.read_csv(
        os.path.join(
            BRONZE_DATA_DIR,
            "claim_lines.csv",
        )
    )

    clinical_notes_df = pd.read_csv(
        os.path.join(
            BRONZE_DATA_DIR,
            "clinical_notes.csv",
        )
    )

    denials_df = pd.read_csv(
        os.path.join(
            BRONZE_DATA_DIR,
            "denials.csv",
        )
    )

    return {
        "patients": patients_df,
        "providers": providers_df,
        "encounters": encounters_df,
        "claims": claims_df,
        "claim_lines": claim_lines_df,
        "clinical_notes": clinical_notes_df,
        "denials": denials_df,
    }

def run_quality_checks(data):
    results = []

    patients = data["patients"]
    providers = data["providers"]
    encounters = data["encounters"]
    claims = data["claims"]
    claim_lines = data["claim_lines"]
    clinical_notes = data["clinical_notes"]
    denials = data["denials"]

    # Primary key checks
    results.append(
        check_null_primary_key(
            patients,
            "patients",
            "patient_id",
        )
    )

    results.append(
        check_duplicate_primary_key(
            patients,
            "patients",
            "patient_id",
        )
    )

    results.append(
        check_null_primary_key(
            providers,
            "providers",
            "provider_id",
        )
    )

    results.append(
        check_duplicate_primary_key(
            providers,
            "providers",
            "provider_id",
        )
    )

    results.append(
        check_null_primary_key(
            claims,
            "claims",
            "claim_id",
        )
    )

    results.append(
        check_duplicate_primary_key(
            claims,
            "claims",
            "claim_id",
        )
    )

    # Date checks
    results.append(
        check_valid_date(
            patients,
            "patients",
            "date_of_birth",
        )
    )

    results.append(
        check_valid_date(
            encounters,
            "encounters",
            "encounter_date",
        )
    )

    results.append(
        check_valid_date(
            claims,
            "claims",
            "claim_date",
        )
    )

    results.append(
        check_valid_date(
            claims,
            "claims",
            "submission_date",
        )
    )

    # Monetary checks
    results.append(
        check_non_negative(
            claims,
            "claims",
            "claim_amount",
        )
    )

    results.append(
        check_non_negative(
            claim_lines,
            "claim_lines",
            "charge_amount",
        )
    )

    results.append(
        check_non_negative(
            claim_lines,
            "claim_lines",
            "allowed_amount",
        )
    )

    results.append(
        check_non_negative(
            claim_lines,
            "claim_lines",
            "paid_amount",
        )
    )

    # Claim status
    results.append(
        check_allowed_values(
            claims,
            "claims",
            "claim_status",
            [
                "SUBMITTED",
                "PENDING",
                "PAID",
                "DENIED",
            ],
        )
    )

    # Foreign keys
    results.append(
        check_foreign_key(
            encounters,
            patients,
            "encounters",
            "patient_id",
            "patient_id",
        )
    )

    results.append(
        check_foreign_key(
            encounters,
            providers,
            "encounters",
            "provider_id",
            "provider_id",
        )
    )

    results.append(
        check_foreign_key(
            claims,
            patients,
            "claims",
            "patient_id",
            "patient_id",
        )
    )

    results.append(
        check_foreign_key(
            claims,
            encounters,
            "claims",
            "encounter_id",
            "encounter_id",
        )
    )

    results.append(
        check_foreign_key(
            claim_lines,
            claims,
            "claim_lines",
            "claim_id",
            "claim_id",
        )
    )

    results.append(
        check_foreign_key(
            clinical_notes,
            encounters,
            "clinical_notes",
            "encounter_id",
            "encounter_id",
        )
    )

    results.append(
        check_foreign_key(
            denials,
            claims,
            "denials",
            "claim_id",
            "claim_id",
        )
    )

    return pd.DataFrame(results)

def main():
    print("Starting data quality checks...")

    data = load_bronze_data()

    results_df = run_quality_checks(data)

    print()
    print(results_df.to_string(index=False))

    failed_checks = results_df[
        results_df["status"] == "FAIL"
    ]

    print()

    if failed_checks.empty:
        print(
            "All data quality checks passed."
        )
    else:
        print(
            f"{len(failed_checks)} data quality checks failed."
        )

        sys.exit(1)


if __name__ == "__main__":
    main()
    