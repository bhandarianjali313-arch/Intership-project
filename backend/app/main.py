from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS

from app.routes.contracts import (
    router as contracts_router,
    init_sample_contracts,
)

from app.routes.chat import (
    router as chat_router,
)

from app.routes.compare import (
    router as compare_router,
)

from app.routes.reports import (
    router as reports_router,
)

from app.routes.auth_audit import (
    router as auth_router,
)

from app.routes.ml_analysis import (
    router as ml_router,
)


# ============================================================================
# APPLICATION LIFESPAN
# ============================================================================


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    """
    Initialize sample contracts when the
    application starts.
    """

    init_sample_contracts()

    yield


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================


app = FastAPI(
    title=(
        "LexiGuard AI - "
        "Contract Intelligence & Risk Scoring API"
    ),
    description=(
        "Autonomous LegalTech NLP, XAI Risk Engine, "
        "RAG Q&A, Version Comparison, and "
        "Machine Learning Contract Analysis"
    ),
    version="2.1.0",
    lifespan=lifespan,
)


# ============================================================================
# CORS
# ============================================================================


app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# APPLICATION ROUTES
# ============================================================================


app.include_router(
    contracts_router,
    prefix="/api/contracts",
    tags=["Contracts"],
)

app.include_router(
    chat_router,
    prefix="/api/contracts",
    tags=["Chat & RAG"],
)

app.include_router(
    compare_router,
    prefix="/api/contracts",
    tags=["Comparison"],
)

app.include_router(
    reports_router,
    prefix="/api/contracts",
    tags=["Reports"],
)

app.include_router(
    auth_router,
    prefix="/api",
    tags=["Auth & Audit"],
)

app.include_router(
    ml_router,
    prefix="/api/ml",
    tags=["ML Analysis"],
)


# ============================================================================
# ROOT ENDPOINT
# ============================================================================


@app.get("/")
def root():
    """
    API root endpoint.
    """

    return {
        "platform":
            (
                "LexiGuard AI - Contract "
                "Intelligence & Risk Scoring"
            ),

        "version":
            "2.1.0",

        "status":
            "ONLINE",

        "docs":
            "/docs",

        "ml_api":
            "/api/ml",

        "features": [
            "Clause Type Detection",

            "Machine Learning Clause Classification",

            "Confidence-Aware Prediction",

            "Human Review Recommendation",

            "NER Named Entity Extraction",

            (
                "Risk Scoring and "
                "Explainable Analysis"
            ),

            (
                "RAG AI Contract Chat "
                "with Citations"
            ),

            (
                "Version Comparison "
                "and Risk Delta"
            ),

            "Semantic Search Engine",

            (
                "Multi-Format Report "
                "Generation"
            ),
        ],
    }