# GitHub Actions Workflows

This directory contains the continuous integration and continuous deployment (CI/CD) pipelines for the `ngs-variant-validator` project. These workflows run automatically on GitHub Actions.

## Available Workflows

### 1. Backend Architecture CI (`ci_pipeline.yaml`)
Triggered on **push** and **pull_request** to the `main` branch. This pipeline ensures the stability, security, and correctness of the backend architecture and frontend UI.

It is split into three main jobs:
- **SAST & Dependency Scanning (`security-scans`)**: Runs `pip-audit` to detect known dependency CVEs and uses `bandit` to perform Static Application Security Testing (SAST) on the core `api/`, `etl/`, and `src/` directories.
- **Backend Tests (`test-and-coverage`)**: Spins up a PostgreSQL 16 service container, initializes database roles & triggers, runs Alembic migrations, and executes the backend Pytest suite with code coverage tracking.
- **React UI Tests (`ui-tests`)**: Navigates to the `ngs-variant-ui` directory, installs NPM dependencies using Node.js 20, and runs frontend tests using Vitest.

### 2. Webhook CI/CD (`webhook_pipeline.yaml`)
Triggered on **push**, **pull_request** to the `main` branch, and manually via **workflow_dispatch**. This pipeline focuses specifically on the `pipeline-pm-webhook` service.

It consists of two main jobs:
- **Unit Tests (`test`)**: Audits Python dependencies via `pip-audit` and strictly runs the Pytest suite for the webhook logic within the `pipeline-pm-webhook` directory.
- **Build and Push (`build-and-push`)**: Uses Trivy to scan the file system for OS and library vulnerabilities. If successful (and if not running on a pull request), it builds a Docker image for the webhook and pushes it to the GitHub Container Registry (`ghcr.io`).
