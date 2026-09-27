import os, uuid, shutil
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from app.models.schemas import (
    ContractSummary, ContractDetail, SearchResponse, AuditLog
)
from app.services.extractor import extract_text_from_file
from app.services.clause_detector import classify_clause
from app.services.ner_engine import extract_entities_from_contract
from app.services.risk_scorer import analyze_clause_risk_and_xai, compute_overall_risk_profile
from app.services.rag_search import perform_semantic_search
from app.config import UPLOAD_DIR, SAMPLE_DIR

router = APIRouter()

CONTRACTS_DB: Dict[str, ContractDetail] = {}
AUDIT_LOGS: List[AuditLog] = []

def log_action(action: str, target: str, user: str = "Legal Counsel", status: str = "SUCCESS", details: str = ""):
    AUDIT_LOGS.insert(0, AuditLog(
        id=f"log_{uuid.uuid4().hex[:8]}",
        timestamp=datetime.now().isoformat(),
        user_role=user,
        user_name="Alex Chen, Esq.",
        action=action,
        target=target,
        status=status,
        details=details
    ))

def process_and_store_contract(title: str, filename: str, file_path: Path, file_size: int, custom_id: Optional[str] = None) -> ContractDetail:
    full_text, sections, total_pages = extract_text_from_file(file_path, filename)

    clauses_list = []
    for sec in sections:
        c_type, conf = classify_clause(sec["title"], sec["text"])
        clause_item = analyze_clause_risk_and_xai(c_type, sec["title"], sec["text"], sec.get("page_number", 1), sec.get("section_number", "1"))
        clause_item.confidence = conf
        clauses_list.append(clause_item)

    entities = extract_entities_from_contract(full_text, sections)
    overall_score, overall_level, cat_scores, red_flags, timeline = compute_overall_risk_profile(clauses_list)

    exec_summary = f"Analyzed '{title}' comprising {len(clauses_list)} clauses across {total_pages} pages. Overall Risk Score is {overall_score}/100 ({overall_level.value}) with {len(red_flags)} critical red flags requiring transactional attention."

    cid = custom_id or f"contract_{uuid.uuid4().hex[:8]}"

    detail = ContractDetail(
        id=cid,
        title=title,
        file_name=filename,
        file_type=file_path.suffix.lower(),
        file_size=file_size,
        upload_time=datetime.now().isoformat(),
        total_pages=total_pages,
        total_clauses=len(clauses_list),
        overall_risk_score=overall_score,
        overall_risk_level=overall_level,
        executive_summary=exec_summary,
        clauses=clauses_list,
        entities=entities,
        category_scores=cat_scores,
        red_flags=red_flags,
        timeline_events=timeline,
        raw_text=full_text
    )

    CONTRACTS_DB[cid] = detail
    log_action("CONTRACT_ANALYZED", title, details=f"Risk Score: {overall_score}, Red Flags: {len(red_flags)}")
    return detail

@router.get("", response_model=List[ContractSummary])
def list_contracts():
    res = []
    for cid, c in CONTRACTS_DB.items():
        res.append(ContractSummary(
            id=c.id,
            title=c.title,
            file_name=c.file_name,
            file_type=c.file_type,
            file_size=c.file_size,
            upload_time=c.upload_time,
            total_pages=c.total_pages,
            total_clauses=c.total_clauses,
            overall_risk_score=c.overall_risk_score,
            overall_risk_level=c.overall_risk_level,
            executive_summary=c.executive_summary,
            red_flag_count=len(c.red_flags)
        ))
    return res

@router.get("/{contract_id}", response_model=ContractDetail)
def get_contract(contract_id: str):
    if contract_id not in CONTRACTS_DB:
        raise HTTPException(status_code=404, detail="Contract not found")
    log_action("VIEW_CONTRACT", CONTRACTS_DB[contract_id].title)
    return CONTRACTS_DB[contract_id]

@router.post("/upload", response_model=ContractDetail)
async def upload_contract(file: UploadFile = File(...)):
    content = await file.read()
    file_size = len(content)
    file_path = UPLOAD_DIR / file.filename
    file_path.write_bytes(content)

    title = file.filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()
    return process_and_store_contract(title, file.filename, file_path, file_size)

@router.delete("/{contract_id}")
def delete_contract(contract_id: str):
    if contract_id in CONTRACTS_DB:
        title = CONTRACTS_DB[contract_id].title
        del CONTRACTS_DB[contract_id]
        log_action("DELETE_CONTRACT", title)
        return {"success": True, "message": "Contract deleted"}
    raise HTTPException(status_code=404, detail="Contract not found")

def init_sample_contracts():
    samples = [
        ("msa_001", "Master Services Agreement (MSA)", "sample_msa.txt"),
        ("nda_001", "Mutual Non-Disclosure Agreement (NDA)", "sample_nda.txt"),
        ("vendor_v1", "Cloud Infrastructure Vendor Agreement (V1.0 - Baseline)", "sample_vendor_v1.txt"),
        ("vendor_v2", "Cloud Infrastructure Vendor Agreement (V2.0 - Redlined High Risk)", "sample_vendor_v2.txt")
    ]
    for cid, title, fname in samples:
        s_path = SAMPLE_DIR / fname
        if s_path.exists():
            process_and_store_contract(title, fname, s_path, s_path.stat().st_size, cid)
    print(f"Loaded {len(CONTRACTS_DB)} sample contracts into in-memory store.")
