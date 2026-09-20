import os

import pandas as pd

from claims_validator import load_data, validate_claim


OUTPUT_DIR = os.path.join(
    "data",
    "gold",
)

OUTPUT_PATH = os.path.join(
    OUTPUT_DIR,
    "claim_validation_report.csv",
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True,
)


def validate_all_claims():
    data = load_data()

    claims = data["claims"]

    results = []

    for claim_id in claims["claim_id"]:
        result = validate_claim(
            claim_id,
            data,
        )

        results.append(
            {
                "claim_id": result["claim_id"],
                "validation_status": result["status"],
                "issue_count": len(
                    result["issues"]
                ),
                "issues": " | ".join(
                    result["issues"]
                ),
            }
        )

    return pd.DataFrame(results)


def main():
    print(
        "Starting batch claim validation..."
    )

    results_df = validate_all_claims()

    results_df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    total_claims = len(results_df)

    passed_claims = (
        results_df[
            results_df["validation_status"]
            == "PASS"
        ].shape[0]
    )

    failed_claims = (
        results_df[
            results_df["validation_status"]
            == "FAIL"
        ].shape[0]
    )

    print(
        f"Total claims validated: {total_claims}"
    )

    print(
        f"Passed claims: {passed_claims}"
    )

    print(
        f"Failed claims: {failed_claims}"
    )

    print(
        f"Validation report created: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()