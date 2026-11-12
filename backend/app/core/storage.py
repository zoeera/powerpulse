import os
import hmac
import hashlib
import time
from pathlib import Path
from typing import Optional, Tuple
from app.core.config import settings

def compute_file_hash(content: bytes) -> str:
    """Compute SHA-256 hash of file content for deduplication."""
    return hashlib.sha256(content).hexdigest()

def ensure_storage_dir(subdir: str = "") -> Path:
    base = Path(settings.STORAGE_PATH)
    target = base / subdir if subdir else base
    target.mkdir(parents=True, exist_ok=True)
    return target

def save_uploaded_file(content: bytes, filename: str, subdir: str = "bills") -> Tuple[str, str]:
    """
    Saves file and returns (relative_path, sha256_hash).
    """
    file_hash = compute_file_hash(content)
    directory = ensure_storage_dir(subdir)
    # Prefix filename with hash for uniqueness
    safe_filename = f"{file_hash[:12]}_{filename}"
    file_path = directory / safe_filename
    
    with open(file_path, "wb") as f:
        f.write(content)
        
    relative_path = f"{subdir}/{safe_filename}"
    return relative_path, file_hash

def generate_signed_url(relative_path: str, expires_in_minutes: Optional[int] = None) -> str:
    """
    Generates a cryptographically signed URL query token for a stored resource.
    Format: /api/v1/files/serve?path=<rel>&expires=<timestamp>&signature=<hmac>
    """
    if expires_in_minutes is None:
        expires_in_minutes = settings.STORAGE_URL_EXPIRES_MINUTES
    
    expires_at = int(time.time()) + (expires_in_minutes * 60)
    data_to_sign = f"{relative_path}:{expires_at}"
    signature = hmac.new(
        settings.STORAGE_SIGNING_SECRET.encode("utf-8"),
        data_to_sign.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    return f"/api/v1/files/serve?path={relative_path}&expires={expires_at}&sig={signature}"

def verify_signed_token(relative_path: str, expires_at: int, signature: str) -> bool:
    """Verifies that the signed URL has not expired and the signature is authentic."""
    if int(time.time()) > expires_at:
        return False
    
    expected_data = f"{relative_path}:{expires_at}"
    expected_sig = hmac.new(
        settings.STORAGE_SIGNING_SECRET.encode("utf-8"),
        expected_data.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_sig, signature)

def get_absolute_path(relative_path: str) -> Path:
    base = Path(settings.STORAGE_PATH).resolve()
    target = (base / relative_path).resolve()
    # Security check against path traversal
    if not str(target).startswith(str(base)):
        raise PermissionError("Path traversal attempt detected")
    return target

