# Debugging Workflow Guide

This guide follows an iterative debugging pattern to systematically identify and fix bugs.

## The Debugging Cycle

1. **Explain the Bug** - Document what's happening
2. **Add Logging** - Instrument the code to capture relevant information
3. **Define Expected Logs** - Document what logs you expect to see
4. **Run and Capture Logs** - Execute the code and collect actual logs
5. **Compare and Iterate** - Analyze differences and repeat if needed

---

## Step 1: Explain the Bug

### Bug Description Template

```markdown
## Bug Report

**Date:** [Date]
**Component:** [Frontend/Backend/API/Database]
**Feature:** [Which feature is affected?]
**Severity:** [Critical/High/Medium/Low]

### Symptoms
- What is happening?
- When does it occur?
- What should happen instead?

### Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Error Messages
- [Any error messages or stack traces]

### Environment
- Backend: [Running/Not Running]
- Frontend: [Running/Not Running]
- Database: [SQLite/PostgreSQL]
- Browser: [If applicable]
```

---

## Step 2: Add Logging

### Backend Logging (Python/Flask)

Add logging at key points in your code:

```python
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# In your function/route:
def yourFunction():
    logger.info(f"[FUNCTION_NAME] Starting execution")
    logger.debug(f"[FUNCTION_NAME] Input parameters: {params}")
    
    try:
        # Your code here
        logger.debug(f"[FUNCTION_NAME] Step 1 completed: {result}")
        
        # More code
        logger.debug(f"[FUNCTION_NAME] Step 2 completed: {result}")
        
        logger.info(f"[FUNCTION_NAME] Successfully completed")
        return result
        
    except Exception as e:
        logger.error(f"[FUNCTION_NAME] Error occurred: {str(e)}")
        logger.error(f"[FUNCTION_NAME] Traceback: {traceback.format_exc()}")
        raise
```

### Frontend Logging (React/TypeScript)

Add console logging at key points:

```typescript
// At the start of a function/component
console.log('[COMPONENT_NAME] Function called', { params });

// Before API calls
console.log('[COMPONENT_NAME] Making API request', { url, method, data });

// After API responses
console.log('[COMPONENT_NAME] API response received', { status, data });

// In error handlers
console.error('[COMPONENT_NAME] Error occurred', { error, stack: error.stack });

// At state changes
console.log('[COMPONENT_NAME] State updated', { previousState, newState });
```

### Database Query Logging

```python
# Before executing query
logger.debug(f"[DB_QUERY] Executing query: {query}")
logger.debug(f"[DB_QUERY] Parameters: {params}")

# After query execution
logger.debug(f"[DB_QUERY] Query result: {result}")
logger.debug(f"[DB_QUERY] Rows affected: {len(result) if isinstance(result, list) else 'N/A'}")
```

---

## Step 3: Define Expected Logs

Before running the code, document what logs you expect to see:

```markdown
## Expected Log Flow

### Scenario: [Normal Operation / Error Case]

1. **Function Entry**
   - Expected: `[FUNCTION_NAME] Starting execution`
   - Expected: `[FUNCTION_NAME] Input parameters: {...}`

2. **Step 1**
   - Expected: `[FUNCTION_NAME] Step 1 completed: {...}`

3. **Step 2**
   - Expected: `[FUNCTION_NAME] Step 2 completed: {...}`

4. **Function Exit**
   - Expected: `[FUNCTION_NAME] Successfully completed`
   - OR (if error): `[FUNCTION_NAME] Error occurred: {...}`

### Expected Values
- Parameter values should be: `[...]`
- Return value should be: `[...]`
- Database state should be: `[...]`
```

---

## Step 4: Run and Capture Logs

### Backend Logs

**Terminal Output:**
```bash
# Run your backend
python server.py

# Capture logs to file (optional)
python server.py > backend.log 2>&1
```

**What to Capture:**
- All log messages with timestamps
- Error stack traces
- Database query logs
- API request/response logs

### Frontend Logs

**Browser Console:**
1. Open Developer Tools (F12)
2. Go to Console tab
3. Clear console
4. Reproduce the bug
5. Copy all console output

**Network Tab:**
1. Go to Network tab
2. Reproduce the bug
3. Check failed requests (red)
4. Check request/response details

### Database Logs

If using SQLite with logging:
```python
# Enable SQLite query logging
import sqlite3
sqlite3.enable_callback_tracebacks(True)
```

---

## Step 5: Compare and Iterate

### Log Analysis Template

```markdown
## Actual Logs vs Expected

### Function Entry
- ✅ Expected: `[FUNCTION_NAME] Starting execution`
- ✅ Actual: `[FUNCTION_NAME] Starting execution`

### Step 1
- ✅ Expected: `[FUNCTION_NAME] Step 1 completed: {...}`
- ❌ Actual: `[FUNCTION_NAME] Step 1 completed: {...}` (DIFFERENT VALUE)

### Step 2
- ✅ Expected: `[FUNCTION_NAME] Step 2 completed: {...}`
- ❌ Actual: `[FUNCTION_NAME] Error occurred: {...}` (ERROR INSTEAD)

### Analysis
- **Issue Found:** [What's different?]
- **Root Cause:** [Why is it different?]
- **Fix Needed:** [What needs to be changed?]
```

### Iteration Steps

1. **If logs match expected but bug persists:**
   - Add more granular logging
   - Check logs from other components (frontend ↔ backend)
   - Verify database state

2. **If logs differ from expected:**
   - Identify where the divergence occurs
   - Add logging before that point
   - Check input parameters and state

3. **If error occurs:**
   - Check full stack trace
   - Verify error handling
   - Check related components

4. **Repeat:**
   - Refine logging based on findings
   - Re-run and compare again
   - Continue until root cause is identified

---

## Example: Debugging an API Endpoint

### Step 1: Explain the Bug

```markdown
## Bug: Events Not Loading

**Component:** Backend API
**Feature:** Get All Events
**Endpoint:** `GET /api/events`

### Symptoms
- Frontend shows "Loading..." indefinitely
- No events appear in the UI
- Browser console shows 500 error

### Steps to Reproduce
1. Start backend server
2. Navigate to Events page in frontend
3. Observe loading state never resolves
```

### Step 2: Add Logging

```python
# In app/controllers/events.py
import logging
logger = logging.getLogger(__name__)

def getAll():
    logger.info("[GET_ALL_EVENTS] Request received")
    
    try:
        logger.debug("[GET_ALL_EVENTS] Connecting to database")
        conn = get_db_connection()
        logger.debug("[GET_ALL_EVENTS] Database connection established")
        
        logger.debug("[GET_ALL_EVENTS] Executing query")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events")
        events = cursor.fetchall()
        logger.debug(f"[GET_ALL_EVENTS] Query returned {len(events)} events")
        
        logger.info("[GET_ALL_EVENTS] Successfully retrieved events")
        return {"data": events}, 200
        
    except Exception as e:
        logger.error(f"[GET_ALL_EVENTS] Error: {str(e)}")
        logger.error(f"[GET_ALL_EVENTS] Traceback: {traceback.format_exc()}")
        return {"message": "Error retrieving events"}, 500
```

### Step 3: Define Expected Logs

```markdown
## Expected Log Flow

1. `[GET_ALL_EVENTS] Request received`
2. `[GET_ALL_EVENTS] Connecting to database`
3. `[GET_ALL_EVENTS] Database connection established`
4. `[GET_ALL_EVENTS] Executing query`
5. `[GET_ALL_EVENTS] Query returned X events`
6. `[GET_ALL_EVENTS] Successfully retrieved events`
```

### Step 4: Run and Capture Logs

**Actual Logs:**
```
2024-01-15 10:30:15 - INFO - [GET_ALL_EVENTS] Request received
2024-01-15 10:30:15 - DEBUG - [GET_ALL_EVENTS] Connecting to database
2024-01-15 10:30:15 - ERROR - [GET_ALL_EVENTS] Error: no such table: events
2024-01-15 10:30:15 - ERROR - [GET_ALL_EVENTS] Traceback: ...
```

### Step 5: Compare and Iterate

**Analysis:**
- ❌ Expected: Database connection established
- ❌ Actual: Error - "no such table: events"
- **Root Cause:** Events table doesn't exist in database
- **Fix Needed:** Run table initialization or check table name

---

## Quick Reference: Common Logging Patterns

### API Request/Response
```python
logger.info(f"[API] {request.method} {request.path}")
logger.debug(f"[API] Headers: {dict(request.headers)}")
logger.debug(f"[API] Body: {request.get_json()}")
logger.debug(f"[API] Response: {response}")
```

### Database Operations
```python
logger.debug(f"[DB] Query: {query}")
logger.debug(f"[DB] Params: {params}")
logger.debug(f"[DB] Result count: {len(results)}")
```

### Authentication
```python
logger.info(f"[AUTH] Login attempt for user: {username}")
logger.debug(f"[AUTH] Token generated: {token[:20]}...")
logger.warning(f"[AUTH] Invalid credentials for user: {username}")
```

### File Operations
```python
logger.info(f"[FILE] Uploading file: {filename}")
logger.debug(f"[FILE] File size: {file_size} bytes")
logger.debug(f"[FILE] Saved to: {file_path}")
```

---

## Tips for Effective Debugging

1. **Use Consistent Prefixes:** `[COMPONENT_NAME]` makes logs easy to filter
2. **Log at Multiple Levels:** INFO for flow, DEBUG for details, ERROR for problems
3. **Include Context:** Log relevant variables, IDs, timestamps
4. **Don't Log Sensitive Data:** Avoid logging passwords, tokens, PII
5. **Use Structured Logging:** JSON format for easier parsing
6. **Time Your Operations:** Log execution time for performance issues
7. **Log Before and After:** Capture state changes
8. **Remove Debug Logs:** Clean up excessive logging after fixing bugs

---

## Next Steps After Finding the Bug

1. **Document the Fix:** Update this file with the solution
2. **Add Tests:** Create tests to prevent regression
3. **Review Logging:** Keep useful logs, remove excessive ones
4. **Update Documentation:** Document the issue and solution

---

**Last Updated:** [Date]
**Version:** 1.0












