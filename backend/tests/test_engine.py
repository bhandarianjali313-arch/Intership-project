import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.clause_detector import classify_clause, ClauseType
from app.services.ner_engine import extract_entities_from_contract
from app.services.risk_scorer import analyze_clause_risk_and_xai, compute_overall_risk_profile, RiskLevel
from app.services.rag_search import answer_contract_question
from app.services.diff_engine import compare_contract_versions

def test_clause_detection():
    ctype, conf = classify_clause("Termination for Convenience", "Either party may terminate upon 30 days notice.")
    assert ctype == ClauseType.TERMINATION, f"Expected Termination, got {ctype}"
    print("✅ 1. Clause Detection Passed")

def test_ner_extraction():
    txt = "Acme Corp agrees to pay $500,000 by January 15, 2026 in Delaware. Signed by Sarah Jenkins."
    ents = extract_entities_from_contract(txt, [{"text": txt, "page_number": 1}])
    etypes = {e.entity_type.value for e in ents}
    assert "Monetary Value" in etypes or "Date" in etypes, "NER failed"
    print("✅ 2. NER Entity Extraction Passed")

def test_rag_qa_and_citations():
    cl = analyze_clause_risk_and_xai(ClauseType.LIABILITY, "Limitation of Liability", "Liability is capped at $100,000.", 1, "Sec 8")
    res = answer_contract_question("Test MSA", [cl], "what is the liability cap?")
    assert res.has_sufficient_evidence, "RAG failed evidence check"
    assert len(res.citations) > 0, "Expected citations"
    print("✅ 3. RAG Q&A with Citations Passed")

if __name__ == "__main__":
    test_clause_detection()
    test_ner_extraction()
    test_rag_qa_and_citations()
    print("\n🚀 All Backend Unit Tests Passed Successfully!")
