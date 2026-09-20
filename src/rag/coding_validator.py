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


def validate_coding_result(
    coding_result,
    clinical_results,
    code_results,
):
    if coding_result.get("status") != "SUCCESS":
        return {
            "status": "FAIL",
            "reason": "Coding suggestion was not generated successfully",
        }

    suggested_code = str(
        coding_result.get(
            "suggested_code",
            "",
        )
    )

    note_id = str(
        coding_result.get(
            "note_id",
            "",
        )
    )

    patient_id = str(
        coding_result.get(
            "patient_id",
            "",
        )
    )

    encounter_id = str(
        coding_result.get(
            "encounter_id",
            "",
        )
    )

    clinical_evidence = str(
        coding_result.get(
            "clinical_evidence",
            "",
        )
    ).strip()

    valid_codes = set(
        code_results[
            "code"
        ].astype(str)
    )

    valid_note_ids = set(
        clinical_results[
            "note_id"
        ].astype(str)
    )

    valid_patient_ids = set(
        clinical_results[
            "patient_id"
        ].astype(str)
    )

    valid_encounter_ids = set(
        clinical_results[
            "encounter_id"
        ].astype(str)
    )

    clinical_texts = (
        clinical_results[
            "clinical_text"
        ]
        .fillna("")
        .astype(str)
        .str.lower()
        .tolist()
    )

    if suggested_code not in valid_codes:
        return {
            "status": "FAIL",
            "reason":
                "Suggested code is not present "
                "in retrieved code candidates",
        }

    if note_id not in valid_note_ids:
        return {
            "status": "FAIL",
            "reason":
                "Supporting note ID is not present "
                "in retrieved clinical context",
        }

    if patient_id not in valid_patient_ids:
        return {
            "status": "FAIL",
            "reason":
                "Patient ID is not present "
                "in retrieved clinical context",
        }

    if encounter_id not in valid_encounter_ids:
        return {
            "status": "FAIL",
            "reason":
                "Encounter ID is not present "
                "in retrieved clinical context",
        }

    if not clinical_evidence:
        return {
            "status": "FAIL",
            "reason":
                "Clinical evidence is empty",
        }

    evidence_found = any(
        clinical_evidence.lower()
        in text
        for text in clinical_texts
    )

    if not evidence_found:
        return {
            "status": "FAIL",
            "reason":
                "Clinical evidence is not present "
                "in retrieved context",
        }

    return {
        "status": "PASS",
        "reason":
            "Coding suggestion is supported by "
            "clinical evidence and retrieved "
            "reference code candidates",
    }


def main():
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

    question = (
        "Patient has hypertension "
        "with elevated blood pressure."
    )

    clinical_results = retrieve_notes(
        question,
        notes,
        clinical_vectorizer,
        clinical_vectors,
        top_k=3,
    )

    code_results = retrieve_codes(
        question,
        reference_df,
        code_vectorizer,
        code_vectors,
        code_type="ICD10",
        top_k=3,
    )

    coding_result = (
        build_coding_suggestion(
            question,
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

    print(
        "Coding Validation Result"
    )

    print(
        f"Status: "
        f"{validation_result['status']}"
    )

    print(
        f"Reason: "
        f"{validation_result['reason']}"
    )


if __name__ == "__main__":
    main()