import sqlite3
import pandas as pd


DATABASE_PATH = "data/warehouse/healthcare_rcm.db"


def run_query(query):
    connection = sqlite3.connect(DATABASE_PATH)

    try:
        df = pd.read_sql_query(
            query,
            connection,
        )

        print(
            df.to_string(
                index=False
            )
        )

    finally:
        connection.close()


query = """
   
WITH ranked_claims AS (
    SELECT
        patient_id,
        claim_id,
        claim_date,
        claim_amount,
        claim_status,
        ROW_NUMBER() OVER (
            PARTITION BY patient_id
            ORDER BY claim_date DESC, claim_id DESC
        ) AS rn
    FROM claims
)

SELECT
    patient_id,
    claim_id,
    claim_date,
    claim_amount,
    claim_status
FROM ranked_claims
WHERE rn = 1
ORDER BY patient_id;

"""


run_query(query)