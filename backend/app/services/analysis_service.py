"""
Analysis Service — orchestrates compliance analysis, persistence, and background runs.
"""

import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.core.logging import logger
from app.models.analysis import AnalysisResult
from app.models.document import Document
from app.services import ai_service
from app.services.document_service import get_document_by_id


async def get_compliance_analysis(document_id: str, db: AsyncSession) -> dict:
    """
    Return cached analysis or a status response while analysis is in progress.
    """
    cached = await _get_latest_result(db, document_id)
    if cached:
        return cached

    document = await get_document_by_id(db, document_id)
    if document is None:
        raise ValueError(f"Document {document_id} not found")

    if document.status == "ANALYZING":
        return {
            "overall_status": "ANALYZING",
            "identified_gaps": [],
            "recommendations": [],
            "note": "Compliance analysis is in progress. Results will appear shortly.",
        }

    if document.status == "ANALYSIS_FAILED":
        return {
            "overall_status": "ANALYSIS_FAILED",
            "identified_gaps": [],
            "recommendations": [],
            "note": "Analysis failed. Re-upload the document or check server logs.",
        }

    return {
        "overall_status": "PENDING_AI_REVIEW",
        "identified_gaps": [],
        "recommendations": [],
        "note": "Analysis has not started yet. Upload a file to trigger compliance review.",
    }


async def run_and_persist_analysis(document_id: str) -> None:
    """
    Background task: run AI analysis and persist results.
    Creates its own database session.
    """
    async with async_session() as db:
        try:
            document = await get_document_by_id(db, document_id)
            if document is None:
                logger.warning(f"Analysis skipped — document {document_id} not found")
                return

            document.status = "ANALYZING"
            await db.commit()

            logger.info(f"Starting compliance analysis for document {document_id}")
            result = await ai_service.run_compliance_analysis(document_id, db)

            overall = result.get("overall_status", "NEEDS_REVIEW")
            if overall == "ANALYSIS_FAILED":
                document.status = "ANALYSIS_FAILED"
            elif overall == "PENDING_AI_REVIEW":
                document.status = "AWAITING_AI_ANALYSIS"
            elif overall in ("COMPLIANT", "NON_COMPLIANT", "NEEDS_REVIEW"):
                document.status = "ANALYSIS_COMPLETE"
            else:
                document.status = "ANALYSIS_COMPLETE"

            analysis_row = AnalysisResult(
                document_id=document_id,
                analysis_status=overall,
                summary=result.get("note", ""),
                result_json=json.dumps(result),
            )
            db.add(analysis_row)
            await db.commit()

            logger.info(
                f"Analysis complete for {document_id}: status={overall}, "
                f"gaps={len(result.get('identified_gaps', []))}"
            )
        except Exception as exc:
            logger.exception(f"Analysis pipeline failed for {document_id}: {exc}")
            await db.rollback()
            async with async_session() as err_db:
                document = await get_document_by_id(err_db, document_id)
                if document:
                    document.status = "ANALYSIS_FAILED"
                    err_db.add(
                        AnalysisResult(
                            document_id=document_id,
                            analysis_status="ANALYSIS_FAILED",
                            summary=str(exc),
                            result_json=json.dumps(
                                {
                                    "overall_status": "ANALYSIS_FAILED",
                                    "identified_gaps": [],
                                    "recommendations": [],
                                    "note": str(exc),
                                }
                            ),
                        )
                    )
                    await err_db.commit()


async def _get_latest_result(db: AsyncSession, document_id: str) -> dict | None:
    """Load the most recent persisted analysis result."""
    result = await db.execute(
        select(AnalysisResult)
        .where(AnalysisResult.document_id == document_id)
        .order_by(AnalysisResult.created_at.desc())
        .limit(1)
    )
    row = result.scalar_one_or_none()
    if row is None or not row.result_json:
        return None

    try:
        return json.loads(row.result_json)
    except json.JSONDecodeError:
        logger.error(f"Invalid result_json for document {document_id}")
        return None
