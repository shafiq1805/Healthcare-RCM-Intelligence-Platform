import os

import pandas as pd


SILVER_DATA_DIR = os.path.join(
    "data",
    "silver",
)


def load_data():
    claims = pd.read_csv(
        os.path.join(
            SILVER_DATA_DIR,
            "claims.csv",
        )
    )

    patients = pd.read_csv(
        os.path.join(
            SILVER_DATA_DIR,
            "patients.csv",
        )
    )

    providers = pd.read_csv(
        os.path.join(
            SILVER_DATA_DIR,
            "providers.csv",
        )
    )

    encounters = pd.read_csv(
        os.path.join(
            SILVER_DATA_DIR,
            "encounters.csv",
        )
    )

    claim_lines = pd.read_csv(
        os.path.join(
            SILVER_DATA_DIR,
            "claim_lines.csv",
        )
    )

    return {
        "claims": claims,
        "patients": patients,
        "providers": providers,
        "encounters": encounters,
        "claim_lines": claim_lines,
    }


def validate_claim(
    claim_id,
    data,
):
    claims = data["claims"]
    patients = data["patients"]
    providers = data["providers"]
    encounters = data["encounters"]
    claim_lines = data["claim_lines"]

    issues = []

    claim_rows = claims[
        claims["claim_id"] == claim_id
    ]

    if claim_rows.empty:
        return {
            "claim_id": claim_id,
            "status": "FAIL",
            "issues": [
                "Claim not found"
            ],
        }

    claim = claim_rows.iloc[0]

    patient_id = claim["patient_id"]
    provider_id = claim["provider_id"]
    encounter_id = claim["encounter_id"]

    if patient_id not in patients[
        "patient_id"
    ].values:
        issues.append(
            "Patient not found"
        )

    if provider_id not in providers[
        "provider_id"
    ].values:
        issues.append(
            "Provider not found"
        )

    if encounter_id not in encounters[
        "encounter_id"
    ].values:
        issues.append(
            "Encounter not found"
        )

    matching_lines = claim_lines[
        claim_lines["claim_id"] == claim_id
    ]

    if matching_lines.empty:
        issues.append(
            "Claim contains no claim lines"
        )

    if claim["claim_amount"] <= 0:
        issues.append(
            "Claim amount must be greater than zero"
        )

    if not matching_lines.empty:
        total_line_amount = (
            matching_lines[
                "charge_amount"
            ].sum()
        )

        if total_line_amount != claim[
            "claim_amount"
        ]:
            issues.append(
                "Claim amount does not match "
                "total claim line charges"
            )

        invalid_paid_lines = matching_lines[
            matching_lines["paid_amount"]
            >
            matching_lines["allowed_amount"]
        ]

        if not invalid_paid_lines.empty:
            issues.append(
                "Paid amount exceeds allowed amount"
            )

        if claim["claim_status"] == "DENIED":
            total_paid = matching_lines[
                "paid_amount"
            ].sum()

            if total_paid > 0:
                issues.append(
                    "Denied claim contains paid amount"
                )

    status = (
        "PASS"
        if len(issues) == 0
        else "FAIL"
    )

    return {
        "claim_id": claim_id,
        "status": status,
        "issues": issues,
    }


def main():
    data = load_data()

    test_claim_id = "C00001"

    result = validate_claim(
        test_claim_id,
        data,
    )

    print("Claim Validation Result")
    print(
        f"Claim ID: {result['claim_id']}"
    )
    print(
        f"Status: {result['status']}"
    )
    print(
        f"Issues: {result['issues']}"
    )


if __name__ == "__main__":
    main()