# Beneficiary PIN, Member Token Auth & Survey Module – Validation Report

## 1. Beneficiary PIN logic

### 1.1 Event proposal (setting the PIN)
- **Frontend:** `EventProposalForm` (internal & external) includes field `beneficiaryEvaluationPin` with 5-digit validation (`maxLength: 5`, `inputMode: "numeric"`, digits-only `onUse`).
- **Payload:** `createInternalEvent` / `createExternalEvent` send full `formData`, which includes `beneficiaryEvaluationPin`.
- **Backend:** `events.py`:
  - `_validate_beneficiary_pin()`: requires non-empty, exactly 5 digits, numbers only; returns `(True, pin)` or `(False, error_message)`.
  - Internal/external **create** and **patch** use this validator and persist `beneficiaryEvaluationPin` to the DB.
- **Conclusion:** PIN is validated and stored correctly when creating/updating events.

### 1.2 Exposing events to beneficiaries (no PIN sent)
- **Backend:** `getBeneficiaryEligibleEvents()`:
  - Returns only events that are: public, accepted (not editing/rejected), **ended**, and ended **within the last 7 days**.
  - Only includes events that have a non-empty `beneficiaryEvaluationPin`.
  - **Removes** `beneficiaryEvaluationPin` from the response (`e.pop("beneficiaryEvaluationPin", None)`).
  - Sets `requiresBeneficiaryPin: True` on each returned event.
- **Conclusion:** PIN is never sent to the frontend; only a flag that a PIN is required.

### 1.3 Survey submission (validating the PIN)
- **Frontend:** `BeneficiariesEvaluationForm`:
  - If `selectedEvent.requiresBeneficiaryPin` is true, it requires a non-empty PIN before submit and sends `(eventPin || "").trim()` as `pin` in the payload.
  - `evaluationAnalytics.submitBeneficiaryEvaluation(..., pin)` adds `payload.pin = pin` when provided.
- **Backend:** `evaluation.submitBeneficiaryEvaluation()`:
  - Loads event from DB and reads stored `beneficiaryEvaluationPin` (`event_required_pin`).
  - Returns 400 if event has no PIN set.
  - Requires `request.json.get("pin")`: missing → 400 "Event PIN is required"; not 5 digits → 400 "Invalid PIN format"; mismatch → 400 "Invalid or missing event PIN".
- **Conclusion:** PIN is required and validated correctly on submit; only correct PIN allows submission.

### 1.4 Optional improvement (done)
- Frontend error handling now prefers `error.response?.data?.error` (user-facing message) over `error.response?.data?.message` so backend messages like "Please enter the correct event PIN to submit beneficiary feedback." are shown.

---

## 2. Member token authentication

### 2.1 Frontend
- **Storage:** Token is stored in `localStorage` under key `"token"` on login (`OfficerLogin`).
- **Sending:** `src/api/init.ts` axios interceptor: for every request, `Authorization: "Bearer " + token` is set when `localStorage.getItem("token")` is present.
- **Logout:** `PageLayout` logout calls `logout(usertoken)` and then `localStorage.removeItem("token")`.
- **Protected pages:** e.g. `RequirementEvalPage` checks `localStorage.getItem("token")` and `accountType` on mount; redirects to `/login` with a message if missing or insufficient role.

### 2.2 Backend
- **Middleware:** `tokenCheck.authCheckMiddleware(accountType=[])`:
  - Reads `Authorization` header, strips `"Bearer "`.
  - Returns 403 "Unauthorized action" if token is empty.
  - Looks up session by token (`SessionDb.get(userToken)`); returns 403 "Token invalid" if not found.
  - Loads account by `userid`; returns 403 "Session expired" if not found.
  - If `accountType` list is non-empty, returns 403 "User not permitted for action" if `accountSessionInfo["accountType"]` not in list.
  - Sets `g.accountSessionInfo` on success.
- **Usage:** Applied in:
  - **Events:** All routes except `/api/events/public` and `/api/events/beneficiary-eligible` (both skip auth).
  - **Requirements:** e.g. `authCheckMiddleware(["member", "admin", "officer"])` or `["admin", "officer"]` per route.
  - **Accounts:** `authCheckMiddleware(["admin", "officer"])`.
  - **Evaluation:** Only `/api/evaluation/personal` is explicitly protected; POST `/api/evaluation/beneficiary` is **not** protected (public submission by beneficiaries).

### 2.3 Conclusion
- Token is stored, sent, and cleared correctly on the frontend.
- Backend validates token and session and enforces account type where required.
- Public routes (public events, beneficiary-eligible events, beneficiary evaluation submit) correctly skip auth.

---

## 3. Survey module: PIN handling and event list

### 3.1 Which events are shown
- **API:** `GET /api/events/beneficiary-eligible` (no auth).
- **Criteria:** Public, accepted, **ended** (`durationEnd <= now`), ended **within last 7 days** (`durationEnd >= cutoff`), and event has a non-empty `beneficiaryEvaluationPin`.
- **Frontend:** `BeneficiaryEvaluationPage` calls `getBeneficiaryEligibleEvents()`, maps response to `EvaluationEventOption[]` with `requiresBeneficiaryPin: true`, sorted by `durationEnd` descending.
- **Conclusion:** Only eligible, PIN-configured events are shown; all displayed events require a PIN.

### 3.2 PIN input and submit
- **UI:** When user selects an event, if `requiresBeneficiaryPin` is true, `BeneficiariesEvaluationForm` shows the "Event PIN" field (5 digits).
- **Validation:** Submit is blocked with a warning if `requiresBeneficiaryPin` is true and PIN is empty.
- **Payload:** PIN is sent as `payload.pin`; backend validates format and value before inserting into `satisfactionSurveys`.
- **Conclusion:** Survey module correctly requires and processes PIN and displays only the appropriate events.

---

## Summary

| Area | Status | Notes |
|------|--------|--------|
| Beneficiary PIN – set on event | OK | Validated 5 digits on backend; stored in DB. |
| Beneficiary PIN – never exposed | OK | Removed in `getBeneficiaryEligibleEvents`; only `requiresBeneficiaryPin` sent. |
| Beneficiary PIN – survey submit | OK | Required and validated; wrong PIN → 400 with clear message. |
| Member token – storage & send | OK | localStorage; Bearer header on all requests. |
| Member token – backend | OK | authCheckMiddleware validates token/session/accountType. |
| Public vs protected routes | OK | Public events, beneficiary-eligible, beneficiary submit are public; rest protected. |
| Survey event list | OK | Only eligible, ended-within-7-days, PIN-set events. |
| Survey PIN flow | OK | PIN required when `requiresBeneficiaryPin`; error message improved to show backend `error` text. |
