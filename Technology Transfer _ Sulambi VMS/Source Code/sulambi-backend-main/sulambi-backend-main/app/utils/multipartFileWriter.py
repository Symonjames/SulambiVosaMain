"""
Multipart uploads: in-memory only (no disk), then Cloudinary.

Flask/Werkzeug FileStorage already buffers uploads in memory or temp files;
we read into bytes and upload via Cloudinary (same idea as Multer memoryStorage).
The Python cloudinary SDK used here exposes upload(); we buffer to BytesIO
for a clean in-memory path to the API.
"""
from __future__ import annotations

import io
import logging
from uuid import uuid4

import cloudinary.uploader
from dotenv import load_dotenv
from flask import request
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import BadRequest

from ..config.cloudinary_setup import (
    configure_cloudinary,
    cloudinary_credentials_ok,
    missing_cloudinary_message,
)

load_dotenv()

logger = logging.getLogger(__name__)

# Allowed file extensions for requirements documents (PDF, DOC/DOCX, images)
ALLOWED_EXTENSIONS = {
    "pdf",
    "doc",
    "docx",
    "jpg",
    "jpeg",
    "png",
    "gif",
    "bmp",
    "webp",
    "svg",
    "ico",
    "tiff",
    "tif",
}

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/gif",
    "image/bmp",
    "image/webp",
    "image/svg+xml",
    "image/x-icon",
    "image/tiff",
    "image/x-tiff",
}


def is_allowed_file(filename: str, content_type: str) -> bool:
    if not filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return False
    ct = (content_type or "").strip().lower()
    if not ct:
        return True
    if ct in ALLOWED_MIME_TYPES:
        return True
    # Mobile/some clients send application/octet-stream for camera picks — allow if extension is allowed
    if ct == "application/octet-stream":
        return True
    return False


def _filestorage_to_bytes(fs: FileStorage) -> bytes:
    """Read entire upload into memory (no save to disk)."""
    try:
        fs.stream.seek(0)
    except (OSError, ValueError, io.UnsupportedOperation):
        pass
    data = fs.read()
    if not data:
        raise BadRequest("Empty file upload.")
    return data


def _upload_buffer_to_cloudinary(
    data: bytes,
    *,
    folder: str,
    public_id_base: str,
    resource_type: str = "auto",
) -> dict:
    """
    Upload bytes to Cloudinary (in-memory buffer; no local file).
    Returns the API result dict (includes secure_url).
    """
    configure_cloudinary()
    buffer = io.BytesIO(data)
    buffer.seek(0)
    try:
        return cloudinary.uploader.upload(
            buffer,
            folder=folder,
            public_id=public_id_base,
            resource_type=resource_type,
            overwrite=False,
            use_filename=False,
            unique_filename=True,
        )
    except Exception as e:
        raise BadRequest(f"Cloudinary upload failed: {e!s}") from e


def cloudinaryFileWriter(keys: list[str], folder: str = "requirements") -> dict[str, str]:
    """
    Upload selected form file fields to Cloudinary.

    - Reads each FileStorage fully into memory (no disk).
    - Stores secure_url per field key in the returned dict.

    Raises:
        BadRequest: missing config, validation failure, or upload error.
    """
    if not cloudinary_credentials_ok():
        raise BadRequest(missing_cloudinary_message())

    key_paths: dict[str, str] = {}
    filenames = list(request.files)

    for k in filenames:
        if k not in keys:
            continue
        file = request.files.get(k)
        if file is None or file.filename == "":
            continue

        if not is_allowed_file(file.filename, file.content_type or ""):
            raise BadRequest(
                f"File '{file.filename}' is not allowed. "
                "Allowed: PDF, DOC, DOCX, and common image types."
            )

        unique_name = f"{uuid4()}_{file.filename}"
        public_id_base = unique_name.rsplit(".", 1)[0]

        try:
            data = _filestorage_to_bytes(file)
            result = _upload_buffer_to_cloudinary(
                data,
                folder=folder,
                public_id_base=public_id_base,
                resource_type="auto",
            )
        except BadRequest:
            raise
        except Exception as e:
            raise BadRequest(f"Failed to upload '{file.filename}': {e!s}") from e

        url = result.get("secure_url") or result.get("url")
        if not url or not (url.startswith("http://") or url.startswith("https://")):
            raise BadRequest("Upload succeeded but no valid URL was returned.")

        key_paths[k] = url
        try:
            from urllib.parse import urlparse

            host = urlparse(url).hostname or ""
            logger.info(
                "[CLOUDINARY_UPLOAD] ok folder=%s field=%s file=%s public_id=%s host=%s",
                folder,
                k,
                file.filename,
                result.get("public_id", ""),
                host,
            )
        except Exception:
            logger.info(
                "[CLOUDINARY_UPLOAD] ok folder=%s field=%s file=%s",
                folder,
                k,
                file.filename,
            )

    return key_paths
