import os

import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


SILVER_DIR = os.path.join(
    "data",
    "silver",
)

NOTES_PATH = os.path.join(
    SILVER_DIR,
    "clinical_notes.csv",
)


def load_clinical_notes():
    notes = pd.read_csv(
        NOTES_PATH
    )

    notes["clinical_text"] = (
        notes["clinical_text"]
        .fillna("")
        .astype(str)
    )

    return notes


def build_retriever(notes):
    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    note_vectors = (
        vectorizer.fit_transform(
            notes["clinical_text"]
        )
    )

    return vectorizer, note_vectors


def retrieve_notes(
    query,
    notes,
    vectorizer,
    note_vectors,
    top_k=3,
):
    query_vector = (
        vectorizer.transform(
            [query]
        )
    )

    similarities = cosine_similarity(
        query_vector,
        note_vectors,
    )[0]

    results = notes.copy()

    results[
        "similarity_score"
    ] = similarities

    results = (
        results
        .sort_values(
            "similarity_score",
            ascending=False,
        )
        .head(top_k)
    )

    return results[
        [
            "note_id",
            "encounter_id",
            "patient_id",
            "provider_id",
            "note_type",
            "note_date",
            "clinical_text",
            "similarity_score",
        ]
    ]


def main():
    notes = load_clinical_notes()

    vectorizer, note_vectors = (
        build_retriever(notes)
    )

    query = (
        "patient with hypertension "
        "and elevated blood pressure"
    )

    results = retrieve_notes(
        query,
        notes,
        vectorizer,
        note_vectors,
        top_k=3,
    )

    print(
        "Clinical Retrieval Results"
    )

    print(
        results.to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()