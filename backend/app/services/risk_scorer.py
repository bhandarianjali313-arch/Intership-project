import uuid, re
from typing import List, Tuple, Dict, Any
from app.models.schemas import (
    ClauseType, RiskLevel, ClauseItem, RiskCategoryScore, RedFlagItem, TimelineEvent
)

CATEGORY_MAPPING = {
    ClauseType.PAYMENT: "Financial Risk",
    ClauseType.LIABILITY: "Liability Risk",
    ClauseType.INDEMNIFICATION: "Liability Risk",
    ClauseType.TERMINATION: "Termination Risk",
    ClauseType.PRIVACY: "Privacy Risk",
    ClauseType.DATA_PROTECTION: "Privacy Risk",
    ClauseType.INTELLECTUAL_PROPERTY: "IP Risk",
    ClauseType.WARRANTY: "Compliance Risk",
    ClauseType.FORCE_MAJEURE: "Compliance Risk",
    ClauseType.CONFIDENTIALITY: "Confidentiality Risk",
    ClauseType.NON_COMPETE: "Confidentiality Risk",
    ClauseType.RENEWAL: "Renewal Risk",
    ClauseType.GOVERNING_LAW: "Jurisdiction Risk",
    ClauseType.DISPUTE_RESOLUTION: "Jurisdiction Risk",
    ClauseType.GENERAL: "Compliance Risk"
}

def analyze_clause_risk_and_xai(c_type: ClauseType, title: str, text: str, page: int, sec_num: str) -> ClauseItem:
    txt_lower = text.lower()
    risk_level = RiskLevel.LOW
    reason = "Standard contractual wording aligned with customary commercial terms."
    impact = "Low operational or financial exposure under normal business operations."
    recommendation = "Maintain clause as currently drafted."
    evidence_quote = text[:180].strip() + ("..." if len(text) > 180 else "")

    if c_type == ClauseType.TERMINATION:
        if any(x in txt_lower for x in ["7 days", "immediate termination without cause", "prohibited from terminating", "unilateral"]):
            risk_level = RiskLevel.CRITICAL if "prohibited" in txt_lower else RiskLevel.HIGH
            reason = "The contract allows unilateral termination with extremely short notice (7 days) or restricts customer exit rights."
            impact = "Creates acute business disruption, lock-in vulnerability, and sudden service loss."
            recommendation = "Negotiate a minimum 30 to 60 days mutual termination notice period with transition support."
        elif "15 days" in txt_lower or "immediate" in txt_lower:
            risk_level = RiskLevel.MEDIUM
            reason = "Termination notice window is slightly compressed (15 days)."
            impact = "Requires accelerated transition planning in event of dispute."
            recommendation = "Request extending notice period to 30 days."

    elif c_type == ClauseType.LIABILITY:
        if any(x in txt_lower for x in ["unlimited liability", "no cap", "no monetary ceiling", "strictly limited to $100"]):
            risk_level = RiskLevel.CRITICAL
            reason = "Contract imposes unlimited liability or establishes an egregious asymmetric ceiling ($100 cap for vendor)."
            impact = "Catastrophic financial exposure in case of data breach, infringement, or operational downtime."
            recommendation = "Cap liability strictly to 12 months fees paid or an industry-standard aggregate amount ($500,000)."
        elif "indirect" not in txt_lower or "consequential" not in txt_lower or "exceed" not in txt_lower:
            risk_level = RiskLevel.MEDIUM
            reason = "Consequential or indirect damages waiver is unclear or missing."
            impact = "Potential exposure to unpredictable indirect financial claims."
            recommendation = "Ensure express exclusion of special, incidental, and consequential damages."

    elif c_type == ClauseType.PAYMENT:
        if any(x in txt_lower for x in ["10% daily", "increase fees up to 100%", "unilateral price increase", "net 7"]):
            risk_level = RiskLevel.CRITICAL if "100%" in txt_lower else RiskLevel.HIGH
            reason = "Aggressive payment terms detected (Net 7, 10% daily compounding penalty, or uncontrolled price increases)."
            impact = "Severe cash flow risk, unpredictable price escalation, and punitive interest liabilities."
            recommendation = "Standardize to Net 30, cap late interest to statutory 1-1.5%/month, and cap annual price increases to CPI."
        elif "net 60" in txt_lower or "net 45" in txt_lower:
            risk_level = RiskLevel.MEDIUM
            reason = "Extended payment terms."
            impact = "May slightly strain working capital."
            recommendation = "Negotiate Net 30 terms."

    elif c_type == ClauseType.INTELLECTUAL_PROPERTY:
        if any(x in txt_lower for x in ["train ai models on", "irrevocable, perpetual, worldwide", "transfer all customer proprietary", "exclusive license to vendor"]):
            risk_level = RiskLevel.CRITICAL
            reason = "Unilateral transfer or perpetual data mining license granted over proprietary assets and AI models."
            impact = "Complete forfeiture of core intellectual property and competitive trade secret leakage."
            recommendation = "Strictly retain all IP ownership; limit vendor rights to temporary processing license only."
        elif "work made for hire" not in txt_lower and "ownership" in txt_lower:
            risk_level = RiskLevel.MEDIUM
            reason = "Deliverables ownership transfer language lacks express Work Made for Hire assignment."
            impact = "Ambiguity regarding developer background IP rights."
            recommendation = "Include express assignment clause for all custom deliverables."

    elif c_type in [ClauseType.DATA_PROTECTION, ClauseType.PRIVACY]:
        if any(x in txt_lower for x in ["no representations or warranties", "assumes all risk of data breaches", "no security compliance"]):
            risk_level = RiskLevel.CRITICAL
            reason = "Total disclaimer of data security obligations and breach liability."
            impact = "Massive regulatory exposure under GDPR/CCPA with no vendor recourse during security breaches."
            recommendation = "Mandate ISO 27001 / SOC 2 Type II compliance and prompt breach notice (within 48h)."
        elif "gdpr" not in txt_lower and "ccpa" not in txt_lower:
            risk_level = RiskLevel.MEDIUM
            reason = "Explicit data privacy regulatory compliance frameworks not mentioned."
            impact = "Potential compliance gap under global privacy statutes."
            recommendation = "Attach a standardized Data Processing Addendum (DPA)."

    elif c_type == ClauseType.RENEWAL:
        if any(x in txt_lower for x in ["thirty-six (36) month", "180 days", "notarized opt-out"]):
            risk_level = RiskLevel.HIGH
            reason = "Onerous 3-year auto-renewal lock-in with burdensome 180-day notarized opt-out requirement."
            impact = "Inability to terminate underperforming vendor without heavy financial penalty."
            recommendation = "Change to annual renewal with standard 30-day email non-renewal notice."

    elif c_type in [ClauseType.GOVERNING_LAW, ClauseType.DISPUTE_RESOLUTION]:
        if any(x in txt_lower for x in ["seychelles", "offshore", "sole expense"]):
            risk_level = RiskLevel.HIGH
            reason = "Governing law set in an offshore jurisdiction requiring overseas dispute resolution at sole expense."
            impact = "Prohibitive legal costs to enforce rights or defend against frivolous claims."
            recommendation = "Change governing law and venue to a recognized neutral jurisdiction (e.g., Delaware or New York)."

    elif c_type == ClauseType.INDEMNIFICATION:
        if any(x in txt_lower for x in ["unlimited indemnity", "assume unlimited", "regulatory fines"]):
            risk_level = RiskLevel.CRITICAL
            reason = "One-sided, un-capped indemnification obligating client to cover regulatory fines and open-ended claims."
            impact = "Severe financial risk covering vendor's independent regulatory failures."
            recommendation = "Make indemnification strictly mutual and limited to third-party IP infringement."

    return ClauseItem(
        id=f"cls_{uuid.uuid4().hex[:8]}",
        clause_type=c_type,
        title=title,
        text=text,
        page_number=page,
        section_number=sec_num,
        risk_level=risk_level,
        confidence=0.92,
        reason=reason,
        impact=impact,
        recommendation=recommendation,
        evidence_quote=evidence_quote
    )

def compute_overall_risk_profile(clauses: List[ClauseItem]) -> Tuple[int, RiskLevel, List[RiskCategoryScore], List[RedFlagItem], List[TimelineEvent]]:
    WEIGHTS = {
        RiskLevel.LOW: 10,
        RiskLevel.MEDIUM: 35,
        RiskLevel.HIGH: 70,
        RiskLevel.CRITICAL: 95
    }

    category_buckets: Dict[str, List[ClauseItem]] = {
        "Financial Risk": [],
        "Liability Risk": [],
        "Termination Risk": [],
        "Privacy Risk": [],
        "IP Risk": [],
        "Compliance Risk": [],
        "Confidentiality Risk": [],
        "Renewal Risk": [],
        "Jurisdiction Risk": []
    }

    red_flags: List[RedFlagItem] = []
    timeline_events: List[TimelineEvent] = []

    for c in clauses:
        cat_name = CATEGORY_MAPPING.get(c.clause_type, "Compliance Risk")
        category_buckets[cat_name].append(c)

        if c.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            red_flags.append(RedFlagItem(
                id=f"rf_{uuid.uuid4().hex[:8]}",
                title=f"{c.title}",
                severity=c.risk_level,
                category=cat_name,
                clause_title=c.title,
                page_number=c.page_number,
                summary=c.reason,
                recommendation=c.recommendation
            ))

        if c.clause_type in [ClauseType.TERMINATION, ClauseType.RENEWAL, ClauseType.PAYMENT]:
            t_match = re.search(r"(\d+\s+(?:days?|months?|years?))", c.text, re.IGNORECASE)
            if t_match:
                timeline_events.append(TimelineEvent(
                    date=t_match.group(1),
                    title=f"{c.clause_type.value} Window",
                    description=f"{c.title}: {c.reason[:80]}...",
                    clause_ref=c.section_number
                ))

    category_scores: List[RiskCategoryScore] = []
    cat_weights = []

    for cat_name, items in category_buckets.items():
        if not items:
            score = 15
            r_level = RiskLevel.LOW
            desc = "Standard low exposure; no adverse terms identified."
            findings = ["Standard clauses apply."]
        else:
            item_scores = [WEIGHTS[item.risk_level] for item in items]
            score = int(sum(item_scores) / len(item_scores))
            if any(item.risk_level == RiskLevel.CRITICAL for item in items):
                score = max(score, 88)
            elif any(item.risk_level == RiskLevel.HIGH for item in items):
                score = max(score, 68)

            if score <= 25:
                r_level = RiskLevel.LOW
                desc = "Terms are within normal commercial risk parameters."
            elif score <= 50:
                r_level = RiskLevel.MEDIUM
                desc = "Contains moderate terms requiring operational attention."
            elif score <= 75:
                r_level = RiskLevel.HIGH
                desc = "Significant risk exposure that deviates from market standard."
            else:
                r_level = RiskLevel.CRITICAL
                desc = "Critical legal/financial exposure requiring mandatory remediation."

            findings = [f"{it.title}: {it.reason}" for it in items if it.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]
            if not findings:
                findings = [f"{items[0].title}: Customary terms accepted."]

        category_scores.append(RiskCategoryScore(
            category=cat_name,
            score=score,
            risk_level=r_level,
            description=desc,
            key_findings=findings
        ))
        cat_weights.append(score)

    overall_score = int(sum(cat_weights) / len(cat_weights))
    if any(c.risk_level == RiskLevel.CRITICAL for c in clauses):
        overall_score = max(overall_score, 82)
    elif any(c.risk_level == RiskLevel.HIGH for c in clauses):
        overall_score = max(overall_score, 62)

    if overall_score <= 25:
        overall_risk_level = RiskLevel.LOW
    elif overall_score <= 50:
        overall_risk_level = RiskLevel.MEDIUM
    elif overall_score <= 75:
        overall_risk_level = RiskLevel.HIGH
    else:
        overall_risk_level = RiskLevel.CRITICAL

    return overall_score, overall_risk_level, category_scores, red_flags, timeline_events
