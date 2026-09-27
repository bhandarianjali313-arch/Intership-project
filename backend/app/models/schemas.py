from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ClauseType(str, Enum):
    TERMINATION = "Termination"
    LIABILITY = "Liability"
    PAYMENT = "Payment"
    CONFIDENTIALITY = "Confidentiality"
    PRIVACY = "Privacy"
    INTELLECTUAL_PROPERTY = "Intellectual Property"
    INDEMNIFICATION = "Indemnification"
    WARRANTY = "Warranty"
    RENEWAL = "Renewal"
    GOVERNING_LAW = "Governing Law"
    DISPUTE_RESOLUTION = "Dispute Resolution"
    NON_COMPETE = "Non-compete"
    DATA_PROTECTION = "Data Protection"
    FORCE_MAJEURE = "Force Majeure"
    GENERAL = "General Provisions"

class EntityType(str, Enum):
    PERSON = "Person"
    ORGANIZATION = "Organization"
    DATE = "Date"
    MONEY = "Monetary Value"
    LOCATION = "Location"
    JURISDICTION = "Jurisdiction"
    DURATION = "Contract Duration"
    RENEWAL_DATE = "Renewal Date"
    PAYMENT_TERM = "Payment Term"

class ClauseItem(BaseModel):
    id: str
    clause_type: ClauseType
    title: str
    text: str
    page_number: int
    section_number: str
    risk_level: RiskLevel
    confidence: float
    reason: str
    impact: str
    recommendation: str
    evidence_quote: str

class EntityItem(BaseModel):
    id: str
    entity_type: EntityType
    text: str
    context: str
    page_number: int

class RiskCategoryScore(BaseModel):
    category: str
    score: int
    risk_level: RiskLevel
    description: str
    key_findings: List[str]

class RedFlagItem(BaseModel):
    id: str
    title: str
    severity: RiskLevel
    category: str
    clause_title: str
    page_number: int
    summary: str
    recommendation: str

class TimelineEvent(BaseModel):
    date: str
    title: str
    description: str
    clause_ref: str

class ContractSummary(BaseModel):
    id: str
    title: str
    file_name: str
    file_type: str
    file_size: int
    upload_time: str
    total_pages: int
    total_clauses: int
    overall_risk_score: int
    overall_risk_level: RiskLevel
    executive_summary: str
    red_flag_count: int

class ContractDetail(BaseModel):
    id: str
    title: str
    file_name: str
    file_type: str
    file_size: int
    upload_time: str
    total_pages: int
    total_clauses: int
    overall_risk_score: int
    overall_risk_level: RiskLevel
    executive_summary: str
    clauses: List[ClauseItem]
    entities: List[EntityItem]
    category_scores: List[RiskCategoryScore]
    red_flags: List[RedFlagItem]
    timeline_events: List[TimelineEvent]
    raw_text: Optional[str] = ""

class Citation(BaseModel):
    page_number: int
    section_number: str
    section_title: str
    quote: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
    confidence: float
    has_sufficient_evidence: bool

class ClauseDiff(BaseModel):
    id: str
    section_title: str
    clause_type: ClauseType
    status: str
    v1_text: Optional[str] = None
    v2_text: Optional[str] = None
    risk_v1: Optional[RiskLevel] = None
    risk_v2: Optional[RiskLevel] = None
    risk_delta_summary: str
    risk_changed: bool

class CompareRequest(BaseModel):
    contract_id_v1: str
    contract_id_v2: str

class CompareResponse(BaseModel):
    contract_v1_id: str
    contract_v2_id: str
    contract_v1_title: str
    contract_v2_title: str
    risk_score_v1: int
    risk_score_v2: int
    risk_score_delta: int
    diffs: List[ClauseDiff]
    added_count: int
    removed_count: int
    modified_count: int
    unchanged_count: int
    key_takeaways: List[str]

class SearchResultItem(BaseModel):
    contract_id: str
    contract_title: str
    clause_id: str
    clause_title: str
    clause_type: ClauseType
    page_number: int
    section_number: str
    snippet: str
    similarity_score: float
    risk_level: RiskLevel

class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResultItem]

class AuditLog(BaseModel):
    id: str
    timestamp: str
    user_role: str
    user_name: str
    action: str
    target: str
    status: str
    details: str

class UserLoginRequest(BaseModel):
    email: str
    password: str
    role: Optional[str] = "Legal Counsel"

class UserLoginResponse(BaseModel):
    token: str
    user: Dict[str, Any]
