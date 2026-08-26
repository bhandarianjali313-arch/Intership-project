import uuid
from typing import List
from app.models.schemas import CompareResponse, ClauseDiff, RiskLevel

def compare_contract_versions(c1, c2) -> CompareResponse:
    diffs: List[ClauseDiff] = []
    added = 0
    removed = 0
    modified = 0
    unchanged = 0
    key_takeaways = []

    c1_map = {c.clause_type: c for c in c1.clauses}
    c2_map = {c.clause_type: c for c in c2.clauses}

    all_types = set(list(c1_map.keys()) + list(c2_map.keys()))

    for ctype in all_types:
        v1_clause = c1_map.get(ctype)
        v2_clause = c2_map.get(ctype)

        if v1_clause and not v2_clause:
            removed += 1
            diffs.append(ClauseDiff(
                id=f"diff_{uuid.uuid4().hex[:8]}",
                section_title=v1_clause.title,
                clause_type=ctype,
                status="REMOVED",
                v1_text=v1_clause.text,
                v2_text=None,
                risk_v1=v1_clause.risk_level,
                risk_v2=None,
                risk_delta_summary=f"Clause removed in Version 2 ({v1_clause.title}).",
                risk_changed=True
            ))
            key_takeaways.append(f"➖ Clause '{v1_clause.title}' was completely removed in V2.")

        elif v2_clause and not v1_clause:
            added += 1
            diffs.append(ClauseDiff(
                id=f"diff_{uuid.uuid4().hex[:8]}",
                section_title=v2_clause.title,
                clause_type=ctype,
                status="ADDED",
                v1_text=None,
                v2_text=v2_clause.text,
                risk_v1=None,
                risk_v2=v2_clause.risk_level,
                risk_delta_summary=f"New clause introduced in Version 2. Risk level: {v2_clause.risk_level.value}.",
                risk_changed=True
            ))
            key_takeaways.append(f"➕ New '{v2_clause.title}' clause added with {v2_clause.risk_level.value} risk.")

        else:
            v1_clean = " ".join(v1_clause.text.split()).lower()
            v2_clean = " ".join(v2_clause.text.split()).lower()

            if v1_clean == v2_clean:
                unchanged += 1
                diffs.append(ClauseDiff(
                    id=f"diff_{uuid.uuid4().hex[:8]}",
                    section_title=v2_clause.title,
                    clause_type=ctype,
                    status="UNCHANGED",
                    v1_text=v1_clause.text,
                    v2_text=v2_clause.text,
                    risk_v1=v1_clause.risk_level,
                    risk_v2=v2_clause.risk_level,
                    risk_delta_summary="No material change in clause text or risk profile.",
                    risk_changed=False
                ))
            else:
                modified += 1
                risk_changed = (v1_clause.risk_level != v2_clause.risk_level)
                delta_str = f"Risk changed: {v1_clause.risk_level.value} ➔ {v2_clause.risk_level.value}." if risk_changed else "Text modified with steady risk profile."
                diffs.append(ClauseDiff(
                    id=f"diff_{uuid.uuid4().hex[:8]}",
                    section_title=v2_clause.title,
                    clause_type=ctype,
                    status="MODIFIED",
                    v1_text=v1_clause.text,
                    v2_text=v2_clause.text,
                    risk_v1=v1_clause.risk_level,
                    risk_v2=v2_clause.risk_level,
                    risk_delta_summary=f"{delta_str} {v2_clause.reason}",
                    risk_changed=risk_changed
                ))
                if risk_changed:
                    key_takeaways.append(f"⚠️ {v2_clause.title}: Risk shifted from {v1_clause.risk_level.value} ➔ {v2_clause.risk_level.value}.")

    delta_score = c2.overall_risk_score - c1.overall_risk_score

    return CompareResponse(
        contract_v1_id=c1.id,
        contract_v2_id=c2.id,
        contract_v1_title=c1.title,
        contract_v2_title=c2.title,
        risk_score_v1=c1.overall_risk_score,
        risk_score_v2=c2.overall_risk_score,
        risk_score_delta=delta_score,
        diffs=diffs,
        added_count=added,
        removed_count=removed,
        modified_count=modified,
        unchanged_count=unchanged,
        key_takeaways=key_takeaways or ["No major risk deviations between versions."]
    )
