# Project Management Webhooks

A lightweight, cloud-native FastAPI microservice designed to automate project management workflows for bioinformatics pipeline development. This service acts as a secure bridge between a master System Requirements Google Doc and a GitHub Projects V2 Kanban board.

## 🎯 The Goal
To maintain a Single Source of Truth (SSOT). Whenever an issue is opened or labeled with a specific Requirement ID (e.g., `REQ-SEC-01`), this service dynamically traverses the Google Docs Abstract Syntax Tree (AST), extracts the most up-to-date compliance text, and injects it directly into a custom field on the GitHub Project board via GraphQL.

## 🏗️ Architecture

* **Framework:** FastAPI (Python 3.11)
* **Authentication:** HMAC SHA-256 (GitHub Webhooks) & Google Service Accounts
* **Integrations:** * Google Docs API (Read-only AST traversing)
  * GitHub GraphQL API (Projects V2 mutations)
* **Deployment:** Dockerized and managed via GitHub Actions CI/CD


```mermaid
flowchart TD
    subgraph GitHub["GitHub Ecosystem"]
        Issue["GitHub Issue (Opened/Labeled)"]
        Webhook["GitHub Webhook Trigger"]
        Board["Projects V2 Kanban Board"]
    end

    subgraph Service["Pipeline PM Webhook (Docker Container)"]
        API["FastAPI Endpoint (/webhook)"]
        Security["Security Gate (HMAC SHA-256)"]
        Router["Event Router (Regex Match)"]
        DocsService["Google Docs Service (AST Parser)"]
        GQLService["GitHub GraphQL Service"]
    end

    subgraph Google["Google Cloud"]
        Doc["Master System Requirements (Google Doc)"]
    end

    %% The Flow
    Issue -- "Contains [REQ-ID]" --> Webhook
    Webhook -- "POST JSON & Signature Header" --> API
    API --> Security
    Security -- "Invalid Hash" --> Drop["401 Unauthorized (Drop)"]
    Security -- "Valid Hash" --> Router
    
    Router -- "Extracts REQ-ID" --> DocsService
    DocsService -- "Service Account Auth" --> Doc
    Doc -- "Returns deeply nested AST" --> DocsService
    DocsService -- "Parses & cleans compliance text" --> GQLService
    
    GQLService -- "Mutation: addProjectV2ItemById" --> Board
    GQLService -- "Mutation: updateProjectV2ItemFieldValue" --> Board

    %% Styling
    classDef github fill:#24292e,stroke:#fff,stroke-width:2px,color:#fff;
    classDef service fill:#009688,stroke:#fff,stroke-width:2px,color:#fff;
    classDef google fill:#4285F4,stroke:#fff,stroke-width:2px,color:#fff;
    classDef error fill:#b31d28,stroke:#fff,stroke-width:2px,color:#fff;
    
    class Issue,Webhook,Board github;
    class API,Security,Router,DocsService,GQLService service;
    class Doc google;
    class Drop error;
```

## 🚀 Local Development

This service is fully containerized. To run it locally for development or testing:

### 1. Prerequisites
* Docker installed on your host machine.
* A GitHub Personal Access Token (PAT) with `repo` and `project` scopes.
* A Google Cloud Service Account JSON key (`service_account.json`).

### 2. Environment Variables
Create a `.env` file in the project root (this file is git-ignored):

```env
GITHUB_WEBHOOK_SECRET=your_hmac_secret
GITHUB_PAT=ghp_your_personal_access_token
GOOGLE_DOC_ID=your_google_doc_id
GITHUB_PROJECT_ID=PVT_your_project_id
GITHUB_CUSTOM_FIELD_ID=PVTF_your_field_id
```

### 3. Running the Service
Build and run the Docker container, mounting your Google credentials as a read-only volume:
```bash
docker build -t pipeline-pm-webhook .

docker run --name webhook-service \
  --env-file .env \
  -v $(pwd)/service_account.json:/app/service_account.json:ro \
  -p 8000:8000 \
  pipeline-pm-webhook:latest
```

## 🧪 Testing
The repository utilizes pytest with mocked external API calls to ensure robust CI without hitting rate limits.
```bash
# Run tests locally (requires a virtual environment)
pip install -r requirements.txt pytest httpx
pytest -v tests/
```

## ⚙️ CI/CD Pipeline
Every push to the main branch triggers a GitHub Actions workflow that:

1. Provisions an Ubuntu runner.
2. Executes the pytest suite.
3. If tests pass, builds the Docker image and pushes it to the GitHub Container Registry (GHCR).

<br>
Maintainer: Harrison Reed (harrisonhvreed@gmail.com)
