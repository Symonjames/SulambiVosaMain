"""
Production-ready CORS and cookie config for Render + custom domain.

Checklist (Render backend):
  - FRONTEND_URL = https://www.sulambi-vosa.com   (no trailing slash)
  - CORS: specific origins only, supports_credentials=True (never "*")
  - Cookie on login: Secure=True, SameSite=None when cross-origin

Cross-origin: frontend (www.sulambi-vosa.com) and backend (sulambi-backend1.onrender.com)
are different origins, so the session cookie MUST be SameSite=None; Secure or the
browser will not send it on API requests → 403 after login.
"""
import os

# ---------------------------------------------------------------------------
# Frontend origin (single source of truth for production)
# Set on Render: FRONTEND_URL = https://www.sulambi-vosa.com
# ---------------------------------------------------------------------------
FRONTEND_URL = (os.getenv("FRONTEND_URL") or "").strip().rstrip("/")

def is_production_cross_origin():
  """True when frontend is on a different origin (e.g. custom domain) than backend (Render)."""
  return bool(FRONTEND_URL)


def get_cors_origins():
  """Allowed origins for CORS. Never use '*' when using credentials (cookies)."""
  origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:3000",
  ]
  # Always allow known production frontends (even if FRONTEND_URL is mis-set to localhost on Render).
  production_frontends = [
    "https://www.sulambi-vosa.com",
    "https://sulambi-vosa.com",
    "https://sulambi-frontend1.onrender.com",
    "https://sulambi-vosa.onrender.com",
  ]
  for o in production_frontends:
    if o not in origins:
      origins.append(o)

  if FRONTEND_URL:
    if FRONTEND_URL not in origins:
      origins.append(FRONTEND_URL)
    # Often both www and non-www are used
    if FRONTEND_URL.startswith("https://www."):
      alt = FRONTEND_URL.replace("https://www.", "https://", 1)
      if alt not in origins:
        origins.append(alt)
    elif FRONTEND_URL.startswith("https://") and "www." not in FRONTEND_URL:
      alt = FRONTEND_URL.replace("https://", "https://www.", 1)
      if alt not in origins:
        origins.append(alt)
  return origins


def cookie_attrs_cross_origin():
  """
  Cookie attributes for cross-origin (frontend on custom domain, backend on Render).
  Must use Secure=True, SameSite=None so the browser sends the cookie on API requests.
  """
  return {
    "httponly": True,
    "secure": True,
    "samesite": "None",
    "max_age": 7 * 24 * 3600,  # 7 days
    "path": "/",
  }


def cookie_attrs_same_site(secure: bool):
  """Cookie attributes for same-site or local dev (Lax is enough)."""
  return {
    "httponly": True,
    "secure": secure,
    "samesite": "Lax",
    "max_age": 7 * 24 * 3600,
    "path": "/",
  }
