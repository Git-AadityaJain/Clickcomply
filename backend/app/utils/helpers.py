"""
Utility helpers used across the ClickComply backend.

Contains shared functions that don't belong to a specific service
or domain module.
"""

import uuid


def generate_uuid() -> str:
    """Generate a new UUID v4 string."""
    return str(uuid.uuid4())


def normalize_document_type(doc_type: str) -> str:
    """
    Normalizes a document type string to a consistent format.

    Example:
        "Privacy Policy" -> "privacy_policy"
        "Terms of Service" -> "terms_of_service"
    """
    return doc_type.strip().lower().replace(" ", "_")
