"""
Analysis Service — orchestrates compliance analysis for documents.

This service acts as the bridge between the API layer and the AI engine.
Currently delegates to ai_placeholder.py; when AI is integrated, only
the import path changes.
"""

from app.services.ai_placeholder import run_compliance_analysis
from app.core.logging import logger


async def get_compliance_analysis(document_id: str) -> dict:
    """
    Run (or retrieve) compliance analysis for a document.

    Currently calls the placeholder AI service. When the real AI engine
    is connected, this function's implementation stays the same — only
    the imported `run_compliance_analysis` changes.

    Args:
        document_id: UUID of the document to analyze.

    Returns:
        A dictionary matching the ComplianceAnalysisResponse schema.
    """
    logger.info(f"Requesting compliance analysis for document {document_id}")

    analysis_result = await run_compliance_analysis(document_id)

    logger.info(
        f"Analysis for document {document_id}: status={analysis_result['overall_status']}"
    )

    return analysis_result
