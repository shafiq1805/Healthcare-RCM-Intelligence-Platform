import os

import pandas as pd


BRONZE_DATA_DIR = os.path.join(
    "data",
    "bronze",
)

SILVER_DATA_DIR = os.path.join(
    "data",
    "silver",
)

os.makedirs(
    SILVER_DATA_DIR,
    exist_ok=True,
)

def standardize_columns(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
    )

    return df

def clean_string_columns(df):
    string_columns = df.select_dtypes(
        include=["object","string"]
    ).columns

    for column in string_columns:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )

    return df

def transform_patients(df):
    df = standardize_columns(df)
    df = clean_string_columns(df)

    df["patient_id"] = (
        df["patient_id"]
        .str.upper()
    )

    df["gender"] = (
        df["gender"]
        .str.upper()
    )

    df["date_of_birth"] = pd.to_datetime(
        df["date_of_birth"],
        errors="coerce",
    )

    df["zip_code"] = (
        df["zip_code"]
        .astype("string")
        .str.strip()
    )

    return df

def transform_providers(df):
    df = standardize_columns(df)
    df = clean_string_columns(df)

    df["provider_id"] = (
        df["provider_id"]
        .str.upper()
    )

    df["npi"] = (
        df["npi"]
        .astype("string")
        .str.strip()
    )

    return df

def transform_encounters(df):
    df = standardize_columns(df)
    df = clean_string_columns(df)

    df["encounter_id"] = (
        df["encounter_id"]
        .str.upper()
    )

    df["patient_id"] = (
        df["patient_id"]
        .str.upper()
    )

    df["provider_id"] = (
        df["provider_id"]
        .str.upper()
    )

    df["encounter_type"] = (
        df["encounter_type"]
        .str.upper()
    )

    df["primary_diagnosis"] = (
        df["primary_diagnosis"]
        .str.upper()
    )

    df["encounter_date"] = pd.to_datetime(
        df["encounter_date"],
        errors="coerce",
    )

    df["discharge_date"] = pd.to_datetime(
        df["discharge_date"],
        errors="coerce",
    )

    return df

def transform_claims(df):
    df = standardize_columns(df)
    df = clean_string_columns(df)

    df["claim_id"] = (
        df["claim_id"]
        .str.upper()
    )

    df["patient_id"] = (
        df["patient_id"]
        .str.upper()
    )

    df["encounter_id"] = (
        df["encounter_id"]
        .str.upper()
    )

    df["provider_id"] = (
        df["provider_id"]
        .str.upper()
    )

    df["claim_status"] = (
        df["claim_status"]
        .str.upper()
    )

    df["claim_date"] = pd.to_datetime(
        df["claim_date"],
        errors="coerce",
    )

    df["submission_date"] = pd.to_datetime(
        df["submission_date"],
        errors="coerce",
    )

    df["claim_amount"] = pd.to_numeric(
        df["claim_amount"],
        errors="coerce",
    )

    return df

def transform_claim_lines(df):
    df = standardize_columns(df)
    df = clean_string_columns(df)

    df["claim_line_id"] = (
        df["claim_line_id"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    df["claim_id"] = (
        df["claim_id"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    df["procedure_code"] = (
        df["procedure_code"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    df["diagnosis_code"] = (
        df["diagnosis_code"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    numeric_columns = [
        "units",
        "charge_amount",
        "allowed_amount",
        "paid_amount",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    return df

def transform_clinical_notes(df):
    df = standardize_columns(df)
    df = clean_string_columns(df)

    df["note_id"] = (
        df["note_id"]
        .str.upper()
    )

    df["encounter_id"] = (
        df["encounter_id"]
        .str.upper()
    )

    df["patient_id"] = (
        df["patient_id"]
        .str.upper()
    )

    df["provider_id"] = (
        df["provider_id"]
        .str.upper()
    )

    df["note_date"] = pd.to_datetime(
        df["note_date"],
        errors="coerce",
    )

    return df

def transform_denials(df):
    df = standardize_columns(df)
    df = clean_string_columns(df)

    df["denial_id"] = (
        df["denial_id"]
        .str.upper()
    )

    df["claim_id"] = (
        df["claim_id"]
        .str.upper()
    )

    df["denial_code"] = (
        df["denial_code"]
        .str.upper()
    )

    df["appeal_status"] = (
        df["appeal_status"]
        .str.upper()
    )

    df["denial_date"] = pd.to_datetime(
        df["denial_date"],
        errors="coerce",
    )

    return df

def transform_denials(df):
    df = standardize_columns(df)
    df = clean_string_columns(df)

    df["denial_id"] = (
        df["denial_id"]
        .str.upper()
    )

    df["claim_id"] = (
        df["claim_id"]
        .str.upper()
    )

    df["denial_code"] = (
        df["denial_code"]
        .str.upper()
    )

    df["appeal_status"] = (
        df["appeal_status"]
        .str.upper()
    )

    df["denial_date"] = pd.to_datetime(
        df["denial_date"],
        errors="coerce",
    )

    return df

TRANSFORMATIONS = {
    "patients.csv": transform_patients,
    "providers.csv": transform_providers,
    "encounters.csv": transform_encounters,
    "claims.csv": transform_claims,
    "claim_lines.csv": transform_claim_lines,
    "clinical_notes.csv": transform_clinical_notes,
    "denials.csv": transform_denials,
}

def transform_file(
    file_name,
    transformation_function,
):
    input_path = os.path.join(
        BRONZE_DATA_DIR,
        file_name,
    )

    output_path = os.path.join(
        SILVER_DATA_DIR,
        file_name,
    )

    df = pd.read_csv(input_path)

    transformed_df = (
        transformation_function(df)
    )

    transformed_df.to_csv(
        output_path,
        index=False,
    )

    print(
        f"Transformed {file_name}: "
        f"{len(transformed_df)} rows"
    )

def main():
    print(
        "Starting Bronze to Silver transformation..."
    )

    for (
        file_name,
        transformation_function,
    ) in TRANSFORMATIONS.items():

        transform_file(
            file_name,
            transformation_function,
        )

    print(
        "Silver transformation completed successfully."
    )


if __name__ == "__main__":
    main()