# Debugging Event Submission on Render

## What Was Added

Comprehensive debugging and error logging has been added to help troubleshoot event submission issues on Render deployment.

## Debug Logs Added

### 1. Event Controller Functions (`app/controllers/events.py`)

Both `createInternalEvent()` and `createExternalEvent()` now log:
- ✅ Start of event creation process
- ✅ Signatories creation (success or failure)
- ✅ Required field validation
- ✅ Event creation attempt
- ✅ Success with event ID
- ❌ Detailed errors with traceback
- ❌ Error type and message

### 2. Model.create Method (`app/models/Model.py`)

The `Model.create()` method now logs:
- Table name being inserted into
- Column names and count
- Data tuple length
- Generated SQL query (first 200 chars)
- Data/column count mismatch errors
- Detailed error messages with traceback

## How to View Logs on Render

### Option 1: Render Dashboard Logs

1. Go to Render Dashboard: https://dashboard.render.com
2. Select your backend service (`sulambi-backend1` or similar)
3. Click on **"Logs"** tab
4. Try submitting an event
5. Look for log entries starting with:
   - `[CREATE_INTERNAL_EVENT]` - For internal events
   - `[CREATE_EXTERNAL_EVENT]` - For external events
   - `[MODEL.CREATE]` - For database operations

### Option 2: Real-time Log Streaming

1. In Render Dashboard, click on your backend service
2. Click **"View Logs"** or **"View Live Logs"**
3. Keep this window open while testing
4. Submit an event from the frontend
5. Watch the logs appear in real-time

## What to Look For

### Success Flow
```
[CREATE_INTERNAL_EVENT] Starting event creation for user 123
[CREATE_INTERNAL_EVENT] Creating signatories...
[CREATE_INTERNAL_EVENT] Signatories created with ID: 456
[CREATE_INTERNAL_EVENT] Creating internal event...
[MODEL.CREATE] Table: "internalEvents"
[MODEL.CREATE] Columns (25): title, durationStart, ...
[MODEL.CREATE] Insert successful
[CREATE_INTERNAL_EVENT] Event created successfully with ID: 789
```

### Error Scenarios

**1. Signatories Creation Fails:**
```
[CREATE_INTERNAL_EVENT] ERROR creating signatories: [error message]
[CREATE_INTERNAL_EVENT] Error type: [ErrorType]
```

**2. Missing Required Fields:**
```
[CREATE_INTERNAL_EVENT] Missing required fields: ['field1', 'field2']
```

**3. Database Error:**
```
[MODEL.CREATE] ERROR: [error message]
[MODEL.CREATE] Error type: [ErrorType]
[MODEL.CREATE] Query was: INSERT INTO ...
```

**4. Data Mismatch:**
```
[MODEL.CREATE] ERROR: Data tuple length (20) does not match columns (25)
[MODEL.CREATE] Columns: [list of columns]
[MODEL.CREATE] Data: [data tuple]
```

## Common Issues and Solutions

### Issue: Column name mismatch
**Error:** `column "columnName" does not exist`
**Solution:** Column names are lowercase in PostgreSQL. Check if column names match.

### Issue: Data type mismatch
**Error:** `operator does not exist: type1 = type2`
**Solution:** Check if data types match (e.g., boolean vs integer, string vs number)

### Issue: Missing required field
**Error:** `KeyError: 'fieldName'`
**Solution:** Frontend is not sending required field. Check frontend form data.

### Issue: Data tuple length mismatch
**Error:** `Data tuple length (X) does not match columns (Y)`
**Solution:** Number of values doesn't match number of columns. Check model definition.

## Testing

1. **Submit an event** from the frontend
2. **Check Render logs** immediately
3. **Look for error messages** starting with `[CREATE_*]` or `[MODEL.CREATE]`
4. **Copy the error details** for debugging
5. **Check the query** that was generated
6. **Verify data types** match expected types

## Next Steps

If you see an error:
1. Copy the full error message from logs
2. Check which step failed (signatories, validation, or database insert)
3. Look at the query that was generated
4. Verify the error type and message
5. Use this information to fix the issue

The logs will now show exactly where the error occurs and what data is being used, making it much easier to debug!

