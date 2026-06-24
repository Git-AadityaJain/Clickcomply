"""
Analysis API routes.

Endpoints:
    GET  /analysis/{document_id}        : Get compliance analysis for a document.
    POST /analysis/{document_id}/rerun  : Re-run analysis for an uploaded document.
"""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import logger
from app.schemas.analysis import AnalysisRerunResponse, ComplianceAnalysisResponse, AnalysisCancelResponse
from app.services.analysis_service import (
    get_compliance_analysis,
    run_and_persist_analysis,
    trigger_analysis_rerun,
    cancel_analysis,
)
from app.services.review_pdf_exporter import export_review_pdf
from app.services.document_service import get_document_by_id

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.get(
    "/{document_id}",
    response_model=ComplianceAnalysisResponse,
    summary="Get compliance analysis for a document",
    description=(
        "Returns persisted RAG+LLM compliance analysis for the specified document. "
        "Results are produced automatically after file upload when Ollama is running."
    ),
)
async def get_analysis(
    document_id: str,
    db: AsyncSession = Depends(get_db),
) -> ComplianceAnalysisResponse:
    """Return compliance analysis for a given document."""
    document = await get_document_by_id(db, document_id)

    if document is None:
        logger.warning(f"Analysis requested for unknown document: {document_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found",
        )

    logger.info(f"Analysis requested for document: {document.document_name}")

    result = await get_compliance_analysis(document_id, db)

    return ComplianceAnalysisResponse(**result)


@router.post(
    "/{document_id}/rerun",
    response_model=AnalysisRerunResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Re-run compliance analysis",
    description=(
        "Queues a fresh RAG+LLM analysis for a document that already has an uploaded file. "
        "Use when Ollama was offline during the first run or after policy updates."
    ),
)
async def rerun_analysis(
    document_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> AnalysisRerunResponse:
    """Re-run compliance analysis in the background."""
    try:
        result = await trigger_analysis_rerun(document_id, db)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    background_tasks.add_task(run_and_persist_analysis, document_id)
    logger.info(f"Re-analysis queued for document {document_id}")

    return AnalysisRerunResponse(**result)


@router.post(
    "/{document_id}/cancel",
    response_model=AnalysisCancelResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Cancel a running analysis",
)
async def cancel_running_analysis(
    document_id: str,
    db: AsyncSession = Depends(get_db),
) -> AnalysisCancelResponse:
    try:
        result = await cancel_analysis(document_id, db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return AnalysisCancelResponse(**result)


@router.get(
    "/{document_id}/download",
    summary="Download review report as PDF",
)
async def download_review_report(
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    document = await get_document_by_id(db, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Review not found.")

    analysis = await get_compliance_analysis(document_id, db)
    status_value = analysis.get("overall_status", "")
    if status_value in ("ANALYZING", "PENDING_AI_REVIEW"):
        raise HTTPException(
            status_code=400,
            detail="This review is not ready to download yet.",
        )

    has_content = (
        analysis.get("identified_gaps")
        or analysis.get("recommendations")
        or status_value in ("COMPLIANT", "NON_COMPLIANT", "NEEDS_REVIEW", "ANALYSIS_FAILED")
    )
    if not has_content:
        raise HTTPException(
            status_code=400,
            detail="No review results are available to download yet.",
        )

    try:
        pdf_bytes = export_review_pdf(document.document_name, analysis)
    except RuntimeError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc

    safe_name = "".join(
        c if c.isalnum() or c in " -_" else "_" for c in document.document_name
    ).strip()[:80] or "review"
    filename = f"clickcomply-{safe_name}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
