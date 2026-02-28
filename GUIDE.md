# ClickComply — Developer Onboarding & Execution Guide

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
9. [AI Integration Note (For Future)](#9-ai-integration-note-for-future)

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

### Python 3.13 (Recommended)

Python 3.13 is used for the ClickComply backend to ensure compatibility with the latest language features and performance improvements.

```bash
python --version
# Expected output: Python 3.13.x

### pip

pip is the Python package manager. It is typically bundled with Python.

```bash
pip --version
# Expected output: pip 23.x or higher
```

If `pip` is not found, try `pip3 --version` or install it via `python -m ensurepip --upgrade`.

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
│   ├── compliance-summary.tsx    # Placeholder compliance analysis panel
│   ├── stats-bar.tsx             # Summary statistics bar
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
│   │   ├── services/             # Business logic & AI placeholder
│   │   ├── dpdp/                 # DPDP Act sections, rules, checks
│   │   └── utils/                # Shared helpers
│   ├── requirements.txt          # Python dependencies
│   └── README.md                 # Backend-specific documentation
├── package.json                  # Node.js dependencies
└── GUIDE.md                      # This file
```

### Purpose of Each Part

- **Frontend (`app/`, `components/`, `lib/`)**: A Next.js 16 dashboard that provides the user interface for uploading documents, viewing processing status, and reading compliance analysis results. It communicates with the backend via REST API calls.

- **Backend (`backend/`)**: A FastAPI server that manages document ingestion, lifecycle tracking, and compliance analysis. It uses SQLAlchemy with an async SQLite database for local development. The AI compliance engine is not yet integrated but the architecture is prepared for it.

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

### Step 4: Install Backend Dependencies (Python 3.13 Safe)

To ensure compatibility with Python 3.13 on Windows, install dependencies using **binary wheels only**:

```bash
pip install --upgrade pip setuptools wheel
pip install --only-binary=:all: -r requirements.txt
```
This installs the following packages:

```md
### Backend Dependency Stack (Verified for Python 3.13)

| Package | Version | Purpose |
|------|------|--------|
| fastapi | 0.111.0 | API framework |
| uvicorn | 0.30.1 | ASGI server |
| sqlalchemy | 2.0.31 | Async ORM |
| greenlet | >=3.0.3 | Required for SQLAlchemy async |
| aiosqlite | 0.20.0 | Async SQLite driver |
| pydantic | 2.8.2 | Data validation (Python 3.13 compatible) |
| python-dotenv | 1.0.1 | Environment configuration |
| email-validator | >=2.0.0 | Email validation support |

### Step 5: Configure the Database

ClickComply defaults to **SQLite** for local development. No configuration is required — the database file (`clickcomply.db`) is created automatically when the server starts.

To use **PostgreSQL** instead, create a `.env` file in the `backend/` directory:

```env
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/clickcomply
```

Note: PostgreSQL requires the `asyncpg` package (`pip install asyncpg`).

### Why `greenlet` Is Required

Although ClickComply uses an async database engine, SQLAlchemy internally relies on the `greenlet` library to safely bridge synchronous and asynchronous execution contexts.

Without `greenlet`, the application will fail during startup with:


### Step 6: Start the FastAPI Server

```bash
uvicorn app.main:app --reload
```

Expected terminal output:

```
INFO:     Started server process
INFO:     Starting ClickComply v1.0.0
### Expected Startup Output

```text
INFO:     Starting ClickComply v1.0.0
INFO:     Application startup complete.
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
  "ai_engine": "NOT_INTEGRATED"
}
```

This confirms the server is running. The `ai_engine: "NOT_INTEGRATED"` field is expected.

### Test 2: Ingest a Document

**Endpoint:** `POST /documents/ingest`

In Swagger UI, click the endpoint, press **Try it out**, and enter this request body:

```json
{
  "document_name": "privacy_policy.pdf",
  "document_type": "privacy_policy"
}
```

Press **Execute**.

**Expected response (201 Created):**
```json
{
  "document_id": "a1b2c3d4-...",
  "status": "RECEIVED",
  "message": "Document sensed and queued for compliance analysis"
}
```

Copy the `document_id` value — you will need it for the next two tests.

### Test 3: Check Document Status

**Endpoint:** `GET /documents/{document_id}/status`

Replace `{document_id}` with the UUID from the previous step.

**Expected response (200 OK):**
```json
{
  "document_id": "a1b2c3d4-...",
  "status": "AWAITING_AI_ANALYSIS"
}
```

The status `AWAITING_AI_ANALYSIS` indicates the document has been received and is waiting for the AI engine, which is not yet integrated.

### Test 4: Get Compliance Analysis

**Endpoint:** `GET /analysis/{document_id}`

Replace `{document_id}` with the same UUID.

**Expected response (200 OK):**
```json
{
  "overall_status": "PENDING_AI_REVIEW",
  "identified_gaps": [],
  "recommendations": [],
  "note": "AI compliance engine not yet integrated. This is a placeholder response with the same structure that the real AI engine will produce."
}
```

This confirms the analysis endpoint is working. The empty `identified_gaps` and `recommendations` arrays are expected — they will be populated once the AI engine is connected.

### Summary of Success Criteria

| What to check | Expected behavior |
|---------------|-------------------|
| `http://localhost:8000/docs` loads | Swagger UI is visible |
| `POST /documents/ingest` returns 201 | Document is created with a UUID |
| `GET /documents/{id}/status` returns 200 | Status shows `AWAITING_AI_ANALYSIS` |
| `GET /analysis/{id}` returns 200 | Placeholder analysis with empty arrays |

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
- A documents table (initially empty or showing fallback demo data)
- A compliance summary panel with placeholder analysis information

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

By default, it points to `http://localhost:8000` — the default FastAPI address. To change it:

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

This section walks through a complete workflow to verify that the frontend, backend, and their integration are all functioning correctly.

### Prerequisites

Ensure both servers are running:
- Backend at `http://localhost:8000`
- Frontend at `http://localhost:3000`

### Step 1: Open the Dashboard

Navigate to `http://localhost:3000`. The dashboard loads with the header, stats bar, upload card, documents table, and compliance summary panel.

**What this confirms:** The Next.js frontend is compiled and serving correctly.

### Step 2: Upload a Document

1. On the dashboard, locate the **"Upload Compliance Document"** card.
2. Click the upload area or drag a file onto it. Select any file (e.g., `privacy_policy.pdf`).
3. Click **"Submit for Analysis"**.

**What to observe:**
- The card transitions through three visual stages:
  - **SENSED**: The file has been detected (green indicator).
  - **QUEUED**: The document has been sent to the backend (amber indicator).
  - **AWAITING AI**: The document is stored and waiting for analysis (blue indicator).
- If the backend is not running, an error message appears in the upload card.

**What this confirms:** The frontend can send `POST /documents/ingest` to the backend and receive a response.

### Step 3: Observe Document Status in the Table

After uploading, check the **Documents** table below. The newly uploaded document should appear with:
- The document name you uploaded
- A status badge (e.g., `RECEIVED` or `AWAITING_AI_ANALYSIS`)
- A timestamp

**What this confirms:** The frontend is successfully calling `GET /documents` and rendering live backend data.

### Step 4: View Compliance Analysis

In the **Compliance Summary** panel, you will see:
- `PENDING_AI_REVIEW` as the overall status
- Empty compliance gaps and recommendations sections
- A note explaining that the AI engine is not yet integrated

**What this confirms:** The `GET /analysis/{document_id}` endpoint is reachable and returning the expected placeholder structure.

### Integration Checklist

| Component | How to verify | Expected result |
|-----------|--------------|-----------------|
| Frontend is working | Dashboard loads at `localhost:3000` | All panels render without errors |
| Backend is working | Swagger UI loads at `localhost:8000/docs` | All endpoints return correct responses |
| Integration is correct | Upload a document from the frontend | Document appears in the table with backend-assigned UUID |

---

## 8. Common Errors & Fixes

```md
### Error: `greenlet` Not Found


**Cause:**
`greenlet` is required by SQLAlchemy’s async engine but was not installed.

**Fix:**
```bash
pip install greenlet

### Backend Not Running

**Symptom:** The frontend upload card shows "Failed to submit document. Is the backend running?" or the documents table shows fallback demo data.

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

## 9. AI Integration Note (For Future)

### Current State

ClickComply's AI compliance analysis engine is **intentionally not integrated** at this stage. This is a deliberate architectural decision, not an incomplete feature.

### How It Works Today

All AI-related logic is isolated in a single file:

```
backend/app/services/ai_placeholder.py
```

This placeholder service:
- Implements the exact same function signatures the real AI engine will use
- Returns deterministic, static responses with the correct data structure
- Allows the entire frontend and backend to be built, tested, and demonstrated independently of any AI model

### What the Placeholder Returns

When any compliance analysis is requested, the system returns:

```json
{
  "overall_status": "PENDING_AI_REVIEW",
  "identified_gaps": [],
  "recommendations": [],
  "note": "AI compliance engine not yet integrated..."
}
```

### How AI Will Be Added (Without Changing APIs)

When the RAG + LLM engine is ready, the integration requires changes to **only one file**:

1. Replace `backend/app/services/ai_placeholder.py` with a real implementation (e.g., `ai_service.py`).
2. Maintain the same function signatures:
   - `async def run_compliance_analysis(document_id: str) -> dict`
   - `async def check_ai_health() -> dict`
3. The returned dictionary must match the existing `ComplianceAnalysisResponse` schema (defined in `backend/app/schemas/analysis.py`).
4. Update `compliance_checks.py` to invoke the LLM with prompts from `dpdp_rules.py`.

**No route files, schema files, frontend components, or API client code need to change.**

### Why This Architecture Matters

| Benefit | Explanation |
|---------|-------------|
| Separation of concerns | API contracts are finalized and tested independently of AI model selection |
| Parallel development | Frontend and backend work can continue while the AI team trains and evaluates models |
| Single integration point | Reduces risk during AI integration — only one file changes |
| Testability | The entire system can be verified end-to-end without an AI model running |

### Supporting DPDP Modules

The `backend/app/dpdp/` directory contains structured data ready for AI consumption:

- **`dpdp_sections.py`**: All 8 sections of the DPDP Act 2023 with titles and summaries
- **`dpdp_rules.py`**: 7 compliance rules with AI prompt hints for each
- **`compliance_checks.py`**: Per-section compliance check stubs that will call the AI engine

These modules are ready to be wired into the AI pipeline when the engine is connected.

---

## Summary

| Task | Command |
|----|-------|
| Create venv | `python -m venv venv` |
| Activate venv (Windows) | `venv\Scripts\Activate.ps1` |
| Install dependencies | `pip install --only-binary=:all: -r requirements.txt` |
| Start backend | `uvicorn app.main:app --reload` |
| API docs | `http://localhost:8000/docs` |
| Start frontend | `npm run dev` |

Both servers must be running simultaneously for the full application to function. The backend handles data persistence and API logic; the frontend provides the user interface. AI analysis is architecturally ready but intentionally deferred to a future phase.
