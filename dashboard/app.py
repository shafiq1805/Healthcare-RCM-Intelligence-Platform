import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Healthcare RCM Intelligence",
    page_icon="🏥",
    layout="wide",
)


st.title("Healthcare RCM Intelligence Platform")

st.write(
    "Analyze a claim for structural validity, "
    "denial risk, and evidence-grounded coding."
)


claim_id = st.text_input(
    "Claim ID",
    value="C00001",
)

clinical_question = st.text_area(
    "Clinical Question",
    value=(
        "Patient has hypertension "
        "with elevated blood pressure."
    ),
)


if st.button("Analyze Claim"):

    if not claim_id.strip():
        st.error(
            "Please enter a claim ID."
        )

    elif not clinical_question.strip():
        st.error(
            "Please enter a clinical question."
        )

    else:
        payload = {
            "claim_id": claim_id.strip(),
            "clinical_question":
                clinical_question.strip(),
        }

        try:
            response = requests.post(
                f"{API_URL}/rcm/analyze",
                json=payload,
                timeout=60,
            )

            if response.status_code != 200:
                st.error(
                    f"API Error: "
                    f"{response.text}"
                )

            else:
                result = response.json()

                workflow_status = (
                    result.get(
                        "workflow_status",
                        "UNKNOWN",
                    )
                )

                st.subheader(
                    "Workflow Status"
                )

                if workflow_status == "SUCCESS":
                    st.success(
                        workflow_status
                    )

                elif workflow_status == "MANUAL_REVIEW":
                    st.warning(
                        workflow_status
                    )

                else:
                    st.error(
                        workflow_status
                    )

                claim_validation = (
                    result.get(
                        "claim_validation",
                        {},
                    )
                )

                st.subheader(
                    "Claim Validation"
                )

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Validation Status",
                        claim_validation.get(
                            "status",
                            "N/A",
                        ),
                    )

                with col2:
                    issues = claim_validation.get(
                        "issues",
                        [],
                    )

                    st.metric(
                        "Issues",
                        len(issues),
                    )

                if issues:
                    for issue in issues:
                        st.warning(issue)

                denial_result = (
                    result.get(
                        "denial_result",
                        {},
                    )
                )

                if (
                    denial_result.get(
                        "status"
                    )
                    == "SUCCESS"
                ):
                    st.subheader(
                        "Denial Risk"
                    )

                    probability = (
                        denial_result.get(
                            "denial_probability",
                            0,
                        )
                    )

                    risk_level = (
                        denial_result.get(
                            "risk_level",
                            "UNKNOWN",
                        )
                    )

                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric(
                            "Denial Probability",
                            f"{probability * 100:.2f}%",
                        )

                    with col2:
                        st.metric(
                            "Risk Level",
                            risk_level,
                        )

                    st.progress(
                        min(
                            max(
                                probability,
                                0.0,
                            ),
                            1.0,
                        )
                    )

                    risk_factors = (
                        denial_result.get(
                            "risk_factors",
                            [],
                        )
                    )

                    if risk_factors:
                        st.subheader(
                            "Risk Factors"
                        )

                        for factor in risk_factors:
                            st.write(
                                f"**{factor.get('risk_factor')}** "
                                f"({factor.get('severity')})"
                            )

                            st.caption(
                                factor.get(
                                    "recommendation",
                                    "",
                                )
                            )

                    else:
                        st.info(
                            "No major rule-based "
                            "risk factors identified."
                        )

                coding = result.get(
                    "coding",
                    {},
                )

                coding_result = coding.get(
                    "coding_result",
                    {},
                )

                coding_validation = coding.get(
                    "validation",
                    {},
                )

                if (
                    coding_result.get(
                        "status"
                    )
                    == "SUCCESS"
                ):
                    st.subheader(
                        "Coding Suggestion"
                    )

                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric(
                            "Suggested Code",
                            coding_result.get(
                                "suggested_code",
                                "N/A",
                            ),
                        )

                    with col2:
                        st.metric(
                            "Validation",
                            coding_validation.get(
                                "status",
                                "N/A",
                            ),
                        )

                    st.write(
                        "**Description:** "
                        + str(
                            coding_result.get(
                                "code_description",
                                "",
                            )
                        )
                    )

                    st.write(
                        "**Code Type:** "
                        + str(
                            coding_result.get(
                                "code_type",
                                "",
                            )
                        )
                    )

                    st.write(
                        "**Code Similarity:** "
                        + str(
                            coding_result.get(
                                "code_similarity",
                                "",
                            )
                        )
                    )

                    st.subheader(
                        "Clinical Evidence"
                    )

                    st.write(
                        "**Note ID:** "
                        + str(
                            coding_result.get(
                                "note_id",
                                "",
                            )
                        )
                    )

                    st.write(
                        "**Patient ID:** "
                        + str(
                            coding_result.get(
                                "patient_id",
                                "",
                            )
                        )
                    )

                    st.write(
                        "**Encounter ID:** "
                        + str(
                            coding_result.get(
                                "encounter_id",
                                "",
                            )
                        )
                    )

                    st.info(
                        coding_result.get(
                            "clinical_evidence",
                            "",
                        )
                    )

                with st.expander(
                    "View Raw API Response"
                ):
                    st.json(result)

        except requests.exceptions.ConnectionError:
            st.error(
                "Unable to connect to the FastAPI service. "
                "Make sure the API is running."
            )

        except requests.exceptions.Timeout:
            st.error(
                "The API request timed out."
            )

        except Exception as error:
            st.error(
                f"Unexpected error: {error}"
            )