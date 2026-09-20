import os
import sys


ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

SRC_DIR = os.path.join(
    ROOT_DIR,
    "src",
)

sys.path.append(
    os.path.join(
        SRC_DIR,
        "agents",
    )
)

from rcm_orchestrator import (
    run_rcm_workflow,
)


def test_valid_rcm_workflow():
    result = run_rcm_workflow(
        "C00001",
        (
            "Patient has hypertension "
            "with elevated blood pressure."
        ),
    )

    assert (
        result["workflow_status"]
        in [
            "SUCCESS",
            "MANUAL_REVIEW",
        ]
    )

    assert (
        result[
            "claim_validation"
        ]["status"]
        == "PASS"
    )


def test_invalid_claim():
    result = run_rcm_workflow(
        "C99999",
        (
            "Patient has hypertension."
        ),
    )

    assert (
        result["workflow_status"]
        == "STOPPED"
    )

    assert (
        result["stage"]
        == "CLAIM_VALIDATION"
    )

    assert (
        result[
            "claim_validation"
        ]["status"]
        == "FAIL"
    )