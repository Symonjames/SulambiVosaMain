"""
Global authentication and RBAC for all API routes.
- Every non-public request must have a valid session (validated in backend).
- Role-based access: reject with 403 if user role is not allowed for the path.
- Public routes: login, register, and a few read-only/submit endpoints only.
"""
from flask import request, g
from ..models.AccountModel import AccountModel
from ..models.SessionModel import SessionModel
from ..controllers.auth import SESSION_COOKIE_NAME

AccountDb = AccountModel()
SessionDb = SessionModel()

# ---------------------------------------------------------------------------
# PUBLIC: no authentication required (method + path pattern)
# Only login, register, and explicitly public read/submit endpoints.
# ---------------------------------------------------------------------------
PUBLIC_PATHS = [
    ("GET", "/api"),   # API index / health check
    ("POST", "/api/auth/login"),
    ("POST", "/api/auth/register"),
    ("GET", "/api/events/public"),
    ("GET", "/api/events/beneficiary-eligible"),
    ("GET", "/api/reports/public"),  # Landing page "Latest News" carousel
    ("POST", "/api/evaluation/beneficiary/validate-pin"),
    ("POST", "/api/evaluation/beneficiary"),
]

def _is_public(method, path):
    path = path.rstrip("/") or path
    path_normalized = path.rstrip("/") or "/"
    for m, p in PUBLIC_PATHS:
        if m != method:
            continue
        p_clean = p.rstrip("/") or "/"
        # API index: only exactly GET /api (or /api/) is public, not GET /api/events/ etc.
        if p_clean == "/api":
            if path_normalized == "/api":
                return True
            continue
        if path == p_clean or path.startswith(p_clean + "/"):
            return True
    return False


# ---------------------------------------------------------------------------
# RBAC: path prefix or pattern -> allowed roles. None = any authenticated.
# ---------------------------------------------------------------------------
def _get_allowed_roles(method, path):
    path = path.rstrip("/") or path
    # Admin only
    if path.startswith("/api/accounts"):
        return ["admin"]
    # Admin + Officer
    if path.startswith("/api/dashboard"):
        return ["admin", "officer"]
    if path.startswith("/api/membership"):
        return ["admin", "officer"]
    if path.startswith("/api/reports"):
        return ["admin", "officer"]
    if path.startswith("/api/feedback"):
        return ["admin", "officer"]
    if path.startswith("/api/analytics"):
        return ["admin", "officer"]
    # Requirements: GET /my = member; GET / and PATCH = admin, officer; POST = member (or public for event join - we keep protected)
    if path.startswith("/api/requirements"):
        if "/my" in path or path.endswith("/my"):
            return ["member", "admin", "officer"]
        if method in ("PATCH",):
            return ["admin", "officer"]
        if method == "GET":
            return ["admin", "officer"]
        if method == "POST":
            return ["member", "admin", "officer"]
        return ["admin", "officer"]
    # Events: all authenticated (admin, officer, member) - public paths already excluded
    if path.startswith("/api/events"):
        return ["admin", "officer", "member"]
    # Evaluation: mixed - /personal and most need auth; beneficiary already public
    if path.startswith("/api/evaluation"):
        return ["admin", "officer", "member"]
    # Auth (me, logout, etc.) - any authenticated
    if path.startswith("/api/auth"):
        return ["admin", "officer", "member"]
    # Default: any authenticated role
    return ["admin", "officer", "member"]


def _validate_session():
    """Validate session cookie or Bearer token; set g.accountSessionInfo. Returns (None, None) on success, (response, status) on failure."""
    user_token = request.cookies.get(SESSION_COOKIE_NAME) or ""
    if not user_token:
        user_token = (request.headers.get("authorization") or "").replace("Bearer ", "").strip()
    if not user_token:
        return ({"message": "Unauthorized. Please log in."}, 403)
    session_info = SessionDb.get(user_token)
    if session_info is None:
        return ({"message": "Session invalid or expired."}, 403)
    account = AccountDb.get(session_info.get("userid"))
    if account is None:
        return ({"message": "Account not found."}, 403)
    g.accountSessionInfo = account
    return (None, None)


def global_api_auth():
    """
    Run before every /api/* request. Ensures:
    - Public paths are allowed without auth.
    - All other paths require valid session and allowed role (RBAC).
    """
    if request.method == "OPTIONS":
        return None

    path = request.path
    method = request.method

    if _is_public(method, path):
        return None

    err, status = _validate_session()
    if err is not None:
        return (err, status)

    allowed = _get_allowed_roles(method, path)
    role = (g.accountSessionInfo or {}).get("accountType")
    if not role or role not in allowed:
        return ({"message": "You do not have permission to access this resource."}, 403)

    return None
