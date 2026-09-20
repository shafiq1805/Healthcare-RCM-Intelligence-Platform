import os

import joblib
import pandas as pd


MODEL_PATH = os.path.join(
    "models",
    "denial_random_forest.joblib",
)


def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}"
        )

    return joblib.load(
        MODEL_PATH
    )


def get_risk_level(probability):
    if probability >= 0.70:
        return "HIGH"

    if probability >= 0.40:
        return "MEDIUM"

    return "LOW"


def predict_denial_risk(
    claim_data,
    model,
):
    required_fields = [
        "claim_amount",
        "claim_line_count",
        "total_charge_amount",
        "total_allowed_amount",
        "payer",
        "provider_specialty",
        "encounter_type",
        "days_to_submit",
        "authorization_status",
        "documentation_complete",
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in claim_data
    ]

    if missing_fields:
        return {
            "status": "FAIL",
            "reason": (
                "Missing required fields: "
                + ", ".join(missing_fields)
            ),
        }

    input_df = pd.DataFrame(
        [claim_data]
    )

    probability = float(
        model.predict_proba(
            input_df
        )[0][1]
    )

    prediction = int(
        probability >= 0.50
    )

    risk_level = get_risk_level(
        probability
    )

    return {
        "status": "SUCCESS",
        "predicted_denial": prediction,
        "denial_probability": round(
            probability,
            4,
        ),
        "risk_level": risk_level,
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

    result = predict_denial_risk(
        test_claim,
        model,
    )

    print(
        "Denial Risk Prediction"
    )

    print(
        f"Status: "
        f"{result['status']}"
    )

    if result["status"] == "SUCCESS":
        print(
            f"Predicted Denial: "
            f"{result['predicted_denial']}"
        )

        print(
            f"Denial Probability: "
            f"{result['denial_probability']}"
        )

        print(
            f"Risk Level: "
            f"{result['risk_level']}"
        )

    else:
        print(
            f"Reason: "
            f"{result['reason']}"
        )


if __name__ == "__main__":
    main()