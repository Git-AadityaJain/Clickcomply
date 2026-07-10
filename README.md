# ClickComply

Automated DPDP compliance review for privacy policies and data notices against India's **Digital Personal Data Protection Act, 2023 (DPDP Act)** and **DPDP Rules 2025**.

ClickComply guides you through an organisation questionnaire, determines which DPDP rules apply to your profile, optionally generates a draft policy, and runs AI-powered compliance analysis on uploaded or generated documents. Results — gaps, severity, and recommendations — appear in a web dashboard.

**Free by default:** analysis runs locally via [Ollama](https://ollama.com). No API keys or cloud billing required.

> **Not legal advice.** ClickComply is an assistive screening tool. Final compliance decisions should involve qualified legal review.

**Author:** [AadityaJain](https://github.com/Git-AadityaJain)

---

## Table of Contents

1. [Who this is for](#who-this-is-for)
2. [How it works](#how-it-works)
3. [Requirements](#requirements)
4. [Quick start (local dev)](#quick-start-local-dev)
5. [Using the dashboard](#using-the-dashboard)
6. [Authentication](#authentication)
7. [Configuration](#configuration)
8. [Docker deployment](#docker-deployment)
9. [Database (SQLite vs PostgreSQL)](#database-sqlite-vs-postgresql)
10. [Project structure](#project-structure)
11. [Architecture for developers](#architecture-for-developers)
12. [API reference](#api-reference)
13. [Verify everything works](#verify-everything-works)
14. [Troubleshooting](#troubleshooting)
15. [Tech stack](#tech-stack)
16. [Further reading](#further-reading)

---

## Who this is for

| Audience | Use case |
|----------|----------|
| Compliance / legal teams | First-pass review of privacy policies and data notices |
| Product & engineering | Check draft policies before publication |
| Developers / evaluators | Run and extend an open DPDP analysis pipeline locally |

---

## How it works

```
Org questionnaire (5 steps)
  → rule applicability report (which of 16 DPDP rules apply)
  → optional: generate draft policy (DOCX/PDF)
  → optional: upload existing PDF/DOCX
  → extract text (pypdf / python-docx)
  → index in ChromaDB (RAG over DPDP Act + Rules 2025)
  → evaluate applicable rules via Ollama (llama3.2)
  → persist results → dashboard (gaps + recommendations)
```

Analysis starts **automatically** after upload or draft submission. The dashboard polls while status is `ANALYZING`. On a typical laptop, the first document may take **8–20+ minutes** (up to 16 LLM rule evaluations per document).

### DPDP areas checked (16 rules)

Aligned with the **DPDP Act 2023** and **DPDP Rules 2025** (G.S.R. 846(E), Nov 2025). Rule applicability is filtered based on your organisation profile — not all 16 rules apply to every business.

| Area | Legal basis | What is evaluated |
|------|-------------|-------------------|
| Notice (itemised) | §5; Rule 3 | Data, purposes, rights, withdrawal means |
| Board complaint | §5(1)(iii); Rule 3 | How to complain to the Data Protection Board |
| Consent | §6 | Free, specific, informed consent and withdrawal |
| Consent Manager | §6(7)–(9); Rule 4 | Consent management platform where applicable |
| Legitimate uses | §7 | Processing without consent and conditions |
| Security safeguards | §8(5); Rule 6 | Encryption, access control, logging, backups |
| Storage & erasure | §8(7)–(8); Rule 8 | Retention, inactivity erasure, 1-year logs |
| Children's data | §9; Rule 10 | Parental consent, no targeted ads/tracking |
| Disability + guardian | §9(1); Rule 11 | Verifiable guardian consent |
| Data principal rights | §§11–14; Rule 14 | Access, correction, erasure, nomination |
| Grievance redressal | §8(10), §13; Rule 14(3) | Complaint channel, **90-day** response |
| Contact / DPO | §8(9); Rule 9 | Published contact for processing questions |
| Data breach | §8(6); Rule 7 | Principal notice + **72-hour** Board intimation |
| Cross-border transfer | §16; Rule 15 | Transfers outside India and safeguards |
| Data processors | §8(1)–(2) | Third-party processors under valid contract |
| Significant Data Fiduciary | §10; Rule 13 | DPO, DPIA, audit, algorithmic risk |

**Not automated:** Board appeals, penalties, government exemptions (§17), and Data Principal duties (§15).

---

## Requirements

| Tool | Version | Why |
|------|---------|-----|
| [Node.js](https://nodejs.org) | LTS (20+) | Frontend dashboard |
| Python | 3.10+ | FastAPI backend |
| [Ollama](https://ollama.com) | Latest | Local LLM + embeddings (**required for analysis**) |

**Supported files:** PDF, DOCX, DOC (max **50 MB** per file).

**Ports used:**

| Service | Port |
|---------|------|
| Frontend (Next.js) | `3000` |
| Backend (FastAPI) | `8000` |
| Ollama | `11434` |
| PostgreSQL (prod only) | `5432` |

---

## Quick start (local dev)

You need **three processes** running: Ollama, backend, and frontend.

### 1. Ollama (one-time setup)

Install Ollama, then pull the models ClickComply expects:

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

Keep Ollama running in the background while you use the app.

Verify:

```bash
curl http://127.0.0.1:11434/api/tags
```

### 2. Backend

```bash
cd backend
python -m venv venv
```

Activate the virtual environment:

- **Windows (PowerShell):** `venv\Scripts\Activate.ps1`
- **macOS / Linux:** `source venv/bin/activate`

```bash
pip install -r requirements.txt
```

From the **project root**, start the backend (keep this terminal open):

```bash
npm run dev:backend
```

`dev:backend` uses `scripts/dev-backend.mjs` to launch uvicorn with `--reload` on `127.0.0.1:8000`. Override the port with `BACKEND_PORT` if needed.

- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health: [http://localhost:8000/health](http://localhost:8000/health)

### 3. Frontend

In a **second terminal**, from the project root:

```bash
npm install
npm run dev
```

- Dashboard: [http://localhost:3000](http://localhost:3000)

In development, the frontend proxies API calls through `/api/*` → backend (configured in `next.config.mjs`), so you do not need `NEXT_PUBLIC_API_URL` locally.

### npm scripts

| Script | Command | Purpose |
|--------|---------|---------|
| `dev` | `next dev --webpack` | Frontend dev server |
| `dev:backend` | `node scripts/dev-backend.mjs` | Backend with hot reload |
| `build` | `next build` | Production frontend build |
| `start` | `next start` | Production frontend |
| `lint` | `eslint .` | Lint frontend |

---

## Using the dashboard

### Review flow

1. Open `http://localhost:3000` (login is optional in local dev — see [Authentication](#authentication))
2. Complete the **5-step organisation questionnaire** (company details, processing type, data collected, retention, etc.)
3. Review the **Rule Applicability** summary — shows which DPDP rules apply to your profile
4. Optionally **generate a draft policy** (DOCX or PDF) from your answers
5. Optionally **upload an existing PDF/DOCX** for comparison and analysis
6. Analysis runs automatically; watch the documents table for status updates
7. Click a row to open the **Compliance Summary** (gaps, recommendations, overall status)
8. **Export** results as JSON, CSV, or PDF from the compliance panel
9. Use **Re-run analysis** if Ollama was offline during the first pass

### Sample test document

A demo privacy policy and walkthrough are in `demo/`:

- `demo/NovaStack_Demo_Privacy_Policy.docx` — upload this with the questionnaire answers in `demo/DEMO_WALKTHROUGH.txt`

### Document statuses

| Status | Meaning |
|--------|---------|
| `AWAITING_UPLOAD` | Questionnaire saved; no file uploaded yet |
| `QUEUED_FOR_ANALYSIS` | File stored; analysis queued |
| `ANALYZING` | RAG + LLM evaluation in progress |
| `ANALYSIS_COMPLETE` | Results ready |
| `ANALYSIS_FAILED` | Analysis error (often Ollama not running or timeout) |

### Analysis outcomes

| `overall_status` | Meaning |
|------------------|---------|
| `COMPLIANT` | No significant gaps found |
| `NON_COMPLIANT` | One or more high-severity gaps |
| `NEEDS_REVIEW` | Ambiguous or medium-severity items |
| `ANALYZING` | Still running; panel auto-refreshes |

### Session storage

Reviews are **ephemeral by default** — closing the browser clears un-remembered reviews on next visit. Toggle **Remember** on a document row to persist it across sessions.

---

## Authentication

Phase 2 adds JWT-based auth. In local development, auth is **optional** (`REQUIRE_AUTH=false` by default).

| Mode | `REQUIRE_AUTH` | Behaviour |
|------|----------------|-----------|
| Local dev | `false` (default) | Skip login or register; anonymous reviews work |
| Production | `true` | All document/analysis routes require a Bearer token |

### Frontend auth flow

1. `/login` — register or sign in → tokens saved to `localStorage`
2. **Skip for now** — bypasses auth for local testing
3. `AuthGate` on `/` allows access when authenticated or skipped

### Backend auth endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Create account + profile |
| `POST` | `/auth/login` | Sign in → access + refresh tokens |
| `POST` | `/auth/refresh` | Refresh token pair |
| `GET` | `/auth/me` | Current user |
| `PATCH` | `/auth/profile` | Update profile |

Tokens use HS256: access token (15 min), refresh token (7 days). Set `JWT_SECRET` to a strong random value when enabling auth.

---

## Configuration

Defaults work out of the box with Ollama. Copy `backend/.env.example` → `backend/.env` to override.

### Backend environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `AI_PROVIDER` | `ollama` | `ollama` \| `openai` \| `gemini` |
| `OLLAMA_MODEL` | `llama3.2` | Chat model for rule evaluation |
| `OLLAMA_EMBEDDING_MODEL` | `nomic-embed-text` | Embeddings for RAG |
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | Ollama API address |
| `DATABASE_URL` | SQLite (`clickcomply.db`) | Document + analysis storage |
| `REQUIRE_AUTH` | `false` | Force login when `true` |
| `JWT_SECRET` | `dev-insecure-change-me` | Required when `REQUIRE_AUTH=true` |
| `CORS_ORIGINS` | `http://localhost:3000,...` | Allowed browser origins |
| `UPLOAD_DIR` | `backend/uploads/` | Stored upload files |
| `CHROMA_DIR` | `backend/chroma_data/` | Vector store data |
| `MAX_FILE_SIZE` | `50000000` (50 MB) | Upload limit |

Generate a production JWT secret:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

### Frontend environment variables

Only needed when the backend is **not** on port 8000, or in production builds. Create `.env.local` in the project root:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Restart `npm run dev` after changing env files.

**Paid cloud AI (optional):** set `AI_PROVIDER=openai` or `gemini` in `backend/.env` and install the matching package. See [backend/README.md](backend/README.md).

---

## Docker deployment

### Development stack

Runs Ollama, backend (SQLite), and frontend in containers:

```bash
docker compose up --build
```

| Service | Port | Notes |
|---------|------|-------|
| `ollama` | 11434 | Pulls `llama3.2` + `nomic-embed-text` on first start |
| `backend` | 8000 | SQLite at `/app/data/clickcomply.db` |
| `frontend` | 3000 | `NEXT_PUBLIC_API_URL=http://localhost:8000` baked at build |

### Production stack

Adds PostgreSQL, Alembic migrations, and required auth:

```bash
cp .env.prod.example .env
# Edit .env: set JWT_SECRET, POSTGRES_PASSWORD, CORS_ORIGINS

docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build
```

Production overlay changes:

- **PostgreSQL 16** replaces SQLite
- `REQUIRE_AUTH=true` — startup fails if `JWT_SECRET` is unset
- Backend runs `alembic upgrade head` before uvicorn
- `DEBUG=false`

---

## Database (SQLite vs PostgreSQL)

| Environment | Driver | Schema management |
|-------------|--------|-------------------|
| Local dev (default) | `sqlite+aiosqlite` | `init_db()` — `create_all()` + inline migrations |
| Production (Docker) | `postgresql+asyncpg` | Alembic migrations (`alembic upgrade head`) |

### Switch to PostgreSQL locally

1. Run PostgreSQL (or use the prod compose overlay)
2. Set in `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://clickcomply:clickcomply@localhost:5432/clickcomply
```

3. Apply migrations:

```bash
cd backend
alembic upgrade head
```

### Tables

| Table | Purpose |
|-------|---------|
| `users` | Accounts (email, password hash) |
| `user_profiles` | Full name, company, phone |
| `documents` | Review lifecycle, org profile, generated policy, file metadata |
| `analysis_results` | Compliance gaps, recommendations, overall status |

---

## Project structure

```
clickcomply/
├── app/                          # Next.js App Router pages
│   ├── page.tsx                  # Dashboard (auth-gated)
│   └── login/page.tsx            # Login / register / skip
├── components/                   # Dashboard UI
│   ├── org-questionnaire-wizard.tsx
│   ├── document-upload.tsx
│   ├── compliance-summary.tsx
│   ├── applicability-summary.tsx
│   ├── documents-table.tsx
│   └── ui/                       # shadcn/ui primitives
├── lib/
│   ├── api.ts                    # Frontend → backend API client
│   ├── auth.ts                   # Token storage
│   ├── org-profile.ts            # Questionnaire types
│   └── hooks/                    # SWR data hooks
├── hooks/                        # Shared UI hooks (toast, mobile)
├── backend/
│   ├── app/
│   │   ├── routes/               # auth, documents, analysis
│   │   ├── services/             # AI, RAG, analysis, policy gen
│   │   ├── models/               # SQLAlchemy ORM
│   │   ├── schemas/              # Pydantic request/response
│   │   └── dpdp/                 # DPDP rules, applicability, sections
│   ├── alembic/                  # PostgreSQL migrations
│   └── requirements.txt
├── demo/                         # Sample policy + walkthrough for testing
├── docker-compose.yml            # Dev stack
├── docker-compose.prod.yml       # Prod overlay (Postgres + auth)
├── GUIDE.md                      # Step-by-step onboarding + E2E checklist
└── backend/README.md             # API reference and AI configuration
```

**Runtime data (gitignored):** `backend/clickcomply.db`, `backend/uploads/`, `backend/chroma_data/`, `backend/venv/`, `node_modules/`, `.next/`

---

## Architecture for developers

### Backend services

| Service | Role |
|---------|------|
| `document_service` | Ingest, upload, policy generation, remember flag |
| `analysis_service` | Orchestrate analysis, persist results, rerun/cancel |
| `ai_service` | Per-rule RAG + LLM compliance evaluation |
| `rag_service` | ChromaDB vector store (DPDP knowledge + document chunks) |
| `policy_generator` | Markdown → DOCX/PDF draft from questionnaire |
| `compare_service` | Compare uploaded policy vs generated draft |
| `rule_applicability` | Filter 16 rules by org profile |
| `text_extractor` | PDF/DOCX text extraction |
| `user_service` | Registration, login, profile |
| `review_pdf_exporter` | PDF compliance report download |

### Frontend data flow

1. `OrgQuestionnaireWizard` collects `OrgProfile` → `POST /documents/ingest`
2. Applicability returned → `ApplicabilitySummary` displays applicable rules
3. Optional draft → `POST /documents/{id}/generate-policy`
4. Optional upload → `POST /documents/{id}/upload` (triggers analysis)
5. `ComplianceSummary` polls `GET /analysis/{id}` until complete
6. `useDocuments` (SWR) keeps the documents table in sync
7. `useBackendHealth` polls `/health/live` and `/health` for AI readiness

### Adding a new DPDP rule

1. Define the rule in `backend/app/dpdp/dpdp_rules.py`
2. Add applicability logic in `backend/app/dpdp/rule_applicability.py`
3. Add RAG knowledge in `backend/app/dpdp/dpdp_rules_2025.py` or `dpdp_sections.py`
4. The AI service automatically evaluates new rules in the compliance loop

### Key files to read first

| File | Why |
|------|-----|
| `backend/app/main.py` | FastAPI entry, lifespan, router registration |
| `backend/app/dpdp/dpdp_rules.py` | The 16 compliance rules |
| `backend/app/services/ai_service.py` | RAG + LLM evaluation loop |
| `lib/api.ts` | All frontend API calls |
| `components/document-upload.tsx` | Main user flow |
| `components/org-questionnaire-wizard.tsx` | Questionnaire UI |

---

## API reference

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/documents/ingest` | Start review with `org_profile` |
| `GET` | `/documents` | List all documents |
| `GET` | `/documents/{id}/status` | Processing status |
| `POST` | `/documents/{id}/upload` | Upload file; triggers analysis |
| `POST` | `/documents/{id}/generate-policy` | Generate draft from questionnaire |
| `GET` | `/documents/{id}/suggested-policy/download` | Download generated draft |
| `GET` | `/documents/{id}/applicability` | Rule applicability report |
| `POST` | `/documents/{id}/analyze-draft` | Analyze generated draft (no upload) |
| `PATCH` | `/documents/{id}/remember` | Toggle remember flag |
| `POST` | `/documents/prune-session` | Remove ephemeral reviews |

### Analysis

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/analysis/{id}` | Compliance results (includes progress while analyzing) |
| `POST` | `/analysis/{id}/rerun` | Re-queue analysis |
| `POST` | `/analysis/{id}/cancel` | Cancel in-progress analysis |
| `GET` | `/analysis/{id}/download` | Download PDF compliance report |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Basic liveness |
| `GET` | `/health/live` | Liveness probe |
| `GET` | `/health` | Backend + AI health (Ollama status) |

Interactive docs when the backend is running: [http://localhost:8000/docs](http://localhost:8000/docs).

---

## Verify everything works

```bash
# Ollama
curl http://127.0.0.1:11434/api/tags

# Backend liveness
curl http://localhost:8000/health/live

# Backend + AI readiness
curl http://localhost:8000/health
```

Expect `"status": "READY"` under `ai` when Ollama and models are available.

**Quick functional test:**

1. Open the dashboard → complete the questionnaire
2. Upload `demo/NovaStack_Demo_Privacy_Policy.docx` (answers in `demo/DEMO_WALKTHROUGH.txt`)
3. Row appears → status reaches `ANALYSIS_COMPLETE`
4. Compliance panel shows gaps and recommendations

Full step-by-step checklist: [GUIDE.md §7](GUIDE.md#7-end-to-end-testing-frontend--backend).

---

## Troubleshooting

| Problem | What to check |
|---------|---------------|
| Upload fails | Backend running? `npm run dev:backend` in a separate terminal |
| Table shows "Backend offline" | Start backend on port 8000; check `NEXT_PUBLIC_API_URL` |
| `OLLAMA_NOT_RUNNING` on health check | Start Ollama; pull `llama3.2` and `nomic-embed-text` |
| Stuck on `ANALYZING` or `ANALYSIS_FAILED` | Ollama may be slow or timed out; check backend terminal logs |
| CORS errors in browser | Frontend must be on `localhost:3000` or `127.0.0.1:3000` (default) |
| `ModuleNotFoundError` (Python) | Activate `venv` and run `pip install -r requirements.txt` |
| Auth 401 in production | Set `JWT_SECRET`; ensure frontend sends Bearer token |
| Docker backend won't start | Check Ollama health; first start pulls models (slow) |

More fixes: [GUIDE.md §8](GUIDE.md#8-common-errors--fixes).

---

## Tech stack

| Layer | Stack |
|-------|-------|
| Frontend | Next.js 16, React 19, Tailwind CSS 4, shadcn/ui, SWR |
| Backend | FastAPI, SQLAlchemy (async), Pydantic |
| Database | SQLite (dev) / PostgreSQL 16 (prod) |
| Migrations | Alembic (PostgreSQL only) |
| AI | Ollama (`llama3.2`), ChromaDB RAG, `nomic-embed-text` |
| Auth | JWT (HS256), bcrypt password hashing |
| Containers | Docker Compose (Ollama + backend + frontend) |

---

## Further reading

| Document | Contents |
|----------|----------|
| [GUIDE.md](GUIDE.md) | Full setup, E2E verification, troubleshooting, AI architecture |
| [backend/README.md](backend/README.md) | API endpoints, upload workflow, environment variables |
| [demo/DEMO_WALKTHROUGH.txt](demo/DEMO_WALKTHROUGH.txt) | Sample questionnaire answers for testing |

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-change`
3. Follow existing code conventions (see [Architecture for developers](#architecture-for-developers))
4. Test locally: Ollama + backend + frontend all running
5. Open a pull request with a clear description of what changed and why
