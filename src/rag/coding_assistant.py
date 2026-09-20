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


def build_coding_suggestion(
    question,
    clinical_results,
    code_results,
    minimum_clinical_score=0.05,
    minimum_code_score=0.05,
):
    if clinical_results.empty:
        return {
            "status": "FAIL",
            "reason": "No clinical evidence found",
        }

    if code_results.empty:
        return {
            "status": "FAIL",
            "reason": "No candidate code found",
        }

    best_clinical = clinical_results.iloc[0]
    best_code = code_results.iloc[0]

    clinical_score = float(
        best_clinical[
            "similarity_score"
        ]
    )

    code_score = float(
        best_code[
            "similarity_score"
        ]
    )

    if clinical_score < minimum_clinical_score:
        return {
            "status": "FAIL",
            "reason":
                "Clinical evidence similarity "
                "is below threshold",
        }

    if code_score < minimum_code_score:
        return {
            "status": "FAIL",
            "reason":
                "Code similarity is below threshold",
        }

    return {
        "status": "SUCCESS",
        "question": question,
        "suggested_code":
            best_code["code"],
        "code_description":
            best_code["description"],
        "code_type":
            best_code["code_type"],
        "code_category":
            best_code["category"],
        "code_similarity":
            round(
                code_score,
                4,
            ),
        "note_id":
            best_clinical["note_id"],
        "patient_id":
            best_clinical["patient_id"],
        "encounter_id":
            best_clinical["encounter_id"],
        "clinical_evidence":
            best_clinical[
                "clinical_text"
            ],
        "clinical_similarity":
            round(
                clinical_score,
                4,
            ),
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

    result = build_coding_suggestion(
        question,
        clinical_results,
        code_results,
    )

    print(
        "Coding Assistant Result"
    )

    print(
        f"Status: "
        f"{result['status']}"
    )

    if result["status"] == "SUCCESS":
        print()

        print(
            f"Suggested Code: "
            f"{result['suggested_code']}"
        )

        print(
            f"Description: "
            f"{result['code_description']}"
        )

        print(
            f"Code Type: "
            f"{result['code_type']}"
        )

        print(
            f"Code Similarity: "
            f"{result['code_similarity']}"
        )

        print()

        print(
            f"Note ID: "
            f"{result['note_id']}"
        )

        print(
            f"Patient ID: "
            f"{result['patient_id']}"
        )

        print(
            f"Encounter ID: "
            f"{result['encounter_id']}"
        )

        print(
            f"Clinical Similarity: "
            f"{result['clinical_similarity']}"
        )

        print()

        print(
            "Clinical Evidence:"
        )

        print(
            result[
                "clinical_evidence"
            ]
        )

    else:
        print(
            f"Reason: "
            f"{result['reason']}"
        )


if __name__ == "__main__":
    main()