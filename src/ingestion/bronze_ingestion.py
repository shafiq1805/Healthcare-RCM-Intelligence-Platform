import os
from datetime import datetime

import pandas as pd


RAW_DATA_DIR = os.path.join("data", "raw")
BRONZE_DATA_DIR = os.path.join("data", "bronze")

os.makedirs(BRONZE_DATA_DIR, exist_ok=True)


SOURCE_FILES = [
    "patients.csv",
    "providers.csv",
    "encounters.csv",
    "claims.csv",
    "claim_lines.csv",
    "clinical_notes.csv",
    "denials.csv",
]


def create_batch_id():
    return datetime.now().strftime(
        "BATCH_%Y%m%d_%H%M%S"
    )


def ingest_file(file_name, batch_id):
    input_path = os.path.join(
        RAW_DATA_DIR,
        file_name,
    )

    if not os.path.exists(input_path):
        print(f"WARNING: {file_name} not found.")
        return

    df = pd.read_csv(input_path)

    ingestion_timestamp = datetime.now()

    df["source_file"] = file_name
    df["ingestion_timestamp"] = ingestion_timestamp
    df["batch_id"] = batch_id
    df["source_row_number"] = range(
        1,
        len(df) + 1,
    )

    output_path = os.path.join(
        BRONZE_DATA_DIR,
        file_name,
    )

    df.to_csv(
        output_path,
        index=False,
    )

    print(
        f"Ingested {file_name}: {len(df)} rows"
    )


def main():
    print("Starting Bronze ingestion pipeline...")

    batch_id = create_batch_id()

    print(f"Batch ID: {batch_id}")

    for file_name in SOURCE_FILES:
        ingest_file(
            file_name,
            batch_id,
        )

    print(
        "Bronze ingestion completed successfully."
    )


if __name__ == "__main__":
    main()