# ClickComply Backend

AI-powered DPDP Act (Digital Personal Data Protection Act, 2023) compliance platform backend built with FastAPI, SQLAlchemy, and Pydantic.

## Purpose

ClickComply allows administrators to upload compliance documents, run automated DPDP analysis, and view gaps and recommendations. Analysis uses **local Ollama** by default (free, no API keys).

## Architecture

```
backend/
├── app/
│   ├── main.py                  # FastAPI entry point with lifespan handler
│   ├── core/
│   │   ├── config.py            # Environment-based settings
│   │   ├── database.py          # Async SQLAlchemy engine & sessions
│   │   └── logging.py           # Centralized logging configuration
│   ├── models/
│   │   ├── document.py          # Document ORM model
│   │   └── analysis.py          # AnalysisResult ORM model
│   ├── schemas/
│   │   ├── document.py          # Request/response Pydantic schemas
│   │   └── analysis.py          # Analysis response schemas
│   ├── routes/
│   │   ├── documents.py         # POST /documents/ingest, GET /documents/{id}/status
│   │   └── analysis.py          # GET /analysis/{document_id}
│   ├── services/
│   │   ├── document_service.py  # Document business logic (ingest, retrieve, save)
│   │   ├── analysis_service.py  # Analysis orchestration + persistence
│   │   ├── ai_service.py        # RAG + LLM compliance evaluation
│   │   ├── llm_client.py        # Ollama (default) / OpenAI / Gemini
│   │   ├── rag_service.py       # ChromaDB vector store
│   │   └── text_extractor.py    # PDF + DOCX text extraction
│   ├── dpdp/
│   │   ├── dpdp_sections.py    # DPDP Act section constants
│   │   ├── dpdp_rules.py       # Compliance rule definitions
│   │   └── compliance_checks.py # Per-section check stubs
│   └── utils/
│       ├── helpers.py           # Shared utility functions
│       └── file_utils.py        # File upload, storage, and metadata helpers
├── requirements.txt
└── README.md
```

## Quick Start

### 1. Install Ollama (free, local AI)

Download from [https://ollama.com](https://ollama.com), then pull the models:

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

Keep Ollama running in the background (it starts automatically after install on Windows/Mac).

### 2. Start the backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## API Endpoints

| Method | Endpoint                      | Description                        |
|--------|-------------------------------|------------------------------------|
| POST   | `/documents/ingest`           | Ingest a new document (metadata)   |
| POST   | `/documents/{id}/upload`      | Upload file & save metadata        |
| GET    | `/documents/{id}/status`      | Get document processing status     |
| GET    | `/documents`                  | List all documents                 |
| GET    | `/analysis/{document_id}`     | Get compliance analysis results    |
| GET    | `/health`                     | Health check with AI status        |

## AI Engine (RAG + Ollama — free by default)

ClickComply uses **ChromaDB** for vector RAG and **Ollama** for local LLM + embeddings. No API keys or cloud billing required.

### Default setup (Ollama)

| Setting | Default |
|---------|---------|
| `AI_PROVIDER` | `ollama` |
| `OLLAMA_MODEL` | `llama3.2` |
| `OLLAMA_EMBEDDING_MODEL` | `nomic-embed-text` |
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434` |

Optional: copy `backend/.env.example` to `backend/.env` to override models.

Analysis runs automatically after each file upload. Results persist in `analysis_results`.

### Optional paid cloud providers

Set `AI_PROVIDER=openai` or `AI_PROVIDER=gemini` in `.env` and install the optional package:

```bash
pip install openai          # for OpenAI
pip install google-generativeai  # for Gemini
```

### Key modules

| Module | Role |
|--------|------|
| `app/services/text_extractor.py` | PDF + DOCX text extraction |
| `app/services/rag_service.py` | Chroma vector store (DPDP + document chunks) |
| `app/services/llm_client.py` | Ollama / OpenAI / Gemini embeddings + chat |
| `app/services/ai_service.py` | Per-rule RAG+LLM compliance evaluation |
| `app/services/analysis_service.py` | Persistence + background analysis |

## Legacy placeholder

`ai_placeholder.py` is retained for reference only. Production analysis uses `ai_service.py`.

## Database

Defaults to SQLite (via `aiosqlite`) for local development. Set `DATABASE_URL` in your environment to switch to PostgreSQL for production.

### Tables

- **documents**: `id`, `document_name`, `document_type`, `status`, `created_at`, `file_size`, `upload_timestamp`, `uploader_ip`, `original_filename`, `stored_filename`
- **analysis_results**: `id`, `document_id` (FK), `analysis_status`, `summary`, `created_at`

### File Upload Storage

Uploaded files are stored in the `backend/uploads/` directory with UUID-based names to prevent collisions. Original filenames are preserved in the `documents` table for auditing:

- **Original filename** (user's file): Stored in `original_filename` column
- **Stored filename** (UUID-based): Stored in `stored_filename` column and used for disk storage
- **Storage location**: `backend/uploads/{stored_filename}`
- **Metadata tracked**: File size, upload timestamp (UTC), uploader IP

## Environment Variables

| Variable       | Default                              | Description           |
|----------------|--------------------------------------|-----------------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./clickcomply.db` | Database connection URI |
| `HOST`         | `0.0.0.0`                           | Server bind address   |
| `PORT`         | `8000`                               | Server port           |
| `DEBUG`        | `true`                               | Enable debug logging  |
| `UPLOAD_DIR`   | `./backend/uploads`                  | Directory for file uploads |
| `MAX_FILE_SIZE` | `50000000`                          | Maximum file size in bytes (50 MB) |

## File Upload Workflow

The frontend submits documents in a two-step process:

### Step 1: Ingest Metadata
```bash
POST /documents/ingest
Content-Type: application/json

{
  "document_name": "privacy_policy.pdf",
  "document_type": "privacy_policy"
}

Response (201 Created):
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "RECEIVED",
  "message": "Document sensed and queued for compliance analysis"
}
```

### Step 2: Upload File
```bash
POST /documents/{document_id}/upload
Content-Type: multipart/form-data

file: <binary PDF/DOCX data>

Response (200 OK):
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "document_name": "privacy_policy.pdf",
  "document_type": "privacy_policy",
  "status": "QUEUED_FOR_ANALYSIS",
  "created_at": "2026-03-05T10:00:00Z",
  "file_size": 245632,
  "upload_timestamp": "2026-03-05T10:15:00Z",
  "uploader_ip": "203.0.113.42",
  "original_filename": "privacy_policy.pdf",
  "stored_filename": "a7f2e9c1-privacy_policy.pdf"
}
```

### Storage Details
- **Uploads directory**: Created automatically at `backend/uploads/` on startup
- **File naming**: UUID-based (e.g., `a7f2e9c1-privacy_policy.pdf`) to prevent collisions
- **Metadata**: Both original and stored filenames are tracked for auditing
- **Size validation**: Files exceeding `MAX_FILE_SIZE` are rejected with 413 Payload Too Large
- **IP tracking**: Uploader IP is captured from HTTP request headers (if available)
