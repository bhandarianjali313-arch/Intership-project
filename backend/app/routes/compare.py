from fastapi import APIRouter, HTTPException
from app.models.schemas import CompareRequest, CompareResponse
from app.services.diff_engine import compare_contract_versions
from app.routes.contracts import CONTRACTS_DB, log_action

router = APIRouter()

@router.post("/compare", response_model=CompareResponse)
def compare_contracts(req: CompareRequest):
    if req.contract_id_v1 not in CONTRACTS_DB or req.contract_id_v2 not in CONTRACTS_DB:
        raise HTTPException(status_code=404, detail="One or both contracts not found")

    c1 = CONTRACTS_DB[req.contract_id_v1]
    c2 = CONTRACTS_DB[req.contract_id_v2]
    result = compare_contract_versions(c1, c2)
    log_action("CONTRACT_COMPARE", f"{c1.title} vs {c2.title}", details=f"Risk Delta: {result.risk_score_delta}")
    return result
