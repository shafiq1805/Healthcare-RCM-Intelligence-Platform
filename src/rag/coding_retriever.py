import os

import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


REFERENCE_DIR = os.path.join(
    "data",
    "reference",
)

ICD_PATH = os.path.join(
    REFERENCE_DIR,
    "icd10_reference.csv",
)

PROCEDURE_PATH = os.path.join(
    REFERENCE_DIR,
    "procedure_reference.csv",
)


def load_reference_data():
    icd_df = pd.read_csv(
        ICD_PATH
    )

    procedure_df = pd.read_csv(
        PROCEDURE_PATH
    )

    icd_df["code_type"] = "ICD10"
    procedure_df["code_type"] = "PROCEDURE"

    reference_df = pd.concat(
        [
            icd_df,
            procedure_df,
        ],
        ignore_index=True,
    )

    reference_df["search_text"] = (
        reference_df["description"]
        .fillna("")
        .astype(str)
        + " "
        + reference_df["category"]
        .fillna("")
        .astype(str)
    )

    return reference_df


def build_code_retriever(
    reference_df,
):
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
    )

    reference_vectors = (
        vectorizer.fit_transform(
            reference_df[
                "search_text"
            ]
        )
    )

    return (
        vectorizer,
        reference_vectors,
    )


def retrieve_codes(
    query,
    reference_df,
    vectorizer,
    reference_vectors,
    code_type=None,
    top_k=5,
):
    query_vector = (
        vectorizer.transform(
            [query]
        )
    )

    similarities = cosine_similarity(
        query_vector,
        reference_vectors,
    )[0]

    results = reference_df.copy()

    results[
        "similarity_score"
    ] = similarities

    if code_type is not None:
        results = results[
            results["code_type"]
            == code_type
        ]

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
            "code",
            "description",
            "category",
            "code_type",
            "similarity_score",
        ]
    ]


def main():
    reference_df = (
        load_reference_data()
    )

    (
        vectorizer,
        reference_vectors,
    ) = build_code_retriever(
        reference_df
    )

    diagnosis_query = (
        "patient with hypertension "
        "and elevated blood pressure"
    )

    diagnosis_results = (
        retrieve_codes(
            diagnosis_query,
            reference_df,
            vectorizer,
            reference_vectors,
            code_type="ICD10",
            top_k=3,
        )
    )

    print(
        "ICD Retrieval Results"
    )

    print(
        diagnosis_results.to_string(
            index=False
        )
    )

    print()

    procedure_query = (
        "electrocardiogram performed"
    )

    procedure_results = (
        retrieve_codes(
            procedure_query,
            reference_df,
            vectorizer,
            reference_vectors,
            code_type="PROCEDURE",
            top_k=3,
        )
    )

    print(
        "Procedure Retrieval Results"
    )

    print(
        procedure_results.to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()