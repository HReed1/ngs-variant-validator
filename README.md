# ngs-variant-validator 🧬

[![CI/CD Pipeline](https://img.shields.io/badge/build-passing-brightgreen)](#)
[![pytest](https://img.shields.io/badge/pytest-passing-blue)](#)
[![Nextflow](https://img.shields.io/badge/nextflow-DSL2-orange)](#)
[![AWS Batch](https://img.shields.io/badge/deployed-AWS_Batch-yellow)](#)

## Overview
`ngs-variant-validator` is an automated, CI/CD-driven testing framework and execution environment for a clinical-grade Oxford Nanopore (ONT) Whole-Genome Sequencing (WGS) pipeline. 

Designed with stringent Software Development Life Cycle (SDLC) best practices, this repository demonstrates how to bridge the gap between biological research and enterprise software engineering. It features a fully containerized Nextflow architecture, decoupled database I/O using PostgreSQL, and a rigorous automated testing suite capable of mocking external dependencies and validating analytical outputs.

## 🏗️ System Architecture & Repository Structure

This codebase is strictly modular, separating core bioinformatics logic from cloud infrastructure and database management.

```text
ngs-variant-validator/
├── api/                        # FastAPI backend for serving pipeline results (with PHI hidden)
├── db-init/                    # PostgreSQL schema, security roles & views, and triggers
├── etl/                        # Data loading and seeding scripts for pipeline events
├── .github/workflows/          # CI/CD pipelines (flake8 linting, pytest with Postgres service)
├── infrastructure/aws/iam/     # Cloud security and deployment configurations
├── src/ont-clinical-pipeline/  # The core Nextflow DAG and Python I/O middleware
├── tests/                      # Automated unit and integration test suite (pytest)
├── docker-compose.yml          # Local database deployment for reproducible development
└── requirements.txt            # Python dependencies
```

## 🔒 Security & Database Architecture

The system uses a PostgreSQL backend with strict role-based access control (RBAC):
- **ETL Worker Role (`etl_worker`)**: Has full access to the base `samples` table, including Protected Health Information (PHI) like `patient_id`. Used by the Nextflow pipeline to log results.
- **Frontend API Role (`frontend_api`)**: Can only access the `frontend_samples` View. The view explicitly excludes the `patient_id` column, ensuring the FastAPI backend physically cannot query or leak PHI, even in the event of a vulnerability. Database triggers automatically manage timestamps.

## Quick Start
1. Install dependencies, create a virtual environment, and spin up the local database:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
docker-compose up -d pipeline-db
```

2. Run the automated test suite:

```bash
pytest tests/ -v
```

3. (Optional) Run the API locally:

```bash
fastapi dev api/main.py
```


## Contact

Harrison H. Vaughn Reed  | Bioinformatics Software Engineer | Contact: HarrisonHVReed@gmail.com
