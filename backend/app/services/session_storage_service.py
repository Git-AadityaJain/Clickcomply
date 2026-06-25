"""
Session-scoped upload storage.

Ephemeral uploads (remember=false) are cleared when the browser opens or
refreshes the site (POST /documents/prune-session). Optional shutdown wipe
is controlled by CLEAR_EPHEMERAL_ON_SHUTDOWN.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import delete, select, or_

from app.core.config import settings
from app.core.database import async_session
from app.core.logging import logger
from app.models.analysis import AnalysisResult
from app.models.document import Document
from app.services.rag_service import clear_document_vectors


def _delete_document_file(stored_filename: str | None) -> None:
    if not stored_filename:
        return
    path = Path(settings.UPLOAD_DIR) / stored_filename
    if path.is_file():
        path.unlink(missing_ok=True)


def _delete_document_files(document: Document) -> None:
    _delete_document_file(document.stored_filename)
    _delete_document_file(document.generated_policy_filename)


async def _delete_document_record(db, document: Document) -> None:
    await db.execute(
        delete(AnalysisResult).where(AnalysisResult.document_id == document.id)
    )
    await db.delete(document)


async def clear_ephemeral_uploads(
    keep_document_ids: set[str] | None = None,
) -> list[str]:
    """Remove documents not marked remember, including files and vector chunks."""
    keep_ids = keep_document_ids or set()
    removed_ids: list[str] = []

    async with async_session() as db:
        result = await db.execute(
            select(Document).where(
                or_(Document.remember.is_(False), Document.remember.is_(None))
            )
        )
        ephemeral = list(result.scalars().all())

        if not ephemeral:
            return removed_ids

        for document in ephemeral:
            if document.id in keep_ids:
                if not document.remember:
                    document.remember = True
                continue

            removed_ids.append(document.id)
            _delete_document_files(document)
            try:
                clear_document_vectors(document.id)
            except Exception as exc:
                logger.warning(
                    f"Could not clear vectors for document {document.id}: {exc}"
                )
            await _delete_document_record(db, document)

        if removed_ids or keep_ids:
            await db.commit()

        if removed_ids:
            logger.info(f"Cleared {len(removed_ids)} ephemeral document(s)")

    return removed_ids


async def apply_session_lifecycle_policy_on_shutdown() -> None:
    await clear_ephemeral_uploads()
