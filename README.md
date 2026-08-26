# 🚀 LexiGuard AI — AI-Powered Contract Intelligence & Risk Scoring Platform

An enterprise LegalTech platform combining **Natural Language Processing (NLP)**, **CUAD-aligned Clause Segmentation**, **Legal Named Entity Recognition (NER)**, **0–100 Multi-Dimensional Risk Scoring**, **Explainable AI (XAI)**, **RAG Contract Q&A with Verified Citations**, and **Side-by-Side Version Diffing & Risk Delta Tracking**.

---

## 🌟 Key Capabilities

1. **Multi-Format Ingestion**:
   - Parses **PDF**, **DOCX**, **TXT**, and Markdown agreements.
   - Automatically segments clauses by Article/Section and tracks physical page numbering.

2. **14-Category Clause Detection (CUAD Aligned)**:
   - *Termination*, *Liability*, *Payment*, *Confidentiality*, *Privacy*, *Intellectual Property*, *Indemnification*, *Warranty*, *Renewal*, *Governing Law*, *Dispute Resolution*, *Non-compete*, *Data Protection*, and *Force Majeure*.

3. **Legal Named Entity Recognition (NER)**:
   - Extracts *Parties/Organizations*, *Signatories*, *Monetary Values*, *Dates*, *Jurisdictions*, *Durations*, *Notice Windows*, and *Payment Terms*.

4. **Explainable AI (XAI) Risk Scoring (0–100 Scale)**:
   - Computes granular risk scores across **9 dimensions**: Financial, Liability, Termination, Privacy, IP, Compliance, Confidentiality, Renewal, and Jurisdiction.
   - Every risky clause receives structured **Reasoning**, **Business/Legal Impact**, **Actionable Remediation**, and **Exact Page Evidence**.

5. **RAG Contract Conversational Assistant**:
   - Ask any natural language question about agreements.
   - Returns responses strictly grounded in the document with **Section & Page Citations**.
   - Handles missing evidence with honest fallbacks (*"I could not find sufficient evidence in this contract"*).

6. **Side-by-Side Version Diff & Risk Delta Engine**:
   - Compares Version 1 vs Version 2 (e.g., Baseline vs Redlined SaaS agreements).
   - Classifies modifications into `ADDED`, `REMOVED`, `MODIFIED`, `UNCHANGED`.
   - Tracks net **Risk Score Deltas** (e.g. +63 surge when unilateral clauses are added).

7. **Institutional Report Generator**:
   - One-click export to **Printable PDF/HTML** and **Structured JSON**.

8. **Governance & Audit Trail**:
   - Full immutable log of document uploads, AI queries, redlines, and exports with RBAC role switching.

---

## 📁 Repository Structure

```
legaltech-ai-platform/
├── backend/
│   ├── app/
│   │   ├── models/schemas.py       # Pydantic schemas (RiskLevel, ClauseItem, Diff, etc.)
│   │   ├── routes/
│   │   │   ├── contracts.py        # CRUD, upload, preloaded sample store
│   │   │   ├── chat.py             # RAG Q&A & Semantic search
│   │   │   ├── compare.py          # Version 1 vs Version 2 diffing
│   │   │   ├── reports.py          # PDF/HTML and JSON report generator
│   │   │   └── auth_audit.py       # Security logs & RBAC login
│   │   ├── services/
│   │   │   ├── extractor.py        # PDF/DOCX/TXT parser & section segmenter
│   │   │   ├── clause_detector.py  # 14 CUAD clause classifier
│   │   │   ├── ner_engine.py       # Legal entity extractor
│   │   │   ├── risk_scorer.py      # 0-100 risk scorer & XAI generator
│   │   │   ├── rag_search.py       # BM25 + keyword citation search
│   │   │   ├── diff_engine.py      # Redline diffing & delta calculator
│   │   │   └── report_generator.py # Multi-format export builder
│   │   ├── sample_data/            # Preloaded MSA, NDA, Vendor V1 & V2 contracts
│   │   ├── config.py               # Settings & CORS config
│   │   └── main.py                 # FastAPI application
│   ├── tests/
│   │   └── test_engine.py          # Automated backend test suite
│   ├── Dockerfile
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/             # RiskBadge, ScoreGauge, RiskRadarChart, ClauseCard, etc.
│   │   ├── pages/                  # Dashboard, AnalysisWorkspace, Chat, Diff, Search, Reports, Audit
│   │   ├── services/api.ts         # Axios API client
│   │   ├── types/contract.ts       # TypeScript contract interfaces
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docker-compose.yml
├── start_all.bat
└── README.md
```

---

## ⚡ Quick Start (Windows / Mac / Linux)

### Option 1: One-Click Windows Launcher
Double-click `start_all.bat` or run:
```cmd
start_all.bat
```

### Option 2: Run Manually

#### 1. Start Backend:
```bash
cd backend
python -m pip install -r requirements.txt
python run.py
```
*API will run at `http://localhost:8000` (Docs at `http://localhost:8000/docs`).*

#### 2. Start Frontend:
```bash
cd frontend
npm install
npm run dev
```
*Frontend will run at `http://localhost:5173`.*

### Option 3: Docker Compose
```bash
docker-compose up --build
```
*Access web interface at `http://localhost:5173`.*

---

## 🧪 Running Automated Unit Tests
```bash
cd backend
python tests/test_engine.py
```
