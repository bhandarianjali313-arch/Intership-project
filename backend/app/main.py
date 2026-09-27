from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import CORS_ORIGINS
from app.routes.contracts import router as contracts_router, init_sample_contracts
from app.routes.chat import router as chat_router
from app.routes.compare import router as compare_router
from app.routes.reports import router as reports_router
from app.routes.auth_audit import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_sample_contracts()
    yield

app = FastAPI(
    title="LexiGuard AI - Contract Intelligence & Risk Scoring API",
    description="Autonomous LegalTech NLP, XAI Risk Engine, RAG Q&A, and Version Comparison",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contracts_router, prefix="/api/contracts", tags=["Contracts"])
app.include_router(chat_router, prefix="/api/contracts", tags=["Chat & RAG"])
app.include_router(compare_router, prefix="/api/contracts", tags=["Comparison"])
app.include_router(reports_router, prefix="/api/contracts", tags=["Reports"])
app.include_router(auth_router, prefix="/api", tags=["Auth & Audit"])

@app.get("/")
def root():
    return {
        "platform": "LexiGuard AI - Contract Intelligence & Risk Scoring",
        "version": "2.0.0",
        "status": "ONLINE",
        "docs": "/docs",
        "features": [
            "14 Clause Type Detection",
            "NER Named Entity Extraction",
            "0-100 Risk Scoring across 9 Categories",
            "Explainable AI (XAI) with Reason, Impact, Recommendation & Evidence",
            "RAG AI Contract Chat with Page/Section Citations",
            "Version Comparison & Risk Delta",
            "Semantic Search Engine",
            "Multi-Format Report Generation (PDF/HTML, DOCX, JSON)"
        ]
    }
