from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from app.services.report_generator import generate_json_report, generate_html_printable_report
from app.routes.contracts import CONTRACTS_DB, log_action

router = APIRouter()

@router.get("/{contract_id}/report/json")
def export_json(contract_id: str):
    if contract_id not in CONTRACTS_DB:
        raise HTTPException(status_code=404, detail="Contract not found")
    contract = CONTRACTS_DB[contract_id]
    data = generate_json_report(contract)
    log_action("EXPORT_JSON", contract.title)
    return JSONResponse(content=data)

@router.get("/{contract_id}/report/html", response_class=HTMLResponse)
def export_html(contract_id: str):
    if contract_id not in CONTRACTS_DB:
        raise HTTPException(status_code=404, detail="Contract not found")
    contract = CONTRACTS_DB[contract_id]
    html = generate_html_printable_report(contract)
    log_action("EXPORT_PDF_HTML", contract.title)
    return HTMLResponse(content=html)
