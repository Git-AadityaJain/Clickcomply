"""
Utilities for file handling, storage, and metadata extraction.

Provides functions for saving uploaded files, generating storage names,
formatting file sizes, and extracting file metadata.
"""

import os
import uuid
from pathlib import Path
from datetime import datetime, timezone


def get_upload_dir(upload_dir: str) -> Path:
    """
    Get or create the upload directory.
    
    Args:
        upload_dir: Path to the upload directory from config
        
    Returns:
        Path object pointing to the upload directory
    """
    upload_path = Path(upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


def generate_stored_filename(original_filename: str) -> str:
    """
    Generate a UUID-based stored filename to prevent collisions.
    
    Preserves the original file extension and a sanitized version of the
    original name for debugging/auditing purposes.
    
    Args:
        original_filename: The user's uploaded filename (e.g., "privacy_policy.pdf")
        
    Returns:
        UUID-based filename (e.g., "4b2e9f6c-privacy_policy.pdf")
    """
    # Split name and extension
    name_parts = original_filename.rsplit(".", 1)
    name = name_parts[0]
    ext = f".{name_parts[1]}" if len(name_parts) > 1 else ""
    
    # Generate UUID and truncate for readability
    unique_id = str(uuid.uuid4())[:8]
    
    # Sanitize original name (remove special chars, keep alphanumeric/underscore/hyphen)
    sanitized_name = "".join(c if c.isalnum() or c in "_-" else "_" for c in name)
    
    return f"{unique_id}-{sanitized_name}{ext}"


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human-readable format (B, KB, MB, GB).
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Formatted string (e.g., "2.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def save_uploaded_file(
    file_content: bytes,
    stored_filename: str,
    upload_dir: Path,
) -> str:
    """
    Save uploaded file content to disk.
    
    Args:
        file_content: Raw bytes of the uploaded file
        stored_filename: The UUID-based filename to save as
        upload_dir: Path object for the upload directory
        
    Returns:
        Full path to the saved file
        
    Raises:
        IOError: If file cannot be written
    """
    file_path = upload_dir / stored_filename
    
    try:
        with open(file_path, "wb") as f:
            f.write(file_content)
        return str(file_path)
    except IOError as e:
        raise IOError(f"Failed to save file {stored_filename}: {str(e)}")


def extract_file_metadata(
    file_content: bytes,
    original_filename: str,
    uploader_ip: str | None = None,
) -> dict:
    """
    Extract metadata from uploaded file.
    
    Args:
        file_content: Raw bytes of the uploaded file
        original_filename: User's original filename
        uploader_ip: IP address of the uploader
        
    Returns:
        Dictionary containing:
            - file_size: Size in bytes
            - upload_timestamp: Current UTC timestamp
            - uploader_ip: IP address (or None)
            - original_filename: User's filename
            - stored_filename: UUID-based filename
    """
    return {
        "file_size": len(file_content),
        "upload_timestamp": datetime.now(timezone.utc),
        "uploader_ip": uploader_ip,
        "original_filename": original_filename,
        "stored_filename": generate_stored_filename(original_filename),
    }
