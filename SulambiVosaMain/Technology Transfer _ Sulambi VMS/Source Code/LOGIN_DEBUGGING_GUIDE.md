# Login Debugging Guide

## What Was Added

I've added comprehensive logging to help debug login issues. The logging tracks:
1. **Frontend login attempts** - What credentials are being sent
2. **API requests** - Network calls to the backend
3. **Backend authentication** - Server-side processing
4. **Database queries** - Account lookup operations

---

## Expected Logs

### When You Try to Login

#### 1. Frontend Console (Browser DevTools - F12)

**On Login Button Click:**
```
[FRONTEND_LOGIN] ========================================
[FRONTEND_LOGIN] Login attempt started
[FRONTEND_LOGIN] Username: Admin
[FRONTEND_LOGIN] Password: ************
[FRONTEND_LOGIN] Making API request to /auth/login...
```

**If Server is Running:**
```
[API_REQUEST] {
  method: "POST",
  url: "http://localhost:8000/api/auth/login",
  fullUrl: "http://localhost:8000/api/auth/login",
  hasData: true,
  dataKeys: ["username", "password"]
}

[API_RESPONSE] {
  status: 200,
  url: "/auth/login",
  data: { message: "Successfully logged in", session: {...}, ... }
}

[FRONTEND_LOGIN] ✅ API response received
[FRONTEND_LOGIN] Status: 200
[FRONTEND_LOGIN] Response data: { message: "Successfully logged in", ... }
[FRONTEND_LOGIN] ✅ Session data received
[FRONTEND_LOGIN] Account Type: admin
[FRONTEND_LOGIN] Token: abc123def456ghi789...
[FRONTEND_LOGIN] Token saved to localStorage
[FRONTEND_LOGIN] ========================================
```

**If Server is NOT Running:**
```
[API_REQUEST] {
  method: "POST",
  url: "http://localhost:8000/api/auth/login",
  ...
}

[API_ERROR] {
  message: "Network Error",
  code: "ERR_NETWORK",
  url: "/auth/login",
  status: undefined,
  statusText: undefined,
  data: undefined
}

[FRONTEND_LOGIN] ❌ ERROR: Login failed
[FRONTEND_LOGIN] Error type: AxiosError
[FRONTEND_LOGIN] Error message: Network Error
[FRONTEND_LOGIN] Error code: ERR_NETWORK
[FRONTEND_LOGIN] 🚨 NETWORK ERROR: Backend server might be offline!
[FRONTEND_LOGIN] ========================================
```

**If Invalid Credentials:**
```
[API_ERROR] {
  message: "Request failed with status code 403",
  code: "ERR_BAD_REQUEST",
  url: "/auth/login",
  status: 403,
  statusText: "FORBIDDEN",
  data: { message: "Invalid Credentials" }
}

[FRONTEND_LOGIN] ❌ ERROR: Login failed
[FRONTEND_LOGIN] Error status: 403
[FRONTEND_LOGIN] Error response: { message: "Invalid Credentials" }
```

---

#### 2. Backend Console (Terminal where server.py is running)

**On Login Request:**
```
[AUTH_LOGIN] ========================================
[AUTH_LOGIN] Login request received
[AUTH_LOGIN] Username: Admin
[AUTH_LOGIN] Password: ************
[AUTH_LOGIN] Attempting authentication...
```

**If Authentication Succeeds:**
```
[AUTH_MODEL] Authenticating user: Admin
[AUTH_MODEL] Executing query: SELECT ... FROM accounts WHERE username=? AND password=? AND active=?
[AUTH_MODEL] Query parameters: username=Admin, password=************, active=True
[AUTH_MODEL] Query result: True
[AUTH_MODEL] ✅ Account found: ID=1, Type=admin
[AUTH_MODEL] Creating session token...
[AUTH_MODEL] ✅ Session created: token=abc123def456ghi789...
[AUTH_LOGIN] ✅ Authentication successful!
[AUTH_LOGIN] Account Type: admin
[AUTH_LOGIN] User ID: 1
[AUTH_LOGIN] Token: abc123def456ghi789...
[AUTH_LOGIN] ========================================
```

**If Authentication Fails:**
```
[AUTH_MODEL] Authenticating user: Admin
[AUTH_MODEL] Executing query: SELECT ... FROM accounts WHERE username=? AND password=? AND active=?
[AUTH_MODEL] Query parameters: username=Admin, password=wrongpassword, active=True
[AUTH_MODEL] Query result: False
[AUTH_MODEL] ❌ No matching account found or account is inactive
[AUTH_LOGIN] ❌ Authentication failed - Invalid credentials
[AUTH_LOGIN] ========================================
```

**If Server Error:**
```
[AUTH_LOGIN] ❌ ERROR: Unexpected error: [error message]
[AUTH_LOGIN] Traceback: [full stack trace]
```

---

## How to Use These Logs

### Step 1: Check if Server is Running

**Look for these in the backend terminal:**
- If you see `* Running on http://127.0.0.1:8000` → Server is running ✅
- If you see nothing or errors → Server is NOT running ❌

**Or check frontend console:**
- If you see `[API_ERROR] code: "ERR_NETWORK"` → Server is offline ❌
- If you see `[API_RESPONSE]` → Server is running ✅

### Step 2: Check Credentials

**Backend logs will show:**
- What username was received
- Whether password matches (without showing actual password)
- Whether account is active

**Common Issues:**
- `Query result: False` → Wrong password or username
- `Account is inactive` → Account exists but is deactivated

### Step 3: Check Network Connection

**Frontend logs will show:**
- The exact URL being called
- Network errors if server is unreachable
- Response status codes

---

## Default Credentials

If you need to test with default accounts:

**Admin:**
- Username: `Admin`
- Password: `sulambi@2024`

**Officer:**
- Username: `Sulambi-Officer`
- Password: `password@2024`

---

## Troubleshooting

### Problem: "Network Error" in Frontend

**Solution:** Start the backend server:
```powershell
cd "C:\Users\Symon\Desktop\CODE FOR SULAMBI\Technology Transfer _ Sulambi VMS\Source Code\sulambi-backend-main\sulambi-backend-main"
python server.py
```

### Problem: "Invalid Credentials" but credentials are correct

**Check logs for:**
1. Username spelling (case-sensitive)
2. Password spelling (case-sensitive)
3. Account active status: `active=True` in database

### Problem: No logs appearing

**Check:**
1. Browser console is open (F12)
2. Backend terminal is visible
3. Server is actually running (check for Flask startup message)

---

## What to Paste Back

When you try to login, copy and paste:

1. **Frontend Console Logs** (all lines starting with `[FRONTEND_LOGIN]`, `[API_REQUEST]`, `[API_RESPONSE]`, `[API_ERROR]`)
2. **Backend Terminal Logs** (all lines starting with `[AUTH_LOGIN]`, `[AUTH_MODEL]`)

This will help identify:
- Is the server running?
- Are credentials being sent correctly?
- Is the database query working?
- Where exactly is the failure happening?

---

**Status:** ✅ Logging Added - Ready for Testing
**Next Step:** Try to login and paste the logs here!












