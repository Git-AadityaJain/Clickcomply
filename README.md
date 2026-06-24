# ClickComply

Automated compliance review for documents against India's **Digital Personal Data Protection Act, 2023 (DPDP Act)**.

Upload a privacy policy or similar document (PDF/DOCX). ClickComply extracts the text, searches it against DPDP Act 2023 and **DPDP Rules 2025** using vector RAG, and evaluates **16 compliance rules** with a local AI model. Results (gaps, severity, and recommendations) appear in a web dashboard.

**Free by default:** analysis runs on your machine via [Ollama](https://ollama.com). No API keys or cloud billing required.

> **Not legal advice.** ClickComply is an assistive screening tool. Final compliance decisions should involve qualified legal review.

---

## Who this is for

| Audience | Use case |
|----------|----------|
| Compliance / legal teams | Quick first-pass review of privacy policies and data notices |
| Product & engineering | Check draft policies before publication |
| Developers / evaluators | Run and extend an open DPDP analysis pipeline locally |

---

## How it works

```
Upload PDF/DOCX
  → extract text (pypdf / python-docx)
  → index in ChromaDB (RAG)
  → evaluate 16 DPDP rules via Ollama (llama3.2)
  → persist results → dashboard (gaps + recommendations)
```

Analysis starts **automatically** after upload. The dashboard polls while status is `ANALYZING`. On a typical laptop, the first document may take **8–20+ minutes** (16 LLM rule evaluations per document).

### DPDP areas checked (16 rules)

Aligned with the **DPDP Act 2023** and **DPDP Rules 2025** (G.S.R. 846(E), Nov 2025).

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
| Data processors | **§8(1)–(2)** | Third-party processors under valid contract |
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

**Ports used:** `3000` (frontend), `8000` (backend), `11434` (Ollama).

---

## Setup

### 1. Ollama (one-time)

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
uvicorn app.main:app --reload
```

- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health: [http://localhost:8000/health](http://localhost:8000/health)

### 3. Frontend

In a **second terminal**, from the project root:

```bash
npm install
npm run dev
```

- Dashboard: [http://localhost:3000](http://localhost:3000)

All three must be running for full analysis: **Ollama + backend + frontend**.

---

## Using the dashboard

1. Open `http://localhost:3000`
2. Drag a PDF or DOCX onto the upload card (or click to browse)
3. Click **Submit for Analysis**
4. Watch the documents table: status moves through `QUEUED_FOR_ANALYSIS` → `ANALYZING` → `ANALYSIS_COMPLETE`
5. Click a row to open the **Compliance Summary** (gaps, recommendations, overall status)
6. Use **Re-run analysis** if Ollama was offline during the first pass
7. **Export** results as JSON or CSV from the compliance panel

### Document statuses

| Status | Meaning |
|--------|---------|
| `RECEIVED` | Metadata registered, file not yet uploaded |
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

---

## Configuration (optional)

Defaults work out of the box with Ollama. To override, copy `backend/.env.example` to `backend/.env`:

| Variable | Default | Purpose |
|----------|---------|---------|
| `AI_PROVIDER` | `ollama` | `ollama` \| `openai` \| `gemini` |
| `OLLAMA_MODEL` | `llama3.2` | Chat model for rule evaluation |
| `OLLAMA_EMBEDDING_MODEL` | `nomic-embed-text` | Embeddings for RAG |
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | Ollama API address |
| `DATABASE_URL` | SQLite (`clickcomply.db`) | Document + analysis storage |
| `UPLOAD_DIR` | `backend/uploads/` | Stored upload files |
| `MAX_FILE_SIZE` | `50000000` (50 MB) | Upload limit |

**Frontend API URL:** if the backend is not on port 8000, create `.env.local` in the project root:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Restart `npm run dev` after changing env files.

**Paid cloud AI (optional):** set `AI_PROVIDER=openai` or `gemini` in `backend/.env` and install the matching package. See [backend/README.md](backend/README.md).

---

## Verify everything works

```bash
# Ollama
curl http://127.0.0.1:11434/api/tags

# Backend + AI
curl http://localhost:8000/health
```

Expect `"status": "READY"` under `ai` when Ollama and models are available.

**Quick functional test:** upload a PDF from the dashboard → row appears → status reaches `ANALYSIS_COMPLETE` → compliance panel shows gaps/recommendations.

Full step-by-step checklist: [GUIDE.md §7](GUIDE.md#7-end-to-end-testing-frontend--backend).

---

## Troubleshooting

| Problem | What to check |
|---------|---------------|
| Upload fails | Backend running? `uvicorn app.main:app --reload` from `backend/` |
| Table shows "Backend offline" | Start backend on port 8000; check `NEXT_PUBLIC_API_URL` |
| `OLLAMA_NOT_RUNNING` on health check | Start Ollama; pull `llama3.2` and `nomic-embed-text` |
| Stuck on `ANALYZING` or `ANALYSIS_FAILED` | Ollama may be slow or timed out; check backend terminal logs |
| CORS errors in browser | Frontend must be on `localhost:3000` or `127.0.0.1:3000` (default) |
| `ModuleNotFoundError` (Python) | Activate `venv` and run `pip install -r requirements.txt` |

More fixes: [GUIDE.md §8](GUIDE.md#8-common-errors--fixes).

---

## Project layout

```
clickcomply/
├── app/                 # Next.js pages
├── components/          # Dashboard UI (upload, table, compliance panel)
├── lib/api.ts           # Frontend → backend API client
├── backend/
│   ├── app/
│   │   ├── routes/      # REST endpoints
│   │   ├── services/    # AI, RAG, analysis, documents
│   │   └── dpdp/        # DPDP sections and rules
│   ├── uploads/         # Stored files (created at runtime)
│   └── clickcomply.db   # SQLite database (created at runtime)
├── GUIDE.md             # Detailed onboarding + E2E checklist
└── backend/README.md    # API reference and AI configuration
```

---

## Tech stack

| Layer | Stack |
|-------|-------|
| Frontend | Next.js 16, React, Tailwind, shadcn/ui, SWR |
| Backend | FastAPI, SQLAlchemy, SQLite |
| AI | Ollama (`llama3.2`), ChromaDB RAG, `nomic-embed-text` |

---

## Documentation

| Document | Contents |
|----------|----------|
| [GUIDE.md](GUIDE.md) | Full setup, E2E verification, troubleshooting, AI architecture |
| [backend/README.md](backend/README.md) | API endpoints, upload workflow, environment variables |

---

## API overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/documents/ingest` | Register document metadata |
| `POST` | `/documents/{id}/upload` | Upload file; triggers analysis |
| `GET` | `/documents` | List all documents |
| `GET` | `/documents/{id}/status` | Processing status |
| `GET` | `/analysis/{id}` | Compliance results (includes progress while analyzing) |
| `POST` | `/analysis/{id}/rerun` | Re-queue analysis for an uploaded document |
| `GET` | `/health` | Backend + AI health |

Interactive docs when the backend is running: [http://localhost:8000/docs](http://localhost:8000/docs).
