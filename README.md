# NGS Variant Validator 🧬

[![CI/CD Pipeline](https://github.com/HReed1/ngs-variant-validator/actions/workflows/ci_pipeline.yaml/badge.svg)](#)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)](#)
[![Nextflow](https://img.shields.io/badge/nextflow-DSL2-orange)](#)

## Overview
`ngs-variant-validator` is an automated, CI/CD-driven testing framework and execution environment for scalable sloud-native bioinformatics pipelines. 


## 🏗️ System Architecture

* **Orchestration:** Nextflow (DSL2) executing containerized processes.
* **Compute Engine:** Local Docker daemon (Dev) / AWS Batch via EC2 Spot Instances (Prod).
* **Storage:** PostgreSQL (Metadata & State) / Amazon S3 (Intermediate workflow files).
* **Backend:** FastAPI (Python) serving a strict, read-only view of sanitized run data.
* **Frontend:** React + Vite + TypeScript, utilizing React Query for polling and Apache ECharts for rendering genomic coverage and quality profiles.

## 🚀 Quick Start (Local Development)

### Prerequisites
* Docker & Colima (or Docker Desktop)
* Nextflow (`>=23.04.0`)
* Python 3.11+
* Node.js & npm

### 1. Boot the Infrastructure
Start the PostgreSQL database and the FastAPI backend:

```bash
./utils/start_dev.sh
alembic upgrade head
python -m etl.jobs.seed_database
```
2. Start the UI
In a new terminal, boot the React frontend:

```bash
cd ngs-variant-ui
npm install
npm run dev
```
3. Run the Local Micro-Dataset
Execute the Nextflow pipeline locally using the built-in Docker profile:

```bash
nextflow run src/ont-clinical-pipeline/main.nf --run RUN-VIRAL-TEST
```
## ☁️ AWS Batch Execution
To run heavy datasets (e.g., HG002) in the cloud:

Ensure your AWS CLI is authenticated and your IAM user has AmazonS3FullAccess and the custom NextflowBatchOrchestrator inline policy.

Push your custom Docker images to ECR: ./utils/aws_push_images.sh

Execute the pipeline with the AWS Batch profile:

```bash
nextflow run src/ont-clinical-pipeline/main.nf --run RUN-AWS-HG002 -profile awsbatch
```
## ✉️ Contact
Harrison H. Vaughn Reed Email: [EMAIL_ADDRESS]


---