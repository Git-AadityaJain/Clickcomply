# ClickComply Backend

AI-powered DPDP Act (Digital Personal Data Protection Act, 2023) compliance platform backend built with FastAPI, SQLAlchemy, and Pydantic.

## Purpose

ClickComply allows administrators to ingest compliance documents (metadata only), track their processing lifecycle, and view compliance analysis results. The system is architecturally ready for AI-powered analysis via RAG + LLM, but the AI engine is **not yet integrated**.

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
│   │   ├── analysis_service.py  # Analysis orchestration
│   │   └── ai_placeholder.py   # ** THE ONLY FILE TO REPLACE FOR AI **
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
| GET    | `/analysis/{document_id}`     | Get compliance analysis (placeholder) |
| GET    | `/health`                     | Health check with AI status        |

## Why AI Is Not Integrated Yet

The system is designed with a clear separation between the API/business layer and the AI engine. This allows:

1. **Frontend development** to proceed independently of AI model selection and training.
2. **API contracts** to be finalized and tested before AI adds complexity.
3. **The AI integration point** to be a single file swap (`ai_placeholder.py`).

## How to Add AI (Without Breaking APIs)

When the RAG + LLM engine is ready:

1. **Replace `app/services/ai_placeholder.py`** with a real implementation.
2. Keep the same function signatures:
   - `async def run_compliance_analysis(document_id: str) -> dict`
   - `async def check_ai_health() -> dict`
3. The return dictionary must match the existing `ComplianceAnalysisResponse` schema.
4. Update `compliance_checks.py` to call the LLM with prompts from `dpdp_rules.py`.
5. **No route, schema, or service orchestration files need to change.**

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
