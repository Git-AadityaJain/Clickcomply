"""
Analysis API routes.

Endpoints:
    GET /analysis/{document_id} — Get compliance analysis for a document.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import logger
from app.schemas.analysis import ComplianceAnalysisResponse
from app.services.analysis_service import get_compliance_analysis
from app.services.document_service import get_document_by_id

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.get(
    "/{document_id}",
    response_model=ComplianceAnalysisResponse,
    summary="Get compliance analysis for a document",
    description=(
        "Returns the compliance analysis results for the specified document. "
        "Currently returns placeholder data — real AI analysis will be "
        "integrated without changing this endpoint's contract."
    ),
)
async def get_analysis(
    document_id: str,
    db: AsyncSession = Depends(get_db),
) -> ComplianceAnalysisResponse:
    """
    Return compliance analysis for a given document.

    Validates that the document exists before requesting analysis.
    The analysis service delegates to ai_placeholder.py for now.
    """
    # Verify the document exists
    document = await get_document_by_id(db, document_id)

    if document is None:
        logger.warning(f"Analysis requested for unknown document: {document_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found",
        )

    logger.info(f"Analysis requested for document: {document.document_name}")

    result = await get_compliance_analysis(document_id)

    return ComplianceAnalysisResponse(**result)
