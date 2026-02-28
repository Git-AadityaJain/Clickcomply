"""
AI Placeholder Service — the ONLY file to replace when integrating RAG+LLM.

This module mimics the interface of a future AI compliance analysis engine.
All functions return deterministic, static responses with the same signatures
that the real AI service will use.

When AI is integrated:
    1. Replace this file with a real implementation (e.g. ai_service.py).
    2. Keep the same function signatures.
    3. No other files in the codebase need to change.
"""

from app.core.logging import logger


async def run_compliance_analysis(document_id: str) -> dict:
    """
    Placeholder for AI-driven compliance analysis.

    In production, this function will:
        - Retrieve the document content from storage
        - Run RAG over DPDP Act provisions
        - Use an LLM to identify compliance gaps
        - Return structured analysis results

    Args:
        document_id: UUID of the document to analyze.

    Returns:
        A dictionary matching the ComplianceAnalysisResponse schema.
    """
    logger.info(
        f"[AI Placeholder] Returning static analysis for document {document_id}. "
        "AI engine not yet integrated."
    )

    return {
        "overall_status": "PENDING_AI_REVIEW",
        "identified_gaps": [],
        "recommendations": [],
        "note": "AI compliance engine not yet integrated. "
                "This is a placeholder response with the same structure "
                "that the real AI engine will produce.",
    }


async def check_ai_health() -> dict:
    """
    Health check for the AI subsystem.

    Returns:
        Status dictionary indicating AI readiness.
    """
    return {
        "ai_engine": "placeholder",
        "status": "NOT_INTEGRATED",
        "message": "AI engine is architecturally ready but not yet connected.",
    }
