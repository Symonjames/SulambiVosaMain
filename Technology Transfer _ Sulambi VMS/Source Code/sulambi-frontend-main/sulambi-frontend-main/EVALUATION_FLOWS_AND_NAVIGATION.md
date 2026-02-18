# Evaluation flows: logic, buttons, and navigation

## Who can evaluate

1. **Beneficiaries (non-members)** – people who attended the event but do not have a website account. They use the **5-digit event PIN** (or in the future could use a link that includes the event).
2. **Volunteers (members)** – people whose participation was accepted (requirement approved). They get an **evaluation link by email** (and can also open it from the officer “Show Evaluation Form” action). The link contains a **requirement token** (UUID).

---

## 1. Beneficiary evaluation (5-digit PIN) – non-members

### Entry points
- **URL:** `/beneficiary-evaluation` (public, no login).
- **Query:** `?eventId=123` to pre-select an event (optional).

### Flow
1. User opens **Beneficiary Evaluation** (e.g. from landing/menu or direct link).
2. **BeneficiaryEvaluationPage** loads and fetches **eligible events** from `GET /api/events/beneficiary-eligible` (public). Only events that:
   - have a `beneficiaryEvaluationPin` set, and
   - ended within the **last 7 days**
   are shown.
3. User **selects an event** (if more than one).
4. User **enters the 5-digit PIN** shared at the event and clicks **Continue**.
5. Frontend calls **`POST /api/evaluation/beneficiary/validate-pin`** (public) with `{ eventId, eventType, pin }`. Backend checks:
   - PIN format: exactly 5 digits.
   - Event exists and has a PIN set.
   - Event ended within the last 7 days.
   - Submitted PIN matches the event’s `beneficiaryEvaluationPin`.
6. If valid → form moves to **survey step** (rating + comment).
7. User fills the form and clicks **Submit**.
8. Frontend calls **`POST /api/evaluation/beneficiary`** (public) with eventId, eventType, criteria, comment, **and the same PIN**. Backend again validates PIN and 7-day window, then inserts into `satisfactionSurveys` with `respondentType: "Beneficiary"`.
9. On success → **navigate to `/feedback-message`** (thank-you page).

### Buttons and navigation
- **Back to Home** → `navigate('/')`.
- **Continue** (after PIN) → validate PIN, then switch to survey step (no route change).
- **Submit** → submit to API, then `navigate('/feedback-message')`.

### Backend (public)
- `GET /api/events/beneficiary-eligible` – list events eligible for beneficiary evaluation (with PIN, not exposing PIN).
- `POST /api/evaluation/beneficiary/validate-pin` – validate PIN before showing survey.
- `POST /api/evaluation/beneficiary` – submit beneficiary evaluation (requires PIN in body).

---

## 2. Volunteer evaluation (email / evaluation token) – members

### Entry points
- **Email link:** `{FRONTEND_APP_URL}/evaluation/{requirementId}`. Sent when an officer **accepts** a participant’s requirement (evaluation mail template).
- **Officer UI:** Requirement list → **Show Evaluation Form** → `navigate(\`/evaluation/${req.id}\`)` (same URL with requirement id).

### Flow
1. User opens **`/evaluation/:id`** where `id` is the **requirement ID** (UUID token).
2. **PublicForm** loads and calls **`GET /api/evaluation/validity/:id`** to check:
   - Requirement exists and is **accepted**.
   - An evaluation row exists for that requirement.
   - If already submitted (`finalized === true`) → show “already submitted” and disable submit.
   - If not yet submitted → `canSubmit: true`, show form.
3. User fills the **volunteer evaluation form** (ratings + q13, q14, comment, recommendations).
4. User clicks **Submit**.
5. Frontend calls **`POST /api/evaluation/:requirementId`** with criteria, q13, q14, comment, recommendations. Backend:
   - Ensures the requirement is evaluatable (accepted, evaluation exists, not finalized).
   - Updates the evaluation row and sets `finalized = true`.
6. On success → **navigate to `/feedback-message`**.

### Buttons and navigation
- **Submit** → `createEvaluation(id, payload)`, then `navigate('/feedback-message')`.
- No “Back” on PublicForm by default; user can use browser back.

### Backend (public so email link works without login)
- `GET /api/evaluation/validity/<requirementId>` – check if requirement is evaluatable and if already submitted. **Public.**
- `POST /api/evaluation/<requirementId>` – submit volunteer evaluation. **Public.**

The requirementId in the URL acts as the secret token; only someone with the link can submit. These endpoints are in the API public paths so the **email link works when the user is not logged in** (e.g. different device or incognito).

---

## 3. Members with accounts (in-app)

- **Member dashboard** → **Events** → join events; after acceptance they can get the same evaluation link (or open it from officer “Show Evaluation Form”).
- **Officer:** Requirement list → **Show Evaluation Form** opens `/evaluation/:id` (same PublicForm as the email link). Officer may be logged in, so validity and submit work.
- **Member** clicking the email link **while logged in** on the same browser: validity and submit also work.

So:
- **Beneficiary (PIN):** No account needed; PIN + event selection; public APIs.
- **Volunteer (token link):** Link is tied to requirement id; currently **APIs require login**, so the email link only works when the user is logged in. Making validity and submit-by-requirementId **public** would allow the link to work without login (the requirementId in the URL acts as the secret token).

---

## Summary table

| Actor           | Entry                     | Auth        | Validation              | Submit endpoint                    |
|----------------|---------------------------|------------|--------------------------|------------------------------------|
| Beneficiary    | /beneficiary-evaluation   | None       | 5-digit PIN + event      | POST /api/evaluation/beneficiary   |
| Volunteer      | /evaluation/:id (email)   | None (link is token) | GET /api/evaluation/validity/:id | POST /api/evaluation/:id |

Both validity and submit are public so the email link works without login.
