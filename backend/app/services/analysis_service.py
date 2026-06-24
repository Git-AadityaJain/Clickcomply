"""
Analysis Service: orchestrates compliance analysis, persistence, and background runs.
"""

import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.core.logging import logger
from app.models.analysis import AnalysisResult
from app.models.document import Document
from app.dpdp.dpdp_rules import COMPLIANCE_RULES
from app.services import ai_service
from app.services.analysis_progress import (
    clear_analysis_progress,
    clear_cancel_request,
    get_analysis_progress,
    request_analysis_cancel,
)
from app.services.document_service import get_document_by_id, parse_org_profile
from app.dpdp.rule_applicability import get_applicable_rules


async def get_compliance_analysis(document_id: str, db: AsyncSession) -> dict:
    """
    Return cached analysis or a status response while analysis is in progress.
    """
    document = await get_document_by_id(db, document_id)
    if document is None:
        raise ValueError(f"Document {document_id} not found")

    if document.status == "ANALYZING":
        return _analyzing_response(document_id, document)

    cached = await _get_latest_result(db, document_id)
    if cached and document.status == "ANALYSIS_COMPLETE":
        return cached

    if document.status == "ANALYSIS_FAILED":
        if cached:
            return cached
        return {
            "overall_status": "ANALYSIS_FAILED",
            "identified_gaps": [],
            "recommendations": [],
            "note": "The check could not finish. Try again or contact support if this keeps happening.",
        }

    if cached:
        return cached

    return {
        "overall_status": "PENDING_AI_REVIEW",
        "identified_gaps": [],
        "recommendations": [],
        "note": "Upload your privacy policy to start a compliance check.",
    }


async def cancel_analysis(document_id: str, db: AsyncSession) -> dict:
    """Request cancellation of a running analysis."""
    document = await get_document_by_id(db, document_id)
    if document is None:
        raise ValueError("Review not found.")

    if document.status != "ANALYZING":
        raise ValueError("No analysis is running right now.")

    request_analysis_cancel(document_id)
    return {
        "document_id": document_id,
        "status": "CANCELLING",
        "message": "Stopping the analysis. This may take a few seconds.",
    }


def _applicable_rule_count(document: Document) -> int:
    profile = parse_org_profile(document)
    if profile:
        return len(get_applicable_rules(profile))
    return len(COMPLIANCE_RULES)


def _analyzing_response(document_id: str, document: Document | None = None) -> dict:
    progress = get_analysis_progress(document_id)
    total = progress["total"] if progress else (
        _applicable_rule_count(document) if document else len(COMPLIANCE_RULES)
    )
    payload: dict = {
        "overall_status": "ANALYZING",
        "identified_gaps": [],
        "recommendations": [],
        "note": "Checking your policy against DPDP requirements. This may take a few minutes.",
    }
    if progress:
        payload["progress"] = progress
    return payload


async def trigger_analysis_rerun(document_id: str, db: AsyncSession) -> dict:
    """Validate document and prepare for a background re-analysis run."""
    document = await get_document_by_id(db, document_id)
    if document is None:
        raise ValueError(f"Document {document_id} not found")

    if document.status == "ANALYZING":
        raise ValueError("Analysis is already in progress for this document.")

    if not document.stored_filename:
        raise ValueError("Please upload your privacy policy first.")

    clear_analysis_progress(document_id)
    clear_cancel_request(document_id)
    document.status = "QUEUED_FOR_ANALYSIS"
    await db.commit()

    return {
        "document_id": document_id,
        "status": "QUEUED_FOR_ANALYSIS",
        "message": "Compliance analysis queued. Results will update when complete.",
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
                logger.warning(f"Analysis skipped: document {document_id} not found")
                return

            clear_analysis_progress(document_id)
            clear_cancel_request(document_id)
            document.status = "ANALYZING"
            await db.commit()

            logger.info(f"Starting compliance analysis for document {document_id}")
            result = await ai_service.run_compliance_analysis(document_id, db)

            overall = result.get("overall_status", "NEEDS_REVIEW")
            if overall == "ANALYSIS_FAILED":
                document.status = "ANALYSIS_FAILED"
            elif overall == "ANALYSIS_CANCELLED":
                document.status = "AWAITING_AI_ANALYSIS" if document.stored_filename else "AWAITING_UPLOAD"
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
            clear_analysis_progress(document_id)
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
