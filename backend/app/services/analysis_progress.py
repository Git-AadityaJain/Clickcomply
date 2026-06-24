"""
In-memory analysis progress for active document evaluations.

Used by the dashboard to show rule-by-rule progress while status is ANALYZING.
"""

from __future__ import annotations

from threading import Lock

_lock = Lock()
_progress: dict[str, dict] = {}


def set_analysis_progress(
    document_id: str,
    *,
    current: int,
    total: int,
    rule_id: str,
    rule_label: str,
) -> None:
    with _lock:
        _progress[document_id] = {
            "current": current,
            "total": total,
            "rule_id": rule_id,
            "rule_label": rule_label,
        }


def get_analysis_progress(document_id: str) -> dict | None:
    with _lock:
        return _progress.get(document_id)


def clear_analysis_progress(document_id: str) -> None:
    with _lock:
        _progress.pop(document_id, None)
