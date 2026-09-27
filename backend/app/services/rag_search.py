import re, math
from typing import List, Tuple, Any
from app.models.schemas import Citation, ChatResponse, SearchResultItem

def compute_bm25_score(query_tokens: List[str], doc_tokens: List[str], avgdl: float, k1: float = 1.5, b: float = 0.75) -> float:
    score = 0.0
    doc_len = len(doc_tokens)
    for q in query_tokens:
        if q in doc_tokens:
            tf = doc_tokens.count(q)
            idf = 1.0
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * (doc_len / (avgdl + 1e-5)))
            score += idf * (numerator / (denominator + 1e-5))
    return score

def answer_contract_question(contract_title: str, clauses: list, query: str) -> ChatResponse:
    q_clean = query.lower()
    q_tokens = [w for w in re.findall(r"\w+", q_clean) if len(w) > 2]

    if not q_tokens or not clauses:
        return ChatResponse(
            answer="I could not find sufficient evidence in this contract regarding your query.",
            citations=[],
            confidence=0.0,
            has_sufficient_evidence=False
        )

    all_lengths = [len(c.text.split()) for c in clauses]
    avgdl = sum(all_lengths) / (len(all_lengths) + 1e-5)

    scored_clauses: List[Tuple[float, Any]] = []
    for c in clauses:
        c_tokens = re.findall(r"\w+", (c.title + " " + c.text).lower())
        bm25 = compute_bm25_score(q_tokens, c_tokens, avgdl)

        intent_boost = 0.0
        if "terminate" in q_clean or "cancel" in q_clean or "notice" in q_clean:
            if c.clause_type.value == "Termination":
                intent_boost += 3.5
        if "liability" in q_clean or "damages" in q_clean or "cap" in q_clean:
            if c.clause_type.value == "Liability":
                intent_boost += 3.5
        if "pay" in q_clean or "invoice" in q_clean or "fee" in q_clean or "rate" in q_clean:
            if c.clause_type.value == "Payment":
                intent_boost += 3.5
        if "ip" in q_clean or "intellectual property" in q_clean or "own" in q_clean or "deliverable" in q_clean:
            if c.clause_type.value == "Intellectual Property":
                intent_boost += 3.5
        if "renew" in q_clean or "extension" in q_clean or "evergreen" in q_clean:
            if c.clause_type.value == "Renewal":
                intent_boost += 3.5
        if "law" in q_clean or "jurisdiction" in q_clean or "dispute" in q_clean or "court" in q_clean or "arbitration" in q_clean:
            if c.clause_type.value in ["Governing Law", "Dispute Resolution"]:
                intent_boost += 3.5

        final_score = bm25 + intent_boost
        if final_score > 0.6:
            scored_clauses.append((final_score, c))

    scored_clauses.sort(key=lambda x: x[0], reverse=True)

    if not scored_clauses:
        return ChatResponse(
            answer="I could not find sufficient evidence in this contract regarding your query.",
            citations=[],
            confidence=0.15,
            has_sufficient_evidence=False
        )

    best_match = scored_clauses[0][1]
    top_matches = [item[1] for item in scored_clauses[:2]]

    citations = [
        Citation(
            page_number=m.page_number,
            section_number=m.section_number,
            section_title=m.title,
            quote=m.text[:220].strip() + ("..." if len(m.text) > 220 else "")
        )
        for m in top_matches
    ]

    answer = f"Based on **Section {best_match.section_number} ({best_match.title})** on **Page {best_match.page_number}** of *{contract_title}*:\n\n"
    answer += f"📌 **Key Provision:** {best_match.text[:300]}\n\n"
    answer += f"⚠️ **Risk Assessment:** {best_match.risk_level.value} Risk — {best_match.reason}\n\n"
    answer += f"💡 **Actionable Recommendation:** {best_match.recommendation}"

    return ChatResponse(
        answer=answer,
        citations=citations,
        confidence=round(min(0.96, 0.65 + scored_clauses[0][0] * 0.05), 2),
        has_sufficient_evidence=True
    )

def perform_semantic_search(query: str, all_contracts: list) -> List[SearchResultItem]:
    results = []
    q_clean = query.lower()
    q_tokens = [w for w in re.findall(r"\w+", q_clean) if len(w) > 2]
    if not q_tokens:
        return []

    for contract in all_contracts:
        for clause in contract.clauses:
            combined = (clause.title + " " + clause.text).lower()
            matches = sum(1 for q in q_tokens if q in combined)
            if matches > 0:
                sim = min(0.98, round(0.40 + (matches / len(q_tokens)) * 0.55, 2))
                snippet = clause.text[:240].strip() + "..."
                results.append(SearchResultItem(
                    contract_id=contract.id,
                    contract_title=contract.title,
                    clause_id=clause.id,
                    clause_title=clause.title,
                    clause_type=clause.clause_type,
                    page_number=clause.page_number,
                    section_number=clause.section_number,
                    snippet=snippet,
                    similarity_score=sim,
                    risk_level=clause.risk_level
                ))

    results.sort(key=lambda x: x.similarity_score, reverse=True)
    return results
