import os
import pandas as pd


SILVER_DATA_DIR = os.path.join(
    "data",
    "silver",
)

GOLD_DATA_DIR = os.path.join(
    "data",
    "gold",
)

os.makedirs(
    GOLD_DATA_DIR,
    exist_ok=True,
)

def load_silver_data():
    claims = pd.read_csv(
        os.path.join(
            SILVER_DATA_DIR,
            "claims.csv",
        )
    )

    claim_lines = pd.read_csv(
        os.path.join(
            SILVER_DATA_DIR,
            "claim_lines.csv",
        )
    )

    denials = pd.read_csv(
        os.path.join(
            SILVER_DATA_DIR,
            "denials.csv",
        )
    )

    patients = pd.read_csv(
        os.path.join(
            SILVER_DATA_DIR,
            "patients.csv",
        )
    )

    encounters = pd.read_csv(
        os.path.join(
            SILVER_DATA_DIR,
            "encounters.csv",
        )
    )

    providers = pd.read_csv(
        os.path.join(
            SILVER_DATA_DIR,
            "providers.csv",
        )
    )

    return {
        "claims": claims,
        "claim_lines": claim_lines,
        "denials": denials,
        "patients": patients,
        "encounters": encounters,
        "providers": providers,
    }
def build_claim_summary(
    claims,
    claim_lines,
):
    line_summary = (
        claim_lines
        .groupby("claim_id")
        .agg(
            claim_line_count=(
                "claim_line_id",
                "count",
            ),
            total_charge_amount=(
                "charge_amount",
                "sum",
            ),
            total_allowed_amount=(
                "allowed_amount",
                "sum",
            ),
            total_paid_amount=(
                "paid_amount",
                "sum",
            ),
        )
        .reset_index()
    )

    claim_summary = claims.merge(
        line_summary,
        on="claim_id",
        how="left",
    )

    claim_summary["denied_flag"] = (
        claim_summary["claim_status"]
        == "DENIED"
    ).astype(int)

    return claim_summary

def build_denial_summary(
    claims,
    denials,
):
    denied_claims = claims[
        claims["claim_status"] == "DENIED"
    ].copy()

    denial_summary = denied_claims.merge(
        denials,
        on="claim_id",
        how="left",
        suffixes=(
            "_claim",
            "_denial",
        ),
    )

    selected_columns = [
        "claim_id",
        "patient_id",
        "provider_id",
        "payer",
        "claim_amount",
        "submission_date",
        "denial_date",
        "denial_code",
        "denial_reason",
        "denial_category",
        "appeal_status",
    ]

    denial_summary = denial_summary[
        selected_columns
    ]

    return denial_summary

def build_payer_performance(
    claim_summary,
):
    payer_performance = (
        claim_summary
        .groupby("payer")
        .agg(
            total_claims=(
                "claim_id",
                "count",
            ),
            denied_claims=(
                "denied_flag",
                "sum",
            ),
            total_claim_amount=(
                "claim_amount",
                "sum",
            ),
            total_allowed_amount=(
                "total_allowed_amount",
                "sum",
            ),
            total_paid_amount=(
                "total_paid_amount",
                "sum",
            ),
        )
        .reset_index()
    )

    payer_performance[
        "denial_rate"
    ] = (
        payer_performance[
            "denied_claims"
        ]
        / payer_performance[
            "total_claims"
        ]
    )

    payer_performance[
        "denial_rate"
    ] = (
        payer_performance[
            "denial_rate"
        ]
        * 100
    ).round(2)

    return payer_performance

def build_patient_utilization(
    patients,
    encounters,
    claims,
):
    encounter_summary = (
        encounters
        .groupby("patient_id")
        .agg(
            total_encounters=(
                "encounter_id",
                "count",
            ),
        )
        .reset_index()
    )

    claim_summary = (
        claims
        .groupby("patient_id")
        .agg(
            total_claims=(
                "claim_id",
                "count",
            ),
            total_claim_amount=(
                "claim_amount",
                "sum",
            ),
        )
        .reset_index()
    )

    patient_utilization = (
        patients[
            [
                "patient_id",
                "gender",
                "city",
                "state",
                "insurance_plan",
            ]
        ]
        .merge(
            encounter_summary,
            on="patient_id",
            how="left",
        )
        .merge(
            claim_summary,
            on="patient_id",
            how="left",
        )
    )

    patient_utilization[
        "total_encounters"
    ] = (
        patient_utilization[
            "total_encounters"
        ]
        .fillna(0)
        .astype(int)
    )

    patient_utilization[
        "total_claims"
    ] = (
        patient_utilization[
            "total_claims"
        ]
        .fillna(0)
        .astype(int)
    )

    patient_utilization[
        "total_claim_amount"
    ] = (
        patient_utilization[
            "total_claim_amount"
        ]
        .fillna(0)
    )

    return patient_utilization

def save_gold_table(
    df,
    file_name,
):
    output_path = os.path.join(
        GOLD_DATA_DIR,
        file_name,
    )

    df.to_csv(
        output_path,
        index=False,
    )

    print(
        f"Created {file_name}: "
        f"{len(df)} rows"
    )

def main():
    print(
        "Starting Silver to Gold transformation..."
    )

    data = load_silver_data()

    claim_summary = build_claim_summary(
        data["claims"],
        data["claim_lines"],
    )

    denial_summary = build_denial_summary(
        data["claims"],
        data["denials"],
    )

    payer_performance = (
        build_payer_performance(
            claim_summary
        )
    )

    patient_utilization = (
        build_patient_utilization(
            data["patients"],
            data["encounters"],
            data["claims"],
        )
    )

    save_gold_table(
        claim_summary,
        "claim_summary.csv",
    )

    save_gold_table(
        denial_summary,
        "denial_summary.csv",
    )

    save_gold_table(
        payer_performance,
        "payer_performance.csv",
    )

    save_gold_table(
        patient_utilization,
        "patient_utilization.csv",
    )

    print(
        "Gold transformation completed successfully."
    )


if __name__ == "__main__":
    main()