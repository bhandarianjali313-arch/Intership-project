from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag_search import answer_contract_question, perform_semantic_search
from app.routes.contracts import CONTRACTS_DB, log_action

router = APIRouter()

@router.post("/{contract_id}/chat", response_model=ChatResponse)
def chat_with_contract(contract_id: str, req: ChatRequest):
    if contract_id not in CONTRACTS_DB:
        raise HTTPException(status_code=404, detail="Contract not found")

    contract = CONTRACTS_DB[contract_id]
    res = answer_contract_question(contract.title, contract.clauses, req.message)
    log_action("CONTRACT_QA", contract.title, details=f"Q: {req.message} | Citations: {len(res.citations)}")
    return res

@router.get("/search")
def search_clauses(q: str):
    all_contracts = list(CONTRACTS_DB.values())
    results = perform_semantic_search(q, all_contracts)
    log_action("SEMANTIC_SEARCH", q, details=f"Hits: {len(results)}")
    return {
        "query": q,
        "total_results": len(results),
        "results": results
    }
