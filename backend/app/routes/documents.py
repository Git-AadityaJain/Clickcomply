"""
Document API routes.
"""

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import logger
from app.core.config import settings
from app.schemas.document import (
    DocumentIngestRequest,
    DocumentIngestResponse,
    DocumentStatusResponse,
    DocumentListItem,
    DocumentRememberUpdate,
    GeneratePolicyRequest,
    GeneratePolicyResponse,
    ApplicabilityResponse,
    PruneSessionRequest,
    PruneSessionResponse,
)
from app.services.session_storage_service import clear_ephemeral_uploads
from app.schemas.org_profile import ApplicabilityReport
from app.services.document_service import (
    ingest_document,
    get_document_by_id,
    get_all_documents,
    save_document_file,
    set_document_remember,
    generate_policy_file,
    document_list_item_fields,
    parse_org_profile,
)
from app.services.analysis_service import run_and_persist_analysis, trigger_draft_analysis

router = APIRouter(prefix="/documents", tags=["Documents"])


def _display_status(status: str) -> str:
    mapping = {
        "AWAITING_UPLOAD": "AWAITING_UPLOAD",
        "QUEUED_FOR_ANALYSIS": "AWAITING_AI_ANALYSIS",
        "ANALYZING": "ANALYZING",
        "ANALYSIS_COMPLETE": "ANALYSIS_COMPLETE",
        "ANALYSIS_FAILED": "ANALYSIS_FAILED",
    }
    return mapping.get(status, status)


def _to_list_item(document) -> DocumentListItem:
    item = DocumentListItem.model_validate(document)
    extra = document_list_item_fields(document)
    item.status = _display_status(item.status)
    item.has_org_profile = extra["has_org_profile"]
    item.has_generated_policy = extra["has_generated_policy"]
    item.has_uploaded_file = extra["has_uploaded_file"]
    return item


@router.post("/ingest", response_model=DocumentIngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest(
    payload: DocumentIngestRequest,
    db: AsyncSession = Depends(get_db),
) -> DocumentIngestResponse:
    logger.info(f"Ingest request: {payload.org_profile.legal_name}")
    document, applicability = await ingest_document(
        db=db,
        org_profile=payload.org_profile,
        document_name=payload.document_name,
        document_type=payload.document_type,
    )
    return DocumentIngestResponse(
        document_id=document.id,
        status=_display_status(document.status),
        message="Your answers were saved.",
        generated_policy_available=False,
        applicability=applicability,
    )


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
async def get_status(document_id: str, db: AsyncSession = Depends(get_db)) -> DocumentStatusResponse:
    document = await get_document_by_id(db, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Review not found.")
    return DocumentStatusResponse(document_id=document.id, status=_display_status(document.status))


@router.get("", response_model=list[DocumentListItem])
async def list_documents(db: AsyncSession = Depends(get_db)) -> list[DocumentListItem]:
    documents = await get_all_documents(db)
    return [_to_list_item(doc) for doc in documents]


@router.post("/prune-session", response_model=PruneSessionResponse)
async def prune_session(payload: PruneSessionRequest) -> PruneSessionResponse:
    """Remove reviews not marked to keep (browser refresh / new visit)."""
    removed_ids = await clear_ephemeral_uploads(set(payload.keep_document_ids))
    return PruneSessionResponse(
        removed_count=len(removed_ids),
        removed_ids=removed_ids,
    )


@router.get("/{document_id}/applicability", response_model=ApplicabilityResponse)
async def get_applicability(document_id: str, db: AsyncSession = Depends(get_db)) -> ApplicabilityResponse:
    document = await get_document_by_id(db, document_id)
    if document is None or not document.applicability_json:
        raise HTTPException(status_code=404, detail="Applicability information not found.")
    report = ApplicabilityReport.model_validate_json(document.applicability_json)
    return ApplicabilityResponse(document_id=document_id, report=report)


@router.post("/{document_id}/generate-policy", response_model=GeneratePolicyResponse)
async def post_generate_policy(
    document_id: str,
    payload: GeneratePolicyRequest,
    db: AsyncSession = Depends(get_db),
) -> GeneratePolicyResponse:
    try:
        document = await generate_policy_file(db, document_id, payload.format)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc

    profile = parse_org_profile(document)
    return GeneratePolicyResponse(
        document_id=document_id,
        format=payload.format,
        filename=document.generated_policy_filename or "",
        legal_name=profile.legal_name if profile else document.document_name,
    )


@router.get("/{document_id}/suggested-policy/download")
async def download_suggested_policy(document_id: str, db: AsyncSession = Depends(get_db)):
    document = await get_document_by_id(db, document_id)
    if document is None or not document.generated_policy_filename:
        raise HTTPException(status_code=404, detail="No suggested policy file is available yet.")

    path = Path(settings.UPLOAD_DIR) / document.generated_policy_filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Suggested policy file is missing.")

    media = (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        if path.suffix == ".docx"
        else "application/pdf"
    )
    return FileResponse(path, media_type=media, filename=path.name)


@router.patch("/{document_id}/remember", response_model=DocumentListItem)
async def update_remember(
    document_id: str,
    payload: DocumentRememberUpdate,
    db: AsyncSession = Depends(get_db),
) -> DocumentListItem:
    try:
        document = await set_document_remember(db=db, document_id=document_id, remember=payload.remember)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _to_list_item(document)


@router.post("/{document_id}/upload", response_model=DocumentListItem)
async def upload_file(
    document_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> DocumentListItem:
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Please choose a file to upload.")

        content = await file.read()
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="That file is too large. Try a smaller PDF or Word document.")

        uploader_ip = request.client.host if request.client else None
        document = await save_document_file(
            db=db,
            document_id=document_id,
            file_content=content,
            original_filename=file.filename,
            uploader_ip=uploader_ip,
        )
        background_tasks.add_task(run_and_persist_analysis, document_id)
        return _to_list_item(document)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except IOError as e:
        logger.error(f"Failed to save file for document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="We could not save your file. Please try again.")


@router.post("/{document_id}/analyze-draft", response_model=DocumentStatusResponse)
async def analyze_draft(
    document_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> DocumentStatusResponse:
    """Queue compliance analysis against the generated policy draft (no file upload needed)."""
    try:
        result = await trigger_draft_analysis(document_id, db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    background_tasks.add_task(run_and_persist_analysis, document_id)
    return DocumentStatusResponse(
        document_id=document_id,
        status=_display_status(result["status"]),
    )
