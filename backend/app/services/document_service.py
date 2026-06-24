"""
Document Service: business logic for document ingestion and status tracking.

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
from app.services.text_extractor import TextExtractionError, extract_text_from_bytes
from app.schemas.org_profile import OrgProfile, ApplicabilityReport
from app.dpdp.rule_applicability import evaluate_rule_applicability
from app.services.policy_generator import (
    generate_policy_markdown,
    export_policy_docx,
    export_policy_pdf,
)


def parse_org_profile(document: Document) -> OrgProfile | None:
    if not document.org_profile_json:
        return None
    return OrgProfile.model_validate_json(document.org_profile_json)


async def ingest_document(
    db: AsyncSession,
    org_profile: OrgProfile,
    document_name: str | None = None,
    document_type: str = "privacy_policy",
) -> tuple[Document, ApplicabilityReport]:
    """Ingest a compliance review with organization processing profile."""
    doc_id = generate_uuid()
    name = document_name or f"{org_profile.legal_name} — Privacy Policy Review"

    applicability = evaluate_rule_applicability(org_profile)

    document = Document(
        id=doc_id,
        document_name=name,
        document_type=document_type,
        status="AWAITING_UPLOAD",
        org_profile_json=org_profile.model_dump_json(),
        applicability_json=applicability.model_dump_json(),
    )

    db.add(document)
    await db.commit()
    await db.refresh(document)

    logger.info(f"Document {doc_id} created with org profile: {org_profile.legal_name}")
    return document, applicability


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

    try:
        extracted = extract_text_from_bytes(file_content, original_filename)
        document.extracted_text = extracted[:500_000]
        logger.info(
            f"Extracted {len(extracted)} characters from document {document_id}"
        )
    except TextExtractionError as exc:
        logger.warning(f"Text extraction failed for {document_id}: {exc}")
        document.extracted_text = None

    # Update document record
    document.file_size = metadata["file_size"]
    document.upload_timestamp = metadata["upload_timestamp"]
    document.uploader_ip = metadata["uploader_ip"]
    document.original_filename = metadata["original_filename"]
    document.stored_filename = metadata["stored_filename"]
    document.status = "QUEUED_FOR_ANALYSIS"

    await db.commit()
    await db.refresh(document)

    logger.info(f"Document {document_id} metadata updated")

    return document


async def set_document_remember(
    db: AsyncSession,
    document_id: str,
    remember: bool,
) -> Document:
    """Toggle whether a document should survive server restarts."""
    document = await get_document_by_id(db, document_id)
    if not document:
        raise ValueError(f"Document {document_id} not found")

    document.remember = remember
    await db.commit()
    await db.refresh(document)
    logger.info(f"Document {document_id} remember -> {remember}")
    return document


async def generate_policy_file(
    db: AsyncSession,
    document_id: str,
    file_format: str = "docx",
) -> Document:
    """Generate a DPDP-aligned policy draft as DOCX or PDF on demand."""
    document = await get_document_by_id(db, document_id)
    profile = parse_org_profile(document)
    if not document or not profile:
        raise ValueError("Review not found or questionnaire missing.")

    markdown = generate_policy_markdown(profile)
    title = f"{profile.legal_name} — Privacy Policy"
    ext = "docx" if file_format == "docx" else "pdf"

    if ext == "docx":
        content = export_policy_docx(markdown, title)
    else:
        content = export_policy_pdf(markdown, title)

    upload_dir = get_upload_dir(settings.UPLOAD_DIR)
    stored_name = f"{document_id}_suggested_policy.{ext}"
    save_uploaded_file(content, stored_name, upload_dir)

    document.generated_policy_md = markdown
    document.generated_policy_filename = stored_name
    await db.commit()
    await db.refresh(document)
    logger.info(f"Generated {ext} policy for document {document_id}")
    return document


def document_list_item_fields(document: Document) -> dict:
    return {
        "has_org_profile": bool(document.org_profile_json),
        "has_generated_policy": bool(document.generated_policy_filename),
        "has_uploaded_file": bool(document.stored_filename),
    }
