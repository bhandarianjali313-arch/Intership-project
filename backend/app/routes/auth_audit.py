import uuid
from typing import List
from fastapi import APIRouter
from app.models.schemas import AuditLog, UserLoginRequest, UserLoginResponse
from app.routes.contracts import AUDIT_LOGS, log_action

router = APIRouter()

@router.get("/audit-logs", response_model=List[AuditLog])
def get_audit_logs():
    return AUDIT_LOGS

@router.post("/auth/login", response_model=UserLoginResponse)
def login(req: UserLoginRequest):
    role = req.role or "Legal Counsel"
    log_action("USER_LOGIN", req.email, user=role, details=f"Role: {role}")
    return UserLoginResponse(
        token=f"token_legis_esq_{uuid.uuid4().hex[:8]}",
        user={
            "email": req.email,
            "name": "Alex Chen, Esq.",
            "role": role,
            "organization": "LexiGuard Enterprise Labs"
        }
    )
