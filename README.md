# AI-Powered Contract Intelligence and Risk Scoring

An end-to-end Machine Learning and NLP pipeline for analyzing legal contract clauses, identifying clause categories, extracting important entities, estimating clause-level risk, and generating contract-level risk reports.

This project was developed as part of a Data Science and Machine Learning internship project.

---

## Project Overview

Legal contracts contain large amounts of unstructured text and can be difficult to review manually.

The goal of this project is to build an ML-assisted contract intelligence pipeline that can:

- preprocess legal contract data
- classify contract clauses
- extract named entities
- estimate clause-level risk
- identify low-confidence predictions
- recommend human review when necessary
- generate contract-level risk summaries
- validate incoming contract text before analysis

The project uses the CUAD dataset for contract clause classification and combines traditional Machine Learning, transformer-based experiments, Named Entity Recognition, confidence-aware inference, and heuristic risk scoring.

---

## Main Features

### 1. Contract Clause Classification

The system classifies contract clauses into legal categories such as:

- Governing Law
- Anti-Assignment
- Cap on Liability
- Non-Compete
- Exclusivity
- Termination for Convenience
- Audit Rights
- Minimum Commitment
- Renewal Term
- Warranty Duration
- Parties
- Effective Date

The project supports 41 CUAD clause categories.

---

### 2. Named Entity Recognition

A spaCy-based NER pipeline is used to extract useful entities from contract text.

Examples include:

- organizations
- persons
- dates
- locations
- legal roles
- laws
- numeric information

NER post-processing is also used to remove low-value entities and improve entity quality.

---

### 3. Confidence-Aware Prediction

Every clause prediction includes a confidence score.

Predictions are grouped into confidence levels such as:

- HIGH
- MEDIUM
- LOW

Low-confidence or ambiguous predictions can automatically be marked for human review.

This helps avoid blindly trusting uncertain model predictions.

---

### 4. Human Review Recommendation

The system contains a review layer that checks whether a prediction should be manually reviewed.

Human review may be recommended when:

- confidence is low
- prediction margin is small
- the prediction is ambiguous

This provides a safer ML-assisted workflow for contract analysis.

---

### 5. Clause-Level Risk Scoring

Predicted clause categories are mapped to operational risk levels:

- LOW
- MEDIUM
- HIGH

Example:

```text
GOVERNING_LAW → LOW

ANTI_ASSIGNMENT → MEDIUM

NON_COMPETE → HIGH