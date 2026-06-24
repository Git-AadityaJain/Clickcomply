"""
In-memory analysis progress and cancellation for active document evaluations.
"""

from __future__ import annotations

from threading import Lock

_lock = Lock()
_progress: dict[str, dict] = {}
_cancel_requests: set[str] = set()


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


def request_analysis_cancel(document_id: str) -> None:
    with _lock:
        _cancel_requests.add(document_id)


def is_cancel_requested(document_id: str) -> bool:
    with _lock:
        return document_id in _cancel_requests


def clear_cancel_request(document_id: str) -> None:
    with _lock:
        _cancel_requests.discard(document_id)
