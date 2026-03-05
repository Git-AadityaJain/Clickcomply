"""
Document Service — business logic for document ingestion and status tracking.

Handles all database operations for the documents table.
Keeps route handlers thin by encapsulating logic here.
"""

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.core.logging import logger
from app.core.config import settings
from app.utils.helpers import generate_uuid
from app.utils.file_utils import (
    get_upload_dir,
    save_uploaded_file,
    extract_file_metadata,
)


async def ingest_document(
    db: AsyncSession,
    document_name: str,
    document_type: str,
) -> Document:
    """
    Ingest a new document into the system.

    Steps:
        1. Create a Document record with status RECEIVED.
        2. Immediately transition to QUEUED_FOR_ANALYSIS.
        3. Persist and return the document.

    In the future, step 2 will dispatch to the AI queue instead of
    performing a synchronous status update.

    Args:
        db: Active database session.
        document_name: Human-readable document name.
        document_type: Category of the document.

    Returns:
        The persisted Document ORM instance.
    """
    doc_id = generate_uuid()

    document = Document(
        id=doc_id,
        document_name=document_name,
        document_type=document_type,
        status="RECEIVED",
    )

    db.add(document)
    await db.flush()

    logger.info(f"Document {doc_id} received: {document_name}")

    # Transition: RECEIVED -> QUEUED_FOR_ANALYSIS
    # In production this would enqueue an async job for the AI engine.
    document.status = "QUEUED_FOR_ANALYSIS"
    await db.commit()
    await db.refresh(document)

    logger.info(f"Document {doc_id} status -> QUEUED_FOR_ANALYSIS")

    return document


async def get_document_by_id(db: AsyncSession, document_id: str) -> Document | None:
    """
    Retrieve a single document by its UUID.

    Args:
        db: Active database session.
        document_id: UUID of the document.

    Returns:
        The Document instance, or None if not found.
    """
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    return result.scalar_one_or_none()


async def get_all_documents(db: AsyncSession) -> list[Document]:
    """
    Retrieve all documents ordered by creation date (newest first).

    Returns:
        List of Document instances.
    """
    result = await db.execute(
        select(Document).order_by(Document.created_at.desc())
    )
    return list(result.scalars().all())


async def save_document_file(
    db: AsyncSession,
    document_id: str,
    file_content: bytes,
    original_filename: str,
    uploader_ip: str | None = None,
) -> Document:
    """
    Save an uploaded file to disk and update document metadata.

    Steps:
        1. Extract metadata from file
        2. Save file to uploads directory
        3. Update document record with file metadata
        4. Persist changes

    Args:
        db: Active database session.
        document_id: UUID of the document to update.
        file_content: Raw bytes of the uploaded file.
        original_filename: User's original filename.
        uploader_ip: IP address of the uploader (optional).

    Returns:
        The updated Document instance with file metadata.

    Raises:
        ValueError: If document not found.
        IOError: If file cannot be saved.
    """
    # Get document
    document = await get_document_by_id(db, document_id)
    if not document:
        raise ValueError(f"Document {document_id} not found")

    # Extract metadata
    metadata = extract_file_metadata(file_content, original_filename, uploader_ip)

    # Save file to disk
    upload_dir = get_upload_dir(settings.UPLOAD_DIR)
    save_uploaded_file(file_content, metadata["stored_filename"], upload_dir)

    logger.info(
        f"File saved for document {document_id}: {metadata['stored_filename']} "
        f"({metadata['file_size']} bytes)"
    )

    # Update document record
    document.file_size = metadata["file_size"]
    document.upload_timestamp = metadata["upload_timestamp"]
    document.uploader_ip = metadata["uploader_ip"]
    document.original_filename = metadata["original_filename"]
    document.stored_filename = metadata["stored_filename"]

    await db.commit()
    await db.refresh(document)

    logger.info(f"Document {document_id} metadata updated")

    return document
