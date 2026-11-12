from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import FileResponse
from app.core.storage import verify_signed_token, get_absolute_path

router = APIRouter()

@router.get("/serve")
def serve_signed_file(
    path: str = Query(..., description="Relative storage path"),
    expires: int = Query(..., description="Expiration timestamp"),
    sig: str = Query(..., description="HMAC SHA-256 signature")
):
    """
    Secure signed URL file server. Never exposes raw filesystem paths.
    Validates cryptographic authenticity and expiration.
    """
    if not verify_signed_token(path, expires, sig):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Signed file URL is invalid, tampered, or has expired."
        )

    try:
        abs_path = get_absolute_path(path)
        if not abs_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requested file not found")
        
        media_type = "application/pdf" if path.endswith(".pdf") else "image/jpeg" if path.endswith((".jpg", ".jpeg")) else "image/png"
        return FileResponse(abs_path, media_type=media_type, filename=abs_path.name)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

