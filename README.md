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
├── .github/workflows/          # CI/CD pipelines for automated linting and pytest execution
├── infrastructure/aws/iam/     # Cloud security and deployment configurations
├── src/ont-clinical-pipeline/  # The core Nextflow DAG and Python I/O middleware
├── tests/                      # Automated unit and integration test suite (pytest)
├── db/                         # PostgreSQL schema definitions and migrations
├── docker-compose.yml          # Local database deployment for reproducible development
└── requirements.txt            # Python dependencies
```

## Quick Start
1. Spin up the local database:

```Bash
docker-compose up -d
```
2. Run the automated test suite:

```Bash
pytest tests/ -v
```

3. Execute a dry-run of the pipeline:

```Bash
nextflow run src/ont-clinical-pipeline/main.nf --sample SRR11032656 -profile standard
```


## Contact

Harrison H. Vaughn Reed  | Bioinformatics Software Engineer