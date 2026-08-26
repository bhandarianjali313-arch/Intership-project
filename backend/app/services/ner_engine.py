import re, uuid
from typing import List
from app.models.schemas import EntityItem, EntityType

def extract_entities_from_contract(full_text: str, sections: list) -> List[EntityItem]:
    entities: List[EntityItem] = []
    seen = set()

    def add_entity(etype: EntityType, text: str, context: str, page: int):
        clean_txt = text.strip().strip(",.;:()\"'")
        if not clean_txt or len(clean_txt) < 2 or len(clean_txt) > 90:
            return
        key = (etype.value, clean_txt.lower())
        if key in seen:
            return
        seen.add(key)
        entities.append(EntityItem(
            id=f"ent_{uuid.uuid4().hex[:8]}",
            entity_type=etype,
            text=clean_txt,
            context=context[:140].strip() + ("..." if len(context) > 140 else ""),
            page_number=page
        ))

    org_pattern = re.compile(r"\b([A-Z][A-Za-z0-9&\.\-\s]{2,40}\b(?:Inc\.?|LLC|Corp\.?|Corporation|Ltd\.?|Limited|Company|Enterprises|Solutions|Labs|Dynamics|Services|Group))\b")
    money_pattern = re.compile(r"(\$[\d,]+(?:\.\d{2})?|\b(?:USD|EUR|GBP)\s+[\d,]+(?:\.\d{2})?|\b[\d,]+\s+dollars\b)", re.IGNORECASE)
    date_pattern = re.compile(r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b|\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b")
    duration_pattern = re.compile(r"\b(\d+|twenty-four|twelve|thirty-six|six|three|ten|ninety|sixty)\s+(?:calendar\s+)?(months?|years?|days?|business days?)\b", re.IGNORECASE)
    payment_terms_pattern = re.compile(r"\b(Net\s+\d+|within\s+\d+\s+days|hourly\s+rate\s+of\s+\$[\d,]+|\d+%\s+(?:per\s+month|annual|daily\s+penalty))\b", re.IGNORECASE)
    jurisdiction_pattern = re.compile(r"\b(?:State of|laws of|courts of|administered by JAMS in)\s+([A-Z][a-zA-Z\s]{2,25})\b|\b(Delaware|California|New York|Texas|England & Wales|Seychelles|London|Singapore)\b")
    person_pattern = re.compile(r"\b(?:By:\s*|Signed by:\s*|Representative:\s*)([A-Z][a-z]+\s+[A-Z][a-z]+(?:,\s*[A-Za-z\s]+)?)")

    for sec in sections:
        txt = sec["text"]
        page = sec.get("page_number", 1)

        for p in person_pattern.findall(txt):
            add_entity(EntityType.PERSON, p, txt, page)

        for org in org_pattern.findall(txt):
            add_entity(EntityType.ORGANIZATION, org, txt, page)

        for m in money_pattern.findall(str(txt)):
            money_txt = m[0] if isinstance(m, tuple) else m
            add_entity(EntityType.MONEY, money_txt, txt, page)

        for d in date_pattern.findall(txt):
            add_entity(EntityType.DATE, d, txt, page)

        for dur in duration_pattern.finditer(txt):
            add_entity(EntityType.DURATION, dur.group(0), txt, page)

        for pt in payment_terms_pattern.findall(txt):
            add_entity(EntityType.PAYMENT_TERM, pt, txt, page)

        for jur in jurisdiction_pattern.findall(txt):
            jur_text = jur[0] if isinstance(jur, tuple) and jur[0] else (jur[1] if isinstance(jur, tuple) else jur)
            if jur_text:
                add_entity(EntityType.JURISDICTION, jur_text, txt, page)

        if "renew" in txt.lower():
            ren_matches = re.findall(r"(\d+\s+(?:days?|months?)\s+prior\s+to\s+(?:the\s+)?expiration)", txt, re.IGNORECASE)
            for rm in ren_matches:
                add_entity(EntityType.RENEWAL_DATE, rm, txt, page)

    return entities
