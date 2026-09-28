from __future__ import annotations

from functools import lru_cache
from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from pydantic import BaseModel, Field

from app.services.ml_contract_service import (
    MLContractService,
)


router = APIRouter()


# ============================================================================
# REQUEST MODELS
# ============================================================================


class ClauseAnalysisRequest(BaseModel):
    """
    Request body for single-clause analysis.
    """

    text: str

    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
    )


class BatchClauseAnalysisRequest(BaseModel):
    """
    Request body for batch clause analysis.
    """

    clauses: list[str]

    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
    )


# ============================================================================
# ML SERVICE LOADING
# ============================================================================


@lru_cache(maxsize=1)
def _create_ml_service() -> MLContractService:
    """
    Create the ML service only once.

    The trained model and vectorizer are therefore
    loaded once instead of on every API request.
    """

    return MLContractService()


def get_ml_service() -> MLContractService:
    """
    FastAPI dependency used to access the ML service.

    A missing model artifact is converted to a
    service-unavailable API response.
    """

    try:
        return _create_ml_service()

    except FileNotFoundError as exc:

        raise HTTPException(
            status_code=503,
            detail=(
                "ML model artifacts are unavailable. "
                f"{exc}"
            ),
        ) from exc


# ============================================================================
# HEALTH ENDPOINT
# ============================================================================


@router.get("/health")
def ml_health(
    service: MLContractService = Depends(
        get_ml_service
    ),
) -> dict[str, Any]:
    """
    Return ML model readiness information.
    """

    return service.health()


# ============================================================================
# SINGLE CLAUSE ANALYSIS
# ============================================================================


@router.post("/analyze-clause")
def analyze_clause(
    request: ClauseAnalysisRequest,
    service: MLContractService = Depends(
        get_ml_service
    ),
) -> dict[str, Any]:
    """
    Analyze one contract clause.

    The response contains:

    - predicted clause category
    - confidence score
    - confidence level
    - ambiguity information
    - human-review recommendation
    - top predictions
    - risk level
    - risk score
    """

    try:

        result = service.analyze_clause(
            text=request.text,
            top_k=request.top_k,
        )

    except (
        ValueError,
        TypeError,
    ) as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return result


# ============================================================================
# BATCH CLAUSE ANALYSIS
# ============================================================================


@router.post("/analyze-clauses")
def analyze_clauses(
    request: BatchClauseAnalysisRequest,
    service: MLContractService = Depends(
        get_ml_service
    ),
) -> dict[str, Any]:
    """
    Analyze multiple contract clauses in one API call.
    """

    try:

        results = service.analyze_clauses(
            clauses=request.clauses,
            top_k=request.top_k,
        )

    except (
        ValueError,
        TypeError,
    ) as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    review_count = sum(
        1
        for item in results
        if item[
            "classification"
        ].get(
            "requires_human_review",
            False,
        )
    )

    return {
        "total_clauses":
            len(results),

        "human_review_required":
            review_count,

        "automatic_review_accepted":
            len(results)
            - review_count,

        "results":
            results,
    }