import os
import sys

# Add project src directories to Python path
CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

SRC_DIR = os.path.dirname(
    CURRENT_DIR
)

sys.path.append(
    os.path.join(
        SRC_DIR,
        "validation",
    )
)

sys.path.append(
    os.path.join(
        SRC_DIR,
        "ml",
    )
)

sys.path.append(
    os.path.join(
        SRC_DIR,
        "rag",
    )
)


from claims_validator import (
    load_data,
    validate_claim,
)

from denial_predictor import (
    load_model,
    predict_denial_risk,
)

from denial_explainer import (
    explain_denial_risk,
)

from clinical_retriever import (
    load_clinical_notes,
    build_retriever,
    retrieve_notes,
)

from coding_retriever import (
    load_reference_data,
    build_code_retriever,
    retrieve_codes,
)

from coding_assistant import (
    build_coding_suggestion,
)

from coding_validator import (
    validate_coding_result,
)


def prepare_denial_features(
    claim_id,
    data,
):
    claims = data["claims"]
    claim_lines = data["claim_lines"]
    providers = data["providers"]
    encounters = data["encounters"]

    claim_rows = claims[
        claims["claim_id"] == claim_id
    ]

    if claim_rows.empty:
        return None

    claim = claim_rows.iloc[0]

    lines = claim_lines[
        claim_lines["claim_id"]
        == claim_id
    ]

    provider_rows = providers[
        providers["provider_id"]
        == claim["provider_id"]
    ]

    encounter_rows = encounters[
        encounters["encounter_id"]
        == claim["encounter_id"]
    ]

    if (
        provider_rows.empty
        or encounter_rows.empty
    ):
        return None

    provider = provider_rows.iloc[0]
    encounter = encounter_rows.iloc[0]

    claim_date = claim["claim_date"]
    submission_date = claim[
        "submission_date"
    ]

    import pandas as pd

    claim_date = pd.to_datetime(
        claim_date
    )

    submission_date = pd.to_datetime(
        submission_date
    )

    days_to_submit = (
        submission_date
        - claim_date
    ).days

    features = {
        "claim_amount":
            claim["claim_amount"],

        "claim_line_count":
            len(lines),

        "total_charge_amount":
            lines[
                "charge_amount"
            ].sum(),

        "total_allowed_amount":
            lines[
                "allowed_amount"
            ].sum(),

        "payer":
            claim["payer"],

        "provider_specialty":
            provider["specialty"],

        "encounter_type":
            encounter["encounter_type"],

        "days_to_submit":
            days_to_submit,

        "authorization_status":
            claim[
                "authorization_status"
            ],

        "documentation_complete":
            claim[
                "documentation_complete"
            ],
    }

    return features


def run_claim_agent(
    claim_id,
    data,
):
    result = validate_claim(
        claim_id,
        data,
    )

    return result


def run_denial_agent(
    claim_id,
    data,
    model,
):
    features = prepare_denial_features(
        claim_id,
        data,
    )

    if features is None:
        return {
            "status": "FAIL",
            "reason":
                "Unable to prepare "
                "denial prediction features",
        }

    prediction = predict_denial_risk(
        features,
        model,
    )

    if prediction[
        "status"
    ] != "SUCCESS":
        return prediction

    risk_factors = (
        explain_denial_risk(
            features
        )
    )

    prediction[
        "risk_factors"
    ] = risk_factors

    return prediction


def run_coding_agent(
    clinical_question,
    clinical_resources,
    coding_resources,
):
    (
        notes,
        clinical_vectorizer,
        clinical_vectors,
    ) = clinical_resources

    (
        reference_df,
        code_vectorizer,
        code_vectors,
    ) = coding_resources

    clinical_results = retrieve_notes(
        clinical_question,
        notes,
        clinical_vectorizer,
        clinical_vectors,
        top_k=3,
    )

    code_results = retrieve_codes(
        clinical_question,
        reference_df,
        code_vectorizer,
        code_vectors,
        code_type="ICD10",
        top_k=3,
    )

    coding_result = (
        build_coding_suggestion(
            clinical_question,
            clinical_results,
            code_results,
        )
    )

    validation_result = (
        validate_coding_result(
            coding_result,
            clinical_results,
            code_results,
        )
    )

    return {
        "coding_result":
            coding_result,

        "validation":
            validation_result,
    }


def initialize_resources():
    claim_data = load_data()

    denial_model = load_model()

    notes = load_clinical_notes()

    (
        clinical_vectorizer,
        clinical_vectors,
    ) = build_retriever(
        notes
    )

    reference_df = (
        load_reference_data()
    )

    (
        code_vectorizer,
        code_vectors,
    ) = build_code_retriever(
        reference_df
    )

    clinical_resources = (
        notes,
        clinical_vectorizer,
        clinical_vectors,
    )

    coding_resources = (
        reference_df,
        code_vectorizer,
        code_vectors,
    )

    return (
        claim_data,
        denial_model,
        clinical_resources,
        coding_resources,
    )


def run_rcm_workflow(
    claim_id,
    clinical_question,
):
    (
        claim_data,
        denial_model,
        clinical_resources,
        coding_resources,
    ) = initialize_resources()

    print(
        "Starting RCM Agent Workflow"
    )

    print(
        f"Claim ID: {claim_id}"
    )

    print()

    # -------------------------
    # Claim Validation Agent
    # -------------------------

    claim_validation = (
        run_claim_agent(
            claim_id,
            claim_data,
        )
    )

    if (
        claim_validation["status"]
        != "PASS"
    ):
        return {
            "workflow_status":
                "STOPPED",

            "stage":
                "CLAIM_VALIDATION",

            "claim_validation":
                claim_validation,
        }

    # -------------------------
    # Denial Risk Agent
    # -------------------------

    denial_result = (
        run_denial_agent(
            claim_id,
            claim_data,
            denial_model,
        )
    )

    if (
        denial_result["status"]
        != "SUCCESS"
    ):
        return {
            "workflow_status":
                "STOPPED",

            "stage":
                "DENIAL_PREDICTION",

            "claim_validation":
                claim_validation,

            "denial_result":
                denial_result,
        }

    # -------------------------
    # Coding Agent
    # -------------------------

    coding_agent_result = (
        run_coding_agent(
            clinical_question,
            clinical_resources,
            coding_resources,
        )
    )

    coding_validation = (
        coding_agent_result[
            "validation"
        ]
    )

    if (
        coding_validation[
            "status"
        ]
        != "PASS"
    ):
        return {
            "workflow_status":
                "MANUAL_REVIEW",

            "stage":
                "CODING_VALIDATION",

            "claim_validation":
                claim_validation,

            "denial_result":
                denial_result,

            "coding":
                coding_agent_result,
        }

    return {
        "workflow_status":
            "SUCCESS",

        "claim_id":
            claim_id,

        "claim_validation":
            claim_validation,

        "denial_result":
            denial_result,

        "coding":
            coding_agent_result,
    }


def print_result(
    result,
):
    print()
    print(
        "=" * 60
    )

    print(
        "RCM WORKFLOW RESULT"
    )

    print(
        "=" * 60
    )

    print(
        f"Workflow Status: "
        f"{result['workflow_status']}"
    )

    if (
        "claim_validation"
        in result
    ):
        claim_validation = (
            result[
                "claim_validation"
            ]
        )

        print()
        print(
            "Claim Validation"
        )

        print(
            f"Status: "
            f"{claim_validation['status']}"
        )

        print(
            f"Issues: "
            f"{claim_validation['issues']}"
        )

    if (
        "denial_result"
        in result
    ):
        denial = result[
            "denial_result"
        ]

        if denial.get(
            "status"
        ) == "SUCCESS":

            print()
            print(
                "Denial Risk"
            )

            print(
                f"Probability: "
                f"{denial['denial_probability']}"
            )

            print(
                f"Risk Level: "
                f"{denial['risk_level']}"
            )

            print(
                "Risk Factors:"
            )

            for item in denial.get(
                "risk_factors",
                [],
            ):
                print(
                    f"- "
                    f"{item['risk_factor']} "
                    f"({item['severity']})"
                )

    if (
        "coding"
        in result
    ):
        coding = result[
            "coding"
        ]

        coding_result = coding[
            "coding_result"
        ]

        validation = coding[
            "validation"
        ]

        print()
        print(
            "Coding Agent"
        )

        print(
            f"Validation: "
            f"{validation['status']}"
        )

        if (
            coding_result.get(
                "status"
            )
            == "SUCCESS"
        ):
            print(
                f"Suggested Code: "
                f"{coding_result['suggested_code']}"
            )

            print(
                f"Description: "
                f"{coding_result['code_description']}"
            )

            print(
                f"Note ID: "
                f"{coding_result['note_id']}"
            )

            print(
                f"Evidence: "
                f"{coding_result['clinical_evidence']}"
            )


def main():
    claim_id = "C00001"

    clinical_question = (
        "Patient has hypertension "
        "with elevated blood pressure."
    )

    result = run_rcm_workflow(
        claim_id,
        clinical_question,
    )

    print_result(
        result
    )


if __name__ == "__main__":
    main()