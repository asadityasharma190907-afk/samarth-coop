import logging
import os
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

logger = logging.getLogger(__name__)

# Directory configuration for local fallback
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


async def save_photo(file: UploadFile, prefix: str = "proof") -> str:
    """Validate and store an uploaded photo.

    Supports Cloudinary when configured, otherwise saves to local
    uploads/ directory.
    """
    content_type = file.content_type or ""
    if content_type not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG, PNG, and WebP images are allowed.",
        )

    # Read content and enforce max file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the 5MB limit.",
        )
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    # Cloudinary Integration (if configured)
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
    storage_mode = os.getenv("PHOTO_STORAGE", "local").lower()

    if storage_mode == "cloudinary" and cloud_name and api_key and api_secret:
        try:
            import cloudinary  # type: ignore[import-untyped,reportMissingImports]
            import cloudinary.uploader  # type: ignore[import-untyped,reportMissingImports]

            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret,
                secure=True,
            )
            upload_result = cloudinary.uploader.upload(
                content,
                folder="samarth_proofs",
                resource_type="image",
            )
            secure_url = upload_result.get("secure_url")
            if secure_url:
                return str(secure_url)
        except Exception as exc:
            logger.warning("Cloudinary upload failed, falling back to local: %s", exc)

    # Local Filesystem Storage Fallback
    ext = ALLOWED_EXTENSIONS[content_type]
    filename = f"{prefix}_{uuid.uuid4().hex[:12]}{ext}"
    target_path = UPLOAD_DIR / filename

    target_path.write_bytes(content)

    return f"/uploads/{filename}"
