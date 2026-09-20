import os
import sqlite3

import pandas as pd


SILVER_DATA_DIR = os.path.join(
    "data",
    "silver",
)

GOLD_DATA_DIR = os.path.join(
    "data",
    "gold",
)

DATABASE_DIR = os.path.join(
    "data",
    "warehouse",
)

DATABASE_PATH = os.path.join(
    DATABASE_DIR,
    "healthcare_rcm.db",
)

os.makedirs(
    DATABASE_DIR,
    exist_ok=True,
)

def get_connection():
    return sqlite3.connect(
        DATABASE_PATH
    )

SILVER_TABLES = {
    "patients": "patients.csv",
    "providers": "providers.csv",
    "encounters": "encounters.csv",
    "claims": "claims.csv",
    "claim_lines": "claim_lines.csv",
    "clinical_notes": "clinical_notes.csv",
    "denials": "denials.csv",
}

GOLD_TABLES = {
    "gold_claim_summary": "claim_summary.csv",
    "gold_denial_summary": "denial_summary.csv",
    "gold_payer_performance": "payer_performance.csv",
    "gold_patient_utilization": "patient_utilization.csv",
}

def load_csv_to_sql(
    connection,
    file_path,
    table_name,
):
    df = pd.read_csv(file_path)

    df.to_sql(
        table_name,
        connection,
        if_exists="replace",
        index=False,
    )

    print(
        f"Loaded {table_name}: "
        f"{len(df)} rows"
    )

def load_silver_tables(connection):
    print()
    print("Loading Silver tables...")

    for (
        table_name,
        file_name,
    ) in SILVER_TABLES.items():

        file_path = os.path.join(
            SILVER_DATA_DIR,
            file_name,
        )

        load_csv_to_sql(
            connection,
            file_path,
            table_name,
        )

def load_gold_tables(connection):
    print()
    print("Loading Gold tables...")

    for (
        table_name,
        file_name,
    ) in GOLD_TABLES.items():

        file_path = os.path.join(
            GOLD_DATA_DIR,
            file_name,
        )

        load_csv_to_sql(
            connection,
            file_path,
            table_name,
        )

def verify_tables(connection):
    query = """
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name;
    """

    tables_df = pd.read_sql_query(
        query,
        connection,
    )

    print()
    print("Tables available in warehouse:")
    print(
        tables_df.to_string(
            index=False
        )
    )

def main():
    print(
        "Starting SQL warehouse load..."
    )

    connection = get_connection()

    try:
        load_silver_tables(
            connection
        )

        load_gold_tables(
            connection
        )

        verify_tables(
            connection
        )

        print()
        print(
            "SQL warehouse loaded successfully."
        )

        print(
            f"Database: {DATABASE_PATH}"
        )

    finally:
        connection.close()


if __name__ == "__main__":
    main()