import re
from typing import Tuple, Dict, Any, List
from app.models.schemas import ClauseType, RiskLevel

CLAUSE_RULES = {
    ClauseType.TERMINATION: {
        "keywords": ["terminate", "termination", "cancel", "cancellation", "cure period", "without cause", "for convenience", "for cause", "notice period", "expiration"],
        "regex": r"\b(terminat|cancel|notice of terminat|cure period|without cause|for cause|convenience)\b"
    },
    ClauseType.LIABILITY: {
        "keywords": ["limitation of liability", "liable", "liability cap", "consequential damages", "indirect damages", "aggregate liability", "punitive damages", "exceed", "disclaimer of liability"],
        "regex": r"\b(limit(ation)? of liability|liabilit(y|ies)|consequential damage|aggregate liability|direct damage|liability cap)\b"
    },
    ClauseType.PAYMENT: {
        "keywords": ["payment", "invoice", "fee", "fees", "rate", "hourly", "compensation", "net 30", "net 60", "net 7", "interest", "late fee", "billing", "taxes"],
        "regex": r"\b(pay(ment)?|invoice|fee|billing|net 30|net 60|net 7|late fee|interest rate|remunerat)\b"
    },
    ClauseType.CONFIDENTIALITY: {
        "keywords": ["confidential", "confidentiality", "proprietary", "trade secret", "non-disclosure", "disclosing party", "receiving party", "permitted purpose"],
        "regex": r"\b(confidential(ity)?|trade secret|proprietary information|non-disclosure|receiving party)\b"
    },
    ClauseType.PRIVACY: {
        "keywords": ["privacy", "personal data", "personally identifiable", "pii", "ccpa", "gdpr", "data subject", "consent", "privacy policy"],
        "regex": r"\b(privacy|personal data|pii|ccpa|gdpr|data subject)\b"
    },
    ClauseType.INTELLECTUAL_PROPERTY: {
        "keywords": ["intellectual property", "ip rights", "patent", "copyright", "trademark", "work made for hire", "source code", "deliverables ownership", "license grant", "background ip"],
        "regex": r"\b(intellectual property|patent|copyright|trademark|work made for hire|work product|ip rights|background ip)\b"
    },
    ClauseType.INDEMNIFICATION: {
        "keywords": ["indemnify", "indemnification", "hold harmless", "defend", "indemnity", "third-party claims", "losses and damages"],
        "regex": r"\b(indemnif(y|ication)|hold harmless|defend, indemnify|indemnity)\b"
    },
    ClauseType.WARRANTY: {
        "keywords": ["warranty", "warranties", "warrants", "as is", "merchantability", "fitness for a particular purpose", "representation", "guarantee"],
        "regex": r"\b(warrant(y|ies|s)?|as is|fitness for a particular purpose|merchantability|representation)\b"
    },
    ClauseType.RENEWAL: {
        "keywords": ["renewal", "renew", "automatic renewal", "evergreen", "successive terms", "opt-out", "extension"],
        "regex": r"\b(renew(al)?|automatic(ally)? renew|evergreen|successive (term|year|period)|opt-out)\b"
    },
    ClauseType.GOVERNING_LAW: {
        "keywords": ["governing law", "jurisdiction", "laws of", "state of", "construed in accordance", "courts of"],
        "regex": r"\b(governing law|laws of the state|construed in accordance with the laws|applicable law)\b"
    },
    ClauseType.DISPUTE_RESOLUTION: {
        "keywords": ["dispute resolution", "arbitration", "arbitrator", "mediation", "jams", "aaa", "litigation", "venue", "court"],
        "regex": r"\b(dispute resolution|arbitrat(ion|or)|mediation|jams|american arbitration|venue)\b"
    },
    ClauseType.NON_COMPETE: {
        "keywords": ["non-compete", "non-competition", "non-solicit", "non-solicitation", "solicitation", "competing business", "restrictive covenant"],
        "regex": r"\b(non-compete|non-competition|non-solicit(ation)?|solicit any employee|restrictive covenant)\b"
    },
    ClauseType.DATA_PROTECTION: {
        "keywords": ["data protection", "security breach", "data breach", "safeguards", "encryption", "iso 27001", "soc 2", "technical and administrative"],
        "regex": r"\b(data protection|security breach|data breach|technical and administrative safeguard|iso 27001|soc 2|encryption)\b"
    },
    ClauseType.FORCE_MAJEURE: {
        "keywords": ["force majeure", "act of god", "natural disaster", "pandemic", "strike", "war", "beyond reasonable control"],
        "regex": r"\b(force majeure|act of god|natural disaster|pandemic|beyond its reasonable control|civil commotion)\b"
    }
}

def classify_clause(title: str, text: str) -> Tuple[ClauseType, float]:
    combined = (title + " " + text).lower()
    best_type = ClauseType.GENERAL
    best_score = 0.0

    for c_type, rules in CLAUSE_RULES.items():
        score = 0.0
        if any(kw in title.lower() for kw in rules["keywords"]):
            score += 0.55

        matches = len(re.findall(rules["regex"], combined, re.IGNORECASE))
        if matches > 0:
            score += min(0.40, matches * 0.12)

        kw_hits = sum(1 for kw in rules["keywords"] if kw in combined)
        score += min(0.25, kw_hits * 0.05)

        if score > best_score:
            best_score = score
            best_type = c_type

    if best_score < 0.20:
        return ClauseType.GENERAL, 0.40

    confidence = round(min(0.98, max(0.55, best_score)), 2)
    return best_type, confidence
