"""
Document API routes.

Endpoints:
    POST /documents/ingest         — Ingest a new document (metadata only).
    GET  /documents/{id}/status    — Get the processing status of a document.
    GET  /documents                — List all documents (for the dashboard).
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import logger
from app.core.config import settings
from app.schemas.document import (
    DocumentIngestRequest,
    DocumentIngestResponse,
    DocumentStatusResponse,
    DocumentListItem,
)
from app.services.document_service import (
    ingest_document,
    get_document_by_id,
    get_all_documents,
    save_document_file,
)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/ingest",
    response_model=DocumentIngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest a new compliance document",
    description=(
        "Accepts document metadata, stores it in the database, "
        "and queues it for compliance analysis. "
        "No actual file upload occurs — this is a metadata-only endpoint."
    ),
)
async def ingest(
    payload: DocumentIngestRequest,
    db: AsyncSession = Depends(get_db),
) -> DocumentIngestResponse:
    """Ingest a document and return its assigned UUID and status."""
    logger.info(f"Ingest request: {payload.document_name} ({payload.document_type})")

    document = await ingest_document(
        db=db,
        document_name=payload.document_name,
        document_type=payload.document_type,
    )

    return DocumentIngestResponse(
        document_id=document.id,
        status=document.status,
        message="Document sensed and queued for compliance analysis",
    )


@router.get(
    "/{document_id}/status",
    response_model=DocumentStatusResponse,
    summary="Get document processing status",
    description="Returns the current lifecycle status of a document.",
)
async def get_status(
    document_id: str,
    db: AsyncSession = Depends(get_db),
) -> DocumentStatusResponse:
    """Return the current status of a specific document."""
    document = await get_document_by_id(db, document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found",
        )

    # Documents in QUEUED_FOR_ANALYSIS are presented as AWAITING_AI_ANALYSIS
    # to the frontend, since the AI engine has not yet processed them.
    display_status = document.status
    if display_status == "QUEUED_FOR_ANALYSIS":
        display_status = "AWAITING_AI_ANALYSIS"

    return DocumentStatusResponse(
        document_id=document.id,
        status=display_status,
    )


@router.get(
    "",
    response_model=list[DocumentListItem],
    summary="List all documents",
    description="Returns all documents ordered by creation date (newest first).",
)
async def list_documents(
    db: AsyncSession = Depends(get_db),
) -> list[DocumentListItem]:
    """Return all documents for the dashboard table."""
    documents = await get_all_documents(db)
    return [DocumentListItem.model_validate(doc) for doc in documents]


@router.post(
    "/{document_id}/upload",
    response_model=DocumentListItem,
    status_code=status.HTTP_200_OK,
    summary="Upload a file for a document",
    description=(
        "Accepts a file upload for an existing document, "
        "saves it to disk, and updates document metadata "
        "(file size, timestamp, IP, original filename, stored filename)."
    ),
)
async def upload_file(
    document_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    request: Request,
) -> DocumentListItem:
    """Upload and save a file for a document."""
    try:
        # Validate file exists
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must have a filename",
            )

        # Check file size
        content = await file.read()
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE} bytes",
            )

        # Get uploader IP from request headers if available
        uploader_ip = None
        if request:
            uploader_ip = request.client.host if request.client else None

        logger.info(
            f"File upload for document {document_id}: {file.filename} ({len(content)} bytes)"
        )

        # Save file and update metadata
        document = await save_document_file(
            db=db,
            document_id=document_id,
            file_content=content,
            original_filename=file.filename,
            uploader_ip=uploader_ip,
        )

        logger.info(f"File saved successfully for document {document_id}")

        return DocumentListItem.model_validate(document)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except IOError as e:
        logger.error(f"Failed to save file for document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save file to server",
        )
