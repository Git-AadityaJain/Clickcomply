# ClickComply Developer Onboarding & Execution Guide

> A step-by-step guide for setting up, running, and verifying the ClickComply DPDP compliance platform locally.
> Written for internship submission and suitable for beginner-to-intermediate developers.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Project Structure Overview](#2-project-structure-overview)
3. [Running the Backend (FastAPI)](#3-running-the-backend-fastapi)
4. [Verifying the Backend is Working](#4-verifying-the-backend-is-working)
5. [Running the Frontend (Next.js)](#5-running-the-frontend-nextjs)
6. [Connecting Frontend to Backend](#6-connecting-frontend-to-backend)
7. [End-to-End Testing (Frontend + Backend)](#7-end-to-end-testing-frontend--backend)
8. [Common Errors & Fixes](#8-common-errors--fixes)
9. [AI Engine (Ollama RAG)](#9-ai-engine-ollama-rag)

---

## 1. Prerequisites

Before running ClickComply, ensure the following tools are installed on your machine.

### Node.js (LTS)

Node.js is required for the Next.js frontend.

```bash
node --version
# Expected output: v20.x.x or v22.x.x (LTS)
```

If not installed, download from [https://nodejs.org](https://nodejs.org). Choose the **LTS** version.

### npm

npm is bundled with Node.js. Verify it is available:

```bash
npm --version
# Expected output: 10.x.x or higher
```

### Python 3.10+

Python is required for the FastAPI backend.

```bash
python --version
# Expected output: Python 3.10.x or higher (3.11, 3.12 also supported)
```

If not installed, download from [https://www.python.org/downloads](https://www.python.org/downloads). On macOS/Linux, you may need to use `python3` instead of `python`.

### pip

pip is the Python package manager. It is typically bundled with Python.

```bash
pip --version
# Expected output: pip 23.x or higher
```

If `pip` is not found, try `pip3 --version` or install it via `python -m ensurepip --upgrade`.

### Ollama (required for AI analysis)

ClickComply uses **Ollama** for local LLM inference and embeddings (free, no API keys).

1. Download and install from [https://ollama.com](https://ollama.com)
2. Pull the required models (one-time):

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

3. Keep Ollama running in the background while using ClickComply.

Verify Ollama is reachable:

```bash
curl http://127.0.0.1:11434/api/tags
```

### VS Code

Download and install Visual Studio Code from [https://code.visualstudio.com](https://code.visualstudio.com).

**Recommended extensions:**

| Extension | Purpose |
|-----------|---------|
| Python (Microsoft) | Python IntelliSense, linting, debugging |
| Pylance | Advanced Python type checking |
| ESLint | JavaScript/TypeScript linting |
| Tailwind CSS IntelliSense | Tailwind class autocomplete |
| REST Client or Thunder Client | API testing from within VS Code |

---

## 2. Project Structure Overview

ClickComply is a full-stack application split into two independent codebases within a single repository:

```
clickcomply/
├── app/                          # Next.js frontend (App Router)
│   ├── globals.css               # Global styles and design tokens
│   ├── layout.tsx                # Root layout with font and metadata
│   └── page.tsx                  # Main dashboard page
├── components/                   # Reusable React components
│   ├── dashboard-header.tsx      # App header with branding
│   ├── document-upload.tsx       # Drag-and-drop document upload card
│   ├── documents-table.tsx       # Document list with status badges
│   ├── compliance-summary.tsx    # Live compliance analysis panel
│   ├── stats-bar.tsx             # Summary statistics bar
│   ├── dashboard-provider.tsx    # Selected document + shared dashboard state
│   ├── dashboard-shell.tsx       # Dashboard layout wrapper
│   ├── providers.tsx             # SWR data-fetching provider
│   └── ui/                       # shadcn/ui component library
├── lib/
│   ├── api.ts                    # Frontend API client (calls backend)
│   └── utils.ts                  # Shared utility functions
├── backend/                      # FastAPI backend (Python)
│   ├── app/
│   │   ├── main.py               # Application entry point
│   │   ├── core/                 # Config, database, logging
│   │   ├── models/               # SQLAlchemy ORM models
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   ├── routes/               # API endpoint definitions
│   │   ├── services/             # Business logic, RAG, and AI services
│   │   ├── dpdp/                 # DPDP Act sections, rules, checks
│   │   └── utils/                # Shared helpers
│   ├── requirements.txt          # Python dependencies
│   └── README.md                 # Backend-specific documentation
├── package.json                  # Node.js dependencies
└── GUIDE.md                      # This file
```

### Purpose of Each Part

- **Frontend (`app/`, `components/`, `lib/`)**: A Next.js 16 dashboard that provides the user interface for uploading documents, viewing processing status, and reading compliance analysis results. It communicates with the backend via REST API calls.

- **Backend (`backend/`)**: A FastAPI server that manages document ingestion, file storage, text extraction, vector RAG indexing, and automated DPDP compliance analysis via Ollama. Uses SQLAlchemy with async SQLite for local development.

---

## 3. Running the Backend (FastAPI)

### Step 1: Open the Backend Folder

Open a terminal in VS Code (`Ctrl+`` ` or `Cmd+`` `) and navigate to the backend directory:

```bash
cd backend
```

### Step 2: Create a Python Virtual Environment

A virtual environment isolates the project's Python dependencies from your system-wide packages.

```bash
# Create the virtual environment
python -m venv venv
```

### Step 3: Activate the Virtual Environment

**macOS / Linux:**
```bash
source venv/bin/activate
```

**Windows (Command Prompt):**
```bash
venv\Scripts\activate
```

**Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

When activated, you will see `(venv)` at the beginning of your terminal prompt.

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs the following packages:

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.111.0 | Web framework for building APIs |
| uvicorn | 0.30.1 | ASGI server to run the FastAPI app |
| sqlalchemy | 2.0.31 | ORM for database operations |
| pydantic | 2.7.4 | Data validation and serialization |
| aiosqlite | 0.20.0 | Async SQLite driver |
| python-dotenv | 1.0.1 | Environment variable loading |

### Step 5: Configure the Database

ClickComply defaults to **SQLite** for local development. No configuration is required; the database file (`clickcomply.db`) is created automatically when the server starts.

To use **PostgreSQL** instead, create a `.env` file in the `backend/` directory:

```env
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/clickcomply
```

Note: PostgreSQL requires the `asyncpg` package (`pip install asyncpg`).

### Step 6: Install and Start Ollama

Ensure Ollama is installed and the models are pulled (see [Prerequisites](#1-prerequisites)). Ollama must be running before you upload documents for analysis.

### Step 7: Start the FastAPI Server

```bash
uvicorn app.main:app --reload
```

Expected terminal output:

```
INFO:     Started server process
INFO:     Starting ClickComply v1.0.0
INFO:     Database tables initialized
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

The `--reload` flag enables auto-restart when Python files are changed (development only).

---

## 4. Verifying the Backend is Working

### Open the Swagger UI

With the backend running, open your browser and navigate to:

```
http://localhost:8000/docs
```

This displays the **FastAPI Swagger UI**, an interactive API documentation page where you can test all endpoints directly.

### Test 1: Health Check

**Endpoint:** `GET /`

Click the endpoint in Swagger UI, press **Try it out**, then **Execute**.

**Expected response (200 OK):**
```json
{
  "app": "ClickComply",
  "version": "1.0.0",
  "status": "running",
  "ai_engine": "READY",
  "ai_provider": "ollama"
}
```

This confirms the server is running. `ai_engine: "READY"` means Ollama is reachable and configured. If you see `OLLAMA_NOT_RUNNING`, start Ollama and pull the models listed in the prerequisites.

**Detailed health:** `GET /health` returns database and AI subsystem status:

```json
{
  "app": "ClickComply",
  "status": "healthy",
  "database": "connected",
  "ai": {
    "ai_engine": "ollama",
    "status": "READY",
    "model": "llama3.2",
    "embedding_model": "nomic-embed-text"
  }
}
```

### Test 2: Ingest a Compliance Review

**Endpoint:** `POST /documents/ingest`

Requires an `org_profile` object (organization processing questionnaire). The easiest path is the **dashboard wizard** at `http://localhost:3000`. For API testing, use the request body schema in Swagger UI (`/docs`) — it lists all required fields.

**Expected response (201 Created):** `document_id`, `status: "AWAITING_UPLOAD"`, generated policy availability, and an `applicability` report.

Copy the `document_id` for the next tests.

### Test 3: Check Document Status

**Endpoint:** `GET /documents/{document_id}/status`

**Expected response (200 OK):** `status: "AWAITING_UPLOAD"` until analysis is triggered.

After **Analyze draft** (`POST /documents/{id}/analyze-draft`) or file upload, status progresses through `QUEUED_FOR_ANALYSIS` → `ANALYZING` → `ANALYSIS_COMPLETE` or `ANALYSIS_FAILED`.

### Test 4: Analyze Draft or Upload a File

**Option A — no upload:** `POST /documents/{document_id}/analyze-draft`

**Option B — compare upload:** `POST /documents/{document_id}/upload` with a PDF or DOCX file.

Both queue background analysis when Ollama is running. Upload additionally runs a draft-vs-upload comparison in the analysis response.

### Test 5: Get Compliance Analysis

**Endpoint:** `GET /analysis/{document_id}`

Replace `{document_id}` with the same UUID. Poll this endpoint while status is `ANALYZING`; analysis can take several minutes locally (16 LLM rule evaluations per document).

**Expected response (200 OK) when complete:**
```json
{
  "overall_status": "COMPLIANT",
  "identified_gaps": ["..."],
  "recommendations": ["..."],
  "note": "Analysis complete. ..."
}
```

`overall_status` may also be `NON_COMPLIANT`, `NEEDS_REVIEW`, or `ANALYSIS_FAILED` depending on document content and Ollama availability.

### Summary of Success Criteria

| What to check | Expected behavior |
|---------------|-------------------|
| `http://localhost:8000/docs` loads | Swagger UI is visible |
| `GET /` returns 200 | `ai_engine` is `READY` when Ollama is running |
| `POST /documents/ingest` returns 201 | Review created with org profile and generated draft |
| `POST /documents/{id}/analyze-draft` or upload returns 200 | Analysis queued |
| `GET /documents/{id}/status` returns 200 | Status progresses to `ANALYSIS_COMPLETE` |
| `GET /analysis/{id}` returns 200 | Populated gaps and recommendations |

---

## 5. Running the Frontend (Next.js)

Open a **new terminal** in VS Code (keep the backend terminal running).

### Step 1: Navigate to the Project Root

```bash
cd clickcomply
```

The frontend files live at the project root (`app/`, `components/`, `lib/`).

### Step 2: Install Dependencies

```bash
npm install
```

This reads `package.json` and installs all Node.js packages. The installation may take a minute the first time.

### Step 3: Start the Development Server

```bash
npm run dev
```

Expected terminal output:

```
  ▲ Next.js 16.x.x
  - Local:        http://localhost:3000
  - Environments: .env
  ✓ Ready
```

### Step 4: Open the Application

Navigate to `http://localhost:3000` in your browser. You should see the ClickComply compliance dashboard with:

- A header displaying "ClickComply" and the DPDP Act compliance label
- A statistics bar showing document counts by status
- A document upload card with drag-and-drop support
- A documents table (empty until you upload, or showing live backend data)
- A compliance summary panel that updates when you select a document

---

## 6. Connecting Frontend to Backend

### How the Frontend Calls Backend APIs

All API communication is centralized in a single file:

```
lib/api.ts
```

This file contains:
- Type definitions matching the FastAPI Pydantic schemas
- Functions for each API endpoint (`ingestDocument`, `getDocumentStatus`, `listDocuments`, `getAnalysis`)
- A `fetcher` helper used by SWR for automatic data fetching and caching

### Where the Backend Base URL is Configured

The API base URL is set at the top of `lib/api.ts`:

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
```

By default, it points to `http://localhost:8000` (the default FastAPI address). To change it:

1. Create a `.env.local` file in the project root:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
2. Restart the Next.js dev server for the change to take effect.

### Running Both Servers Simultaneously

You need **two terminals** running at the same time:

| Terminal | Directory | Command | URL |
|----------|-----------|---------|-----|
| Terminal 1 | `backend/` | `uvicorn app.main:app --reload` | `http://localhost:8000` |
| Terminal 2 | Project root | `npm run dev` | `http://localhost:3000` |

**VS Code tip:** Use the split terminal feature (`Ctrl+Shift+5` or `Cmd+Shift+5`) to see both terminals side by side.

### CORS Configuration

The backend is pre-configured to accept requests from the frontend. In `backend/app/core/config.py`:

```python
CORS_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

Both `localhost` and `127.0.0.1` are allowed. No additional CORS setup is needed for local development.

---

## 7. End-to-End Testing (Frontend + Backend)

This section walks through a complete workflow to verify that the frontend, backend, Ollama, and their integration are all functioning correctly.

### Prerequisites

Ensure all three are running:
- **Ollama** with `llama3.2` and `nomic-embed-text` pulled
- Backend at `http://localhost:8000` (`ai_engine: "READY"` on `GET /`)
- Frontend at `http://localhost:3000`

### E2E Verification Checklist

Use this checklist before demos or submission. Check each box in order.

| # | Step | Pass criteria |
|---|------|---------------|
| 1 | Ollama running | `curl http://127.0.0.1:11434/api/tags` returns model list including `llama3.2` |
| 2 | Backend health | `GET http://localhost:8000/` → `ai_engine: "READY"` |
| 3 | Frontend loads | Dashboard at `localhost:3000` with no console errors |
| 4 | Questionnaire + analyze | Complete wizard → analyze draft or upload policy → analysis completes |
| 5 | Document in table | New row appears with correct name, size, and status badge |
| 6 | Analysis starts | Status becomes `ANALYZING` (may take a few seconds) |
| 7 | Analysis completes | Status becomes `ANALYSIS_COMPLETE` (allow several minutes on first run) |
| 8 | Compliance panel | Selecting the document shows gaps, recommendations, and overall status |
| 9 | API parity | `GET /analysis/{id}` in Swagger matches what the dashboard shows |
| 10 | Backend offline UX | Stop backend → documents table shows offline message (not fake demo data) |

### Step 1: Open the Dashboard

Navigate to `http://localhost:3000`. The dashboard loads with the header, stats bar, upload card, documents table, and compliance summary panel.

**What this confirms:** The Next.js frontend is compiled and serving correctly.

### Step 2: Complete the Organization Questionnaire

1. On the dashboard, complete the **Organization Processing Profile** wizard (6 steps).
2. Click **Generate policy draft** on the final step.

**What to observe:**
- Rule applicability summary for your declared processing activities
- Generated ideal DPDP policy draft (preview / download)
- Options to **Analyze generated draft** or **Upload & analyze** an existing policy

**What this confirms:** The frontend sends `POST /documents/ingest` with `org_profile` and receives a tailored draft.

### Step 3: Run Analysis

Click **Analyze generated draft**, or upload a PDF/DOCX and click **Upload & analyze**.

**What to observe:** Progress through QUEUED → ANALYZING; Compliance Summary updates when complete.

### Step 4: Observe Document Status in the Table

The **Documents** table should show the new review with status progressing to `ANALYSIS_COMPLETE`.

### Step 5: View Compliance Analysis

Select the review. The **Compliance Summary** panel shows:
- Overall status and applicable-rule count (skipped rules noted)
- Identified DPDP gaps and recommendations
- Uploaded vs generated draft comparison (when a file was uploaded)

**What this confirms:** The full questionnaire → draft → RAG → Ollama → persist → display pipeline works end-to-end.

### Integration Checklist

| Component | How to verify | Expected result |
|-----------|--------------|-----------------|
| Ollama | `curl http://127.0.0.1:11434/api/tags` | Models listed |
| Frontend | Dashboard loads at `localhost:3000` | All panels render without errors |
| Backend | Swagger UI at `localhost:8000/docs` | `GET /` shows `ai_engine: "READY"` |
| Integration | Upload a PDF/DOCX from the frontend | Analysis completes; compliance panel populates |

---

## 8. Common Errors & Fixes

### Backend Not Running

**Symptom:** The frontend upload card shows "Failed to submit document. Is the backend running?" or the documents table shows a red "Backend offline" message.

**Fix:** Open a terminal, navigate to `backend/`, activate the virtual environment, and run:
```bash
uvicorn app.main:app --reload
```

### CORS Issues

**Symptom:** Browser console shows an error like:
```
Access to fetch at 'http://localhost:8000/documents/ingest' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Fix:** Ensure the backend `CORS_ORIGINS` in `backend/app/core/config.py` includes your frontend URL. By default, `http://localhost:3000` and `http://127.0.0.1:3000` are allowed. If your frontend runs on a different port, add it to the list:

```python
CORS_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",  # Add your port here
]
```

Restart the backend after changing configuration.

### Ollama Not Running

**Symptom:** `GET /` returns `ai_engine: "OLLAMA_NOT_RUNNING"`. Uploads succeed but analysis stays in `ANALYSIS_FAILED` or never completes.

**Fix:**
1. Start the Ollama application (or `ollama serve` on Linux).
2. Pull models: `ollama pull llama3.2` and `ollama pull nomic-embed-text`.
3. Re-upload or wait for the background task to retry on the next document.

### API Connection Errors

**Symptom:** Network errors in the browser console when the frontend tries to reach the backend.

**Possible causes and fixes:**

1. **Wrong API URL:** Check that `NEXT_PUBLIC_API_URL` in `.env.local` matches the backend address. Default is `http://localhost:8000`.
2. **Backend crashed:** Check the backend terminal for error messages. Common cause: missing Python package. Re-run `pip install -r requirements.txt`.
3. **Database locked:** If using SQLite and you see "database is locked" errors, ensure only one instance of the backend is running.

### Port Conflicts

**Symptom:** `Address already in use` error when starting either server.

**Fix for backend (port 8000):**
```bash
# Find the process using port 8000
lsof -i :8000          # macOS/Linux
netstat -ano | findstr 8000  # Windows

# Kill the process, then restart
kill -9 <PID>           # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

Or run the backend on a different port:
```bash
uvicorn app.main:app --reload --port 8001
```
Remember to update `NEXT_PUBLIC_API_URL` in the frontend to match.

**Fix for frontend (port 3000):**
```bash
# Next.js will automatically try the next available port (3001, 3002, etc.)
# If it does, update the backend CORS_ORIGINS to include the new port.
```

### ModuleNotFoundError (Python)

**Symptom:** `ModuleNotFoundError: No module named 'fastapi'` or similar.

**Fix:** Ensure your virtual environment is activated (you should see `(venv)` in your terminal prompt) and install dependencies:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### TypeScript Build Errors (Frontend)

**Symptom:** TypeScript errors when running `npm run dev`.

**Fix:**
```bash
rm -rf node_modules .next
npm install
npm run dev
```

---

## 9. AI Engine (Ollama RAG)

### Current State

ClickComply runs **automated DPDP compliance analysis** using:

| Layer | Technology |
|-------|------------|
| Text extraction | `pypdf` (PDF), `python-docx` (DOCX) |
| Vector store | ChromaDB (`backend/chroma_data/`): Act sections, compliance rules, **DPDP Rules 2025** |
| Embeddings | Ollama `nomic-embed-text` |
| LLM evaluation | Ollama `llama3.2` (16 rules from `dpdp_rules.py` + DPDP Rules 2025 in RAG) |

Analysis triggers automatically after file upload via FastAPI `BackgroundTasks`.

### Key Modules

| File | Role |
|------|------|
| `backend/app/services/text_extractor.py` | Extract text from uploaded files |
| `backend/app/services/rag_service.py` | Index document + DPDP rule chunks in Chroma |
| `backend/app/services/llm_client.py` | Ollama chat + embeddings (OpenAI/Gemini optional) |
| `backend/app/services/ai_service.py` | Per-rule RAG+LLM compliance evaluation |
| `backend/app/services/analysis_service.py` | Persist results to `analysis_results` |

### Configuration

Copy `backend/.env.example` to `backend/.env` to override defaults:

| Variable | Default |
|----------|---------|
| `AI_PROVIDER` | `ollama` |
| `OLLAMA_MODEL` | `llama3.2` |
| `OLLAMA_EMBEDDING_MODEL` | `nomic-embed-text` |
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434` |

See [backend/README.md](backend/README.md) for optional OpenAI/Gemini setup.

### Performance Notes

- Each document runs **16 LLM calls** (one per DPDP compliance rule) plus embedding indexing.
- First analysis on a typical laptop may take **3–10+ minutes**.
- The compliance panel polls while status is `ANALYZING`.

---

## Summary

| Task | Command | URL |
|------|---------|-----|
| Pull Ollama models | `ollama pull llama3.2 && ollama pull nomic-embed-text` | - |
| Start backend | `cd backend && uvicorn app.main:app --reload` | `http://localhost:8000` |
| View API docs | (backend must be running) | `http://localhost:8000/docs` |
| Start frontend | `npm run dev` | `http://localhost:3000` |
| Health check | `curl http://localhost:8000/health` | JSON with `ai.status: "READY"` |

Ollama, the backend, and the frontend must all be running for full compliance analysis. Use the [E2E Verification Checklist](#e2e-verification-checklist) in Section 7 before demos.
