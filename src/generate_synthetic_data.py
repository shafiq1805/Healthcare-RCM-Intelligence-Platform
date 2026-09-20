import os
import random
from datetime import datetime, timedelta

import pandas as pd

RAW_DATA_DIR = os.path.join("data", "raw")

os.makedirs(RAW_DATA_DIR, exist_ok=True)

FIRST_NAMES = [
    "Arun",
    "Priya",
    "Karthik",
    "Meena",
    "Rahul",
    "Anita",
    "Vijay",
    "Divya",
    "Sanjay",
    "Lakshmi",
]

LAST_NAMES = [
    "Kumar",
    "Raman",
    "Sharma",
    "Rao",
    "Nair",
    "Menon",
    "Patel",
    "Iyer",
]

CITIES = [
    ("Chennai", "Tamil Nadu", "600001"),
    ("Coimbatore", "Tamil Nadu", "641001"),
    ("Madurai", "Tamil Nadu", "625001"),
    ("Bengaluru", "Karnataka", "560001"),
    ("Hyderabad", "Telangana", "500001"),
]

INSURANCE_PLANS = [
    "HealthPlus",
    "CareSecure",
    "MediShield",
]

SPECIALTIES = [
    "Cardiology",
    "Internal Medicine",
    "Orthopedics",
    "Neurology",
    "General Medicine",
]

def generate_patients(count=100):
    patients = []

    for i in range(1, count + 1):
        city, state, zip_code = random.choice(CITIES)

        date_of_birth = datetime(
            random.randint(1945, 2005),
            random.randint(1, 12),
            random.randint(1, 28),
        )

        patients.append(
            {
                "patient_id": f"P{i:04d}",
                "first_name": random.choice(FIRST_NAMES),
                "last_name": random.choice(LAST_NAMES),
                "date_of_birth": date_of_birth.strftime("%Y-%m-%d"),
                "gender": random.choice(["M", "F"]),
                "city": city,
                "state": state,
                "zip_code": zip_code,
                "insurance_plan": random.choice(INSURANCE_PLANS),
                "member_id": f"M{i:06d}",
            }
        )

    return pd.DataFrame(patients)

def generate_providers(count=20):
    providers = []

    for i in range(1, count + 1):
        city, state, _ = random.choice(CITIES)

        providers.append(
            {
                "provider_id": f"PR{i:03d}",
                "provider_name": f"Dr {random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
                "specialty": random.choice(SPECIALTIES),
                "npi": str(1000000000 + i),
                "facility_name": f"{city} Medical Center",
                "city": city,
                "state": state,
            }
        )

    return pd.DataFrame(providers)

DIAGNOSIS_CODES = [
    "I10",
    "E11.9",
    "J18.9",
    "M54.5",
    "I25.10",
]

ENCOUNTER_TYPES = [
    "OUTPATIENT",
    "INPATIENT",
    "EMERGENCY",
]

def generate_encounters(
    patients_df,
    providers_df,
    count=200,
):
    encounters = []

    for i in range(1, count + 1):
        patient = patients_df.sample(1).iloc[0]
        provider = providers_df.sample(1).iloc[0]

        encounter_date = datetime(2026, 1, 1) + timedelta(
            days=random.randint(0, 240)
        )

        encounter_type = random.choice(ENCOUNTER_TYPES)

        if encounter_type == "INPATIENT":
            discharge_date = encounter_date + timedelta(
                days=random.randint(1, 5)
            )
        else:
            discharge_date = encounter_date

        encounters.append(
            {
                "encounter_id": f"E{i:05d}",
                "patient_id": patient["patient_id"],
                "provider_id": provider["provider_id"],
                "encounter_date": encounter_date.strftime("%Y-%m-%d"),
                "encounter_type": encounter_type,
                "department": provider["specialty"],
                "primary_diagnosis": random.choice(DIAGNOSIS_CODES),
                "discharge_date": discharge_date.strftime("%Y-%m-%d"),
            }
        )

    return pd.DataFrame(encounters)

PAYERS = [
    "HealthPlus",
    "CareSecure",
    "MediShield",
]

CLAIM_STATUSES = [
    "SUBMITTED",
    "PENDING",
    "PAID",
    "DENIED",
]

def generate_claims(encounters_df):
    claims = []

    for i, encounter in encounters_df.iterrows():
        claim_date = pd.to_datetime(
            encounter["discharge_date"]
        )

        submission_delay = random.randint(
            1,
            12,
        )

        submission_date = (
            claim_date
            + timedelta(days=submission_delay)
        )

        authorization_status = random.choice(
            [
                "APPROVED",
                "APPROVED",
                "APPROVED",
                "MISSING",
            ]
        )

        documentation_complete = random.choice(
            [
                "YES",
                "YES",
                "YES",
                "NO",
            ]
        )

        claim_amount = random.randint(
            500,
            25000,
        )

        payer = random.choice(
            PAYERS
        )

        denial_risk = 0.08

        if submission_delay > 7:
            denial_risk += 0.20

        if authorization_status == "MISSING":
            denial_risk += 0.35

        if documentation_complete == "NO":
            denial_risk += 0.30

        if claim_amount > 18000:
            denial_risk += 0.10

        if encounter["encounter_type"] == "INPATIENT":
            denial_risk += 0.08

        if payer == "CareSecure":
            denial_risk += 0.05

        denial_risk = min(
            denial_risk,
            0.95,
        )

        if random.random() < denial_risk:
            claim_status = "DENIED"

        else:
            claim_status = random.choice(
                [
                    "SUBMITTED",
                    "PENDING",
                    "PAID",
                ]
            )

        claims.append(
            {
                "claim_id": f"C{i + 1:05d}",
                "patient_id": encounter["patient_id"],
                "encounter_id": encounter["encounter_id"],
                "provider_id": encounter["provider_id"],
                "payer": payer,
                "claim_date": claim_date.strftime(
                    "%Y-%m-%d"
                ),
                "claim_amount": claim_amount,
                "claim_status": claim_status,
                "submission_date": (
                    submission_date.strftime(
                        "%Y-%m-%d"
                    )
                ),
                "authorization_status":
                    authorization_status,
                "documentation_complete":
                    documentation_complete,
            }
        )

    return pd.DataFrame(claims)

PROCEDURE_CODES = [
    "99213",
    "99214",
    "93000",
    "71046",
    "80053",
    "36415",
]

def generate_claim_lines(claims_df):
    claim_lines = []

    line_counter = 1

    for _, claim in claims_df.iterrows():
        number_of_lines = random.randint(1, 4)

        remaining_amount = claim["claim_amount"]

        for line_number in range(number_of_lines):
            if line_number == number_of_lines - 1:
                charge_amount = remaining_amount
            else:
                max_charge = max(
                    1,
                    remaining_amount - (number_of_lines - line_number - 1),
                )

                charge_amount = random.randint(
                    1,
                    max_charge,
                )

            remaining_amount -= charge_amount

            allowed_amount = int(
                charge_amount * random.uniform(0.6, 0.95)
            )

            if claim["claim_status"] == "PAID":
                paid_amount = allowed_amount
            elif claim["claim_status"] == "DENIED":
                paid_amount = 0
            else:
                paid_amount = random.randint(
                    0,
                    allowed_amount,
                )

            claim_lines.append(
                {
                    "claim_line_id": f"CL{line_counter:06d}",
                    "claim_id": claim["claim_id"],
                    "procedure_code": random.choice(PROCEDURE_CODES),
                    "diagnosis_code": random.choice(DIAGNOSIS_CODES),
                    "units": random.randint(1, 3),
                    "charge_amount": charge_amount,
                    "allowed_amount": allowed_amount,
                    "paid_amount": paid_amount,
                }
            )

            line_counter += 1

    return pd.DataFrame(claim_lines)

CLINICAL_TEXTS = [
    "Patient presents with hypertension. Blood pressure remains elevated.",
    "Patient with type 2 diabetes presents for follow-up. Glucose remains above target.",
    "Patient reports chest discomfort. ECG performed during evaluation.",
    "Patient presents with cough and fever. Findings are consistent with pneumonia.",
    "Patient reports lower back pain without neurological deficit.",
]

def generate_clinical_notes(encounters_df):
    notes = []

    for i, encounter in encounters_df.iterrows():
        notes.append(
            {
                "note_id": f"N{i + 1:05d}",
                "encounter_id": encounter["encounter_id"],
                "patient_id": encounter["patient_id"],
                "provider_id": encounter["provider_id"],
                "note_type": random.choice(
                    [
                        "Progress Note",
                        "Consult Note",
                        "Discharge Summary",
                    ]
                ),
                "note_date": encounter["encounter_date"],
                "clinical_text": random.choice(
                    CLINICAL_TEXTS
                ),
            }
        )

    return pd.DataFrame(notes)

DENIALS = [
    ("CO-16", "Missing required documentation", "Documentation"),
    ("CO-50", "Service not medically necessary", "Medical Necessity"),
    ("CO-197", "Authorization missing", "Authorization"),
]

def generate_denials(claims_df):
    denials = []

    denied_claims = claims_df[
        claims_df["claim_status"] == "DENIED"
    ]

    for i, (_, claim) in enumerate(
        denied_claims.iterrows(),
        start=1,
    ):
        denial_code, reason, category = random.choice(
            DENIALS
        )

        denial_date = (
            pd.to_datetime(claim["submission_date"])
            + timedelta(days=random.randint(2, 10))
        )

        denials.append(
            {
                "denial_id": f"D{i:05d}",
                "claim_id": claim["claim_id"],
                "denial_date": denial_date.strftime("%Y-%m-%d"),
                "denial_code": denial_code,
                "denial_reason": reason,
                "denial_category": category,
                "appeal_status": random.choice(
                    [
                        "OPEN",
                        "APPEALED",
                        "CLOSED",
                    ]
                ),
            }
        )

    return pd.DataFrame(denials)

def main():
    random.seed(42)

    patients_df = generate_patients(100)
    providers_df = generate_providers(20)

    encounters_df = generate_encounters(
        patients_df,
        providers_df,
        200,
    )

    claims_df = generate_claims(encounters_df)

    claim_lines_df = generate_claim_lines(
        claims_df
    )

    clinical_notes_df = generate_clinical_notes(
        encounters_df
    )

    denials_df = generate_denials(
        claims_df
    )

    patients_df.to_csv(
        os.path.join(RAW_DATA_DIR, "patients.csv"),
        index=False,
    )

    providers_df.to_csv(
        os.path.join(RAW_DATA_DIR, "providers.csv"),
        index=False,
    )

    encounters_df.to_csv(
        os.path.join(RAW_DATA_DIR, "encounters.csv"),
        index=False,
    )

    claims_df.to_csv(
        os.path.join(RAW_DATA_DIR, "claims.csv"),
        index=False,
    )

    claim_lines_df.to_csv(
        os.path.join(RAW_DATA_DIR, "claim_lines.csv"),
        index=False,
    )

    clinical_notes_df.to_csv(
        os.path.join(RAW_DATA_DIR, "clinical_notes.csv"),
        index=False,
    )

    denials_df.to_csv(
        os.path.join(RAW_DATA_DIR, "denials.csv"),
        index=False,
    )

    print("Synthetic healthcare data generated successfully.")

    print(f"Patients: {len(patients_df)}")
    print(f"Providers: {len(providers_df)}")
    print(f"Encounters: {len(encounters_df)}")
    print(f"Claims: {len(claims_df)}")
    print(f"Claim lines: {len(claim_lines_df)}")
    print(f"Clinical notes: {len(clinical_notes_df)}")
    print(f"Denials: {len(denials_df)}")


if __name__ == "__main__":
    main()