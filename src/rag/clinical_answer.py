from clinical_retriever import (
    load_clinical_notes,
    build_retriever,
    retrieve_notes,
)


def generate_grounded_answer(
    question,
    retrieved_notes,
):
    if retrieved_notes.empty:
        return {
            "status": "FAIL",
            "answer": None,
            "evidence": [],
            "reason": "No relevant clinical context found",
        }

    best_note = retrieved_notes.iloc[0]

    similarity_score = float(
        best_note["similarity_score"]
    )

    if similarity_score <= 0:
        return {
            "status": "FAIL",
            "answer": None,
            "evidence": [],
            "reason": "Retrieved context is not relevant",
        }

    clinical_text = best_note[
        "clinical_text"
    ]

    answer = (
        "Based on the retrieved clinical note: "
        + clinical_text
    )

    evidence = [
        {
            "note_id": best_note[
                "note_id"
            ],
            "patient_id": best_note[
                "patient_id"
            ],
            "encounter_id": best_note[
                "encounter_id"
            ],
            "evidence_text":
                clinical_text,
            "similarity_score":
                round(
                    similarity_score,
                    4,
                ),
        }
    ]

    return {
        "status": "SUCCESS",
        "question": question,
        "answer": answer,
        "evidence": evidence,
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

    result = generate_grounded_answer(
        question,
        retrieved_notes,
    )

    print(
        "Clinical Answer Result"
    )

    print(
        f"Status: {result['status']}"
    )

    if result["status"] == "SUCCESS":
        print()
        print(
            f"Question: "
            f"{result['question']}"
        )

        print()
        print(
            f"Answer: "
            f"{result['answer']}"
        )

        print()
        print("Evidence:")

        for item in result[
            "evidence"
        ]:
            print(
                f"- Note ID: "
                f"{item['note_id']}"
            )

            print(
                f"  Patient ID: "
                f"{item['patient_id']}"
            )

            print(
                f"  Encounter ID: "
                f"{item['encounter_id']}"
            )

            print(
                f"  Similarity: "
                f"{item['similarity_score']}"
            )

            print(
                f"  Evidence: "
                f"{item['evidence_text']}"
            )

    else:
        print(
            f"Reason: "
            f"{result['reason']}"
        )


if __name__ == "__main__":
    main()