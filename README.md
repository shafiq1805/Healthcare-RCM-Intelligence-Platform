# Healthcare RCM Intelligence Platform

An end-to-end healthcare Revenue Cycle Management platform combining:

- Data Engineering
- Data Quality
- SQL Analytics
- Machine Learning
- Clinical Retrieval
- Evidence-Grounded Coding Support
- Multi-Agent Workflow Orchestration
- FastAPI
- Streamlit

## Architecture

Raw Healthcare Data
↓
Bronze Ingestion
↓
Data Quality Validation
↓
Silver Transformation
↓
Gold Analytics Layer
↓
SQL Warehouse
↓
Claims Validation
↓
Denial Risk Prediction
↓
Clinical Retrieval
↓
Coding Retrieval
↓
Coding Validation
↓
RCM Orchestrator
↓
FastAPI
↓
Streamlit Dashboard

## Data Engineering

The platform uses a medallion-style architecture:

### Raw
Original synthetic source files.

### Bronze
Raw records with ingestion metadata including:

- source file
- ingestion timestamp
- batch ID
- source row number

### Silver
Cleaned and standardized healthcare datasets.

### Gold
Business-ready datasets including:

- claim summary
- denial summary
- payer performance
- patient utilization
- claim validation report
- denial ML dataset

## Core Healthcare Datasets

- Patients
- Providers
- Encounters
- Claims
- Claim Lines
- Clinical Notes
- Denials

## Data Quality

Validation includes:

- Null primary keys
- Duplicate primary keys
- Invalid dates
- Invalid monetary values
- Foreign-key integrity
- Claim-status validation

## Claims Validation

Individual claims are checked for:

- valid patient
- valid provider
- valid encounter
- claim lines
- claim amount consistency
- payment consistency

## Denial Prediction

A Random Forest model predicts claim denial risk using features such as:

- claim amount
- claim-line count
- payer
- provider specialty
- encounter type
- submission delay
- authorization status
- documentation completeness

Output includes:

- denial probability
- LOW / MEDIUM / HIGH risk
- explainable risk factors

## Clinical Retrieval

Clinical notes are retrieved using TF-IDF and cosine similarity.

Answers remain linked to:

- note ID
- patient ID
- encounter ID
- supporting clinical evidence

## Coding Support

The coding workflow combines:

Clinical Evidence
+
Reference Code Retrieval
+
Coding Suggestion
+
Validation Guardrail

The system does not rely on unsupported code generation.

## Multi-Agent Workflow

The orchestrator coordinates:

1. Claim Validation
2. Denial Prediction
3. Denial Explanation
4. Clinical Retrieval
5. Coding Retrieval
6. Coding Validation

Workflow outcomes include:

- SUCCESS
- STOPPED
- MANUAL_REVIEW

## API

Run:

```bash
uvicorn src.api.main:app --reload