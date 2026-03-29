"""
Map legacy local paths (uploads/... or bare filenames) to Cloudinary HTTPS delivery URLs.

Production does not serve /uploads; DB rows that still hold local paths break in the browser.
If the same file exists in Cloudinary with public_id uploads/<relative>, delivery works without a DB migration.
"""
from __future__ import annotations

from urllib.parse import quote

from ..config.cloudinary_setup import _env_strip, cloudinary_credentials_ok

# Deliver as raw for non-image documents (Cloudinary /raw/upload/).
_RAW_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".zip",
    ".txt",
    ".csv",
}


def _resource_slug(rel_path: str) -> str:
    ext = ""
    if "." in rel_path:
        ext = rel_path[rel_path.rfind(".") :].lower()
    if ext in _RAW_EXTENSIONS:
        return "raw"
    if ext in (".mp4", ".webm", ".mov"):
        return "video"
    return "image"


def rewrite_legacy_media_url(stored: str) -> str:
    """
    If value is already an absolute URL, return unchanged.
    If Cloudinary is configured and value looks like a legacy uploads path, return https://res.cloudinary.com/...
    Otherwise return the original string.
    """
    s = (stored or "").strip()
    if not s:
        return s
    low = s.lower()
    if low.startswith("http://") or low.startswith("https://"):
        return s
    if "res.cloudinary.com" in low:
        return s
    if not cloudinary_credentials_ok():
        return s

    cloud = _env_strip("CLOUDINARY_CLOUD_NAME")
    if not cloud:
        return s

    normalized = s.replace("\\", "/").strip()
    if ".." in normalized or normalized.startswith("/"):
        return s

    if normalized.lower().startswith("uploads/"):
        rel = normalized[8:].lstrip("/")
    else:
        rel = normalized.lstrip("/")

    if not rel or ".." in rel:
        return s

    public_path = f"uploads/{rel}"
    encoded = "/".join(quote(part, safe="") for part in public_path.split("/"))
    slug = _resource_slug(rel)
    return f"https://res.cloudinary.com/{cloud}/{slug}/upload/{encoded}"


def rewrite_report_photos_in_place(report: dict | None) -> None:
    """Normalize report['photos'] list items to HTTPS where possible."""
    if not report or not isinstance(report, dict):
        return
    photos = report.get("photos")
    if isinstance(photos, str):
        parts = [p.strip() for p in photos.split(",") if p.strip()]
        report["photos"] = [rewrite_legacy_media_url(p) for p in parts]
    elif isinstance(photos, list):
        report["photos"] = [
            rewrite_legacy_media_url(str(p).strip())
            for p in photos
            if str(p).strip()
        ]


def rewrite_requirement_files_in_place(req: dict | None) -> None:
    """Rewrite medCert / waiver when still stored as local paths."""
    if not req or not isinstance(req, dict):
        return
    for key in ("medCert", "waiver"):
        val = req.get(key)
        if val:
            req[key] = rewrite_legacy_media_url(str(val).strip())
