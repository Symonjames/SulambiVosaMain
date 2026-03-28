"""
Cloudinary configuration from environment.
Used for all file uploads (no local /uploads persistence).

Render injects env vars at runtime — no .env file required in production.
Values are stripped to avoid copy/paste whitespace issues.
"""
import os

from dotenv import load_dotenv

load_dotenv()

REQUIRED_ENV = (
    "CLOUDINARY_CLOUD_NAME",
    "CLOUDINARY_API_KEY",
    "CLOUDINARY_API_SECRET",
)


def _env_strip(key: str) -> str:
    v = os.getenv(key)
    return (v or "").strip()


def cloudinary_credentials_ok() -> bool:
    return all(_env_strip(k) for k in REQUIRED_ENV)


def missing_cloudinary_message() -> str:
    return (
        "Cloudinary is not configured. Set CLOUDINARY_CLOUD_NAME, "
        "CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET."
    )


def configure_cloudinary() -> None:
    """Call before any upload. Idempotent. Uses os.environ (Render-compatible)."""
    import cloudinary

    cloudinary.config(
        cloud_name=_env_strip("CLOUDINARY_CLOUD_NAME"),
        api_key=_env_strip("CLOUDINARY_API_KEY"),
        api_secret=_env_strip("CLOUDINARY_API_SECRET"),
        secure=True,
    )
