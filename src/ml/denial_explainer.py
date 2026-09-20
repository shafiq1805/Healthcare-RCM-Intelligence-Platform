from denial_predictor import (
    load_model,
    predict_denial_risk,
)


def explain_denial_risk(claim_data):
    reasons = []

    if claim_data.get(
        "authorization_status"
    ) == "MISSING":
        reasons.append(
            {
                "risk_factor":
                    "Missing authorization",
                "severity":
                    "HIGH",
                "recommendation":
                    "Verify and obtain required "
                    "authorization before submission.",
            }
        )

    if claim_data.get(
        "documentation_complete"
    ) == "NO":
        reasons.append(
            {
                "risk_factor":
                    "Incomplete documentation",
                "severity":
                    "HIGH",
                "recommendation":
                    "Complete all required clinical "
                    "and supporting documentation.",
            }
        )

    days_to_submit = claim_data.get(
        "days_to_submit",
        0,
    )

    if days_to_submit > 7:
        reasons.append(
            {
                "risk_factor":
                    "Delayed claim submission",
                "severity":
                    "MEDIUM",
                "recommendation":
                    "Review submission workflow "
                    "and reduce filing delays.",
            }
        )

    claim_amount = claim_data.get(
        "claim_amount",
        0,
    )

    if claim_amount > 18000:
        reasons.append(
            {
                "risk_factor":
                    "High claim amount",
                "severity":
                    "MEDIUM",
                "recommendation":
                    "Perform additional claim review "
                    "before submission.",
            }
        )

    if claim_data.get(
        "encounter_type"
    ) == "INPATIENT":
        reasons.append(
            {
                "risk_factor":
                    "Inpatient claim complexity",
                "severity":
                    "LOW",
                "recommendation":
                    "Verify inpatient documentation, "
                    "coding, and supporting records.",
            }
        )

    if claim_data.get(
        "payer"
    ) == "CareSecure":
        reasons.append(
            {
                "risk_factor":
                    "Synthetic payer risk pattern",
                "severity":
                    "LOW",
                "recommendation":
                    "Review payer-specific claim "
                    "requirements before submission.",
            }
        )

    return reasons


def build_denial_assessment(
    claim_data,
    model,
):
    prediction = predict_denial_risk(
        claim_data,
        model,
    )

    if prediction["status"] != "SUCCESS":
        return prediction

    reasons = explain_denial_risk(
        claim_data
    )

    return {
        "status": "SUCCESS",
        "predicted_denial":
            prediction[
                "predicted_denial"
            ],
        "denial_probability":
            prediction[
                "denial_probability"
            ],
        "risk_level":
            prediction[
                "risk_level"
            ],
        "risk_factors":
            reasons,
    }


def main():
    model = load_model()

    test_claim = {
        "claim_amount": 22000,
        "claim_line_count": 3,
        "total_charge_amount": 22000,
        "total_allowed_amount": 18000,
        "payer": "CareSecure",
        "provider_specialty": "Cardiology",
        "encounter_type": "INPATIENT",
        "days_to_submit": 10,
        "authorization_status": "MISSING",
        "documentation_complete": "NO",
    }

    result = build_denial_assessment(
        test_claim,
        model,
    )

    print(
        "Denial Risk Assessment"
    )

    print(
        f"Risk Level: "
        f"{result['risk_level']}"
    )

    print(
        f"Denial Probability: "
        f"{result['denial_probability']}"
    )

    print()
    print("Risk Factors:")

    for item in result[
        "risk_factors"
    ]:
        print(
            f"- {item['risk_factor']} "
            f"({item['severity']})"
        )

        print(
            f"  Recommendation: "
            f"{item['recommendation']}"
        )


if __name__ == "__main__":
    main()