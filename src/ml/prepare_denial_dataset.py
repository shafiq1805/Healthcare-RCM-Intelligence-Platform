import os

import pandas as pd


SILVER_DIR = os.path.join(
    "data",
    "silver",
)

GOLD_DIR = os.path.join(
    "data",
    "gold",
)

OUTPUT_PATH = os.path.join(
    GOLD_DIR,
    "denial_ml_dataset.csv",
)

os.makedirs(
    GOLD_DIR,
    exist_ok=True,
)


def load_data():
    claims = pd.read_csv(
        os.path.join(
            SILVER_DIR,
            "claims.csv",
        )
    )

    claim_lines = pd.read_csv(
        os.path.join(
            SILVER_DIR,
            "claim_lines.csv",
        )
    )

    providers = pd.read_csv(
        os.path.join(
            SILVER_DIR,
            "providers.csv",
        )
    )

    encounters = pd.read_csv(
        os.path.join(
            SILVER_DIR,
            "encounters.csv",
        )
    )

    return (
        claims,
        claim_lines,
        providers,
        encounters,
    )


def create_claim_line_features(
    claim_lines,
):
    line_features = (
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

    return line_features


def prepare_dataset():
    (
        claims,
        claim_lines,
        providers,
        encounters,
    ) = load_data()

    line_features = create_claim_line_features(
        claim_lines
    )

    dataset = claims.merge(
        line_features,
        on="claim_id",
        how="left",
    )

    provider_features = providers[
        [
            "provider_id",
            "specialty",
        ]
    ].rename(
        columns={
            "specialty":
                "provider_specialty"
        }
    )

    dataset = dataset.merge(
        provider_features,
        on="provider_id",
        how="left",
    )

    encounter_features = encounters[
        [
            "encounter_id",
            "encounter_type",
        ]
    ]

    dataset = dataset.merge(
        encounter_features,
        on="encounter_id",
        how="left",
    )

    dataset["claim_date"] = pd.to_datetime(
        dataset["claim_date"],
        errors="coerce",
    )

    dataset[
        "submission_date"
    ] = pd.to_datetime(
        dataset["submission_date"],
        errors="coerce",
    )

    dataset["days_to_submit"] = (
        dataset["submission_date"]
        - dataset["claim_date"]
    ).dt.days

    dataset["denied_flag"] = (
        dataset["claim_status"]
        == "DENIED"
    ).astype(int)

    selected_columns = [
        "claim_id",
        "claim_amount",
        "claim_line_count",
        "total_charge_amount",
        "total_allowed_amount",
        "total_paid_amount",
        "payer",
        "provider_specialty",
        "encounter_type",
        "days_to_submit",
        "authorization_status",
        "documentation_complete",
        "denied_flag",
    ]

    dataset = dataset[
        selected_columns
    ]

    return dataset


def main():
    print(
        "Preparing denial prediction dataset..."
    )

    dataset = prepare_dataset()

    dataset.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    total_claims = len(dataset)

    denied_claims = int(
        dataset["denied_flag"].sum()
    )

    non_denied_claims = (
        total_claims
        - denied_claims
    )

    denial_rate = (
        denied_claims
        / total_claims
        * 100
    )

    print(
        f"Total claims: {total_claims}"
    )

    print(
        f"Denied claims: {denied_claims}"
    )

    print(
        f"Non-denied claims: "
        f"{non_denied_claims}"
    )

    print(
        f"Denial rate: "
        f"{denial_rate:.2f}%"
    )

    print()
    print("Columns:")

    for column in dataset.columns:
        print(
            f"- {column}"
        )

    print()
    print(
        f"Dataset created: "
        f"{OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()