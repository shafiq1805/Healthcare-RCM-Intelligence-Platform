import os
import sys

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

SRC_DIR = os.path.dirname(
    CURRENT_DIR
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


app = FastAPI(
    title="Healthcare RCM Intelligence API",
    description=(
        "API for claim validation, denial-risk "
        "prediction, clinical retrieval, and "
        "evidence-grounded coding support."
    ),
    version="1.0.0",
)


class RCMRequest(BaseModel):
    claim_id: str
    clinical_question: str


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service":
            "Healthcare RCM Intelligence API",
    }


@app.post("/rcm/analyze")
def analyze_claim(
    request: RCMRequest,
):
    try:
        result = run_rcm_workflow(
            request.claim_id,
            request.clinical_question,
        )

        return result

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "RCM workflow failed: "
                + str(error)
            ),
        )