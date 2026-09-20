from clinical_retriever import (
    load_clinical_notes,
    build_retriever,
    retrieve_notes,
)

from clinical_answer import (
    generate_grounded_answer,
)


def validate_answer(
    answer_result,
    retrieved_notes,
):
    if answer_result.get("status") != "SUCCESS":
        return {
            "status": "FAIL",
            "reason": "Answer generation failed",
        }

    evidence_list = answer_result.get(
        "evidence",
        [],
    )

    if not evidence_list:
        return {
            "status": "FAIL",
            "reason": "No evidence provided",
        }

    valid_note_ids = set(
        retrieved_notes[
            "note_id"
        ].astype(str)
    )

    valid_patient_ids = set(
        retrieved_notes[
            "patient_id"
        ].astype(str)
    )

    valid_encounter_ids = set(
        retrieved_notes[
            "encounter_id"
        ].astype(str)
    )

    retrieved_texts = (
        retrieved_notes[
            "clinical_text"
        ]
        .fillna("")
        .astype(str)
        .str.lower()
        .tolist()
    )

    for evidence in evidence_list:
        note_id = str(
            evidence.get(
                "note_id",
                "",
            )
        )

        patient_id = str(
            evidence.get(
                "patient_id",
                "",
            )
        )

        encounter_id = str(
            evidence.get(
                "encounter_id",
                "",
            )
        )

        evidence_text = str(
            evidence.get(
                "evidence_text",
                "",
            )
        ).strip()

        if note_id not in valid_note_ids:
            return {
                "status": "FAIL",
                "reason":
                    "Evidence note ID not found "
                    "in retrieved context",
            }

        if patient_id not in valid_patient_ids:
            return {
                "status": "FAIL",
                "reason":
                    "Evidence patient ID not found "
                    "in retrieved context",
            }

        if encounter_id not in valid_encounter_ids:
            return {
                "status": "FAIL",
                "reason":
                    "Evidence encounter ID not found "
                    "in retrieved context",
            }

        if not evidence_text:
            return {
                "status": "FAIL",
                "reason": "Evidence text is empty",
            }

        evidence_found = any(
            evidence_text.lower()
            in context_text
            for context_text
            in retrieved_texts
        )

        if not evidence_found:
            return {
                "status": "FAIL",
                "reason":
                    "Evidence text not found "
                    "in retrieved context",
            }

    return {
        "status": "PASS",
        "reason":
            "Answer is grounded in "
            "retrieved clinical context",
    }


def main():
    notes = load_clinical_notes()

    vectorizer, note_vectors = (
        build_retriever(notes)
    )

    question = (
        "What clinical information "
        "is available about hypertension?"
    )

    retrieved_notes = retrieve_notes(
        question,
        notes,
        vectorizer,
        note_vectors,
        top_k=3,
    )

    answer_result = (
        generate_grounded_answer(
            question,
            retrieved_notes,
        )
    )

    validation_result = (
        validate_answer(
            answer_result,
            retrieved_notes,
        )
    )

    print(
        "Answer Validation Result"
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