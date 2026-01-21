# Email System Debugging Guide

This guide will help you debug why emails aren't being sent during signup and approval.

## Quick Checklist

### ✅ Step 1: Verify Email Configuration

**Check if email is configured:**

```bash
# Test endpoint (replace with your backend URL)
curl https://your-backend.onrender.com/api/auth/test-email?email=your-test-email@gmail.com
```

**Expected Response (Success):**
```json
{
  "success": true,
  "configured": true,
  "provider": "Resend",
  "message": "Email configuration is valid and test email sent to your-test-email@gmail.com",
  "test_email_sent": true
}
```

**If you get an error:**
- `"configured": false` → Email not configured (see Step 2)
- `"provider": "SMTP"` → Using SMTP (may not work on Render free tier)
- `"test_email_sent": false` → Configuration valid but email sending failed

---

### ✅ Step 2: Check Environment Variables

**Required for Resend (Recommended):**
```env
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
RESEND_FROM_EMAIL=onboarding@resend.dev  # or your verified email
```

**Required for SMTP (Fallback):**
```env
AUTOMAILER_EMAIL=your-email@gmail.com
AUTOMAILER_PASSW=your-app-password
```

**Check in Render Dashboard:**
1. Go to your **Backend Service** → **Environment** tab
2. Verify these variables exist and have correct values
3. Make sure `RESEND_API_KEY` starts with `re_`
4. Make sure `RESEND_FROM_EMAIL` is set (or use `onboarding@resend.dev` for testing)

---

### ✅ Step 3: Test Signup Email Flow

**1. Register a new user:**
```bash
POST /api/auth/register
{
  "username": "testuser",
  "email": "test@example.com",
  "fullname": "Test User",
  "password": "testpass123",
  # ... other required fields
}
```

**2. Check backend logs for:**
```
[AUTH_REGISTER] ✅ Registration successful
[EMAIL SUCCESS] Email sent via Resend to test@example.com
```

**3. If you see errors:**
```
[EMAIL ERROR] Email not configured...
[EMAIL ERROR] Failed to send email via Resend...
```

**Common Issues:**
- ❌ `Email not configured` → Set `RESEND_API_KEY` and `RESEND_FROM_EMAIL`
- ❌ `Failed to send email via Resend` → Check Resend dashboard for errors
- ❌ `Template file not found` → Check if `templates/application-under-review.html` exists

---

### ✅ Step 4: Test Approval Email Flow

**1. Approve a membership:**
```bash
PATCH /api/membership/approve/{membershipId}
```

**2. Check backend logs for:**
```
[MEMBERSHIP API] Approving membership ID: {id}
[EMAIL SUCCESS] Email sent via Resend to user@example.com
```

**3. If you see errors:**
```
[EMAIL ERROR] Failed to send email via Resend...
```

**Common Issues:**
- ❌ `FRONTEND_APP_URL` not set → Approval email needs this for login link
- ❌ Template file not found → Check if `templates/we-are-pleased-to-inform-membership.html` exists
- ❌ Email sending failed → Check Resend dashboard logs

---

### ✅ Step 5: Verify Templates Exist

**Check these files exist:**
```
templates/application-under-review.html          # Signup email
templates/we-are-pleased-to-inform-membership.html  # Approval email
```

**If missing, create them or check the file paths in:**
- `app/controllers/auth.py` (line 205) - Signup email
- `app/controllers/membership.py` (line 88) - Approval email

---

### ✅ Step 6: Check Resend Dashboard

**1. Go to https://resend.com/ → Logs**
2. Check for:
   - ✅ **Delivered** emails (green)
   - ⚠️ **Failed** emails (red) - click to see error
   - 📊 **Pending** emails (yellow)

**Common Resend Errors:**
- `Invalid API key` → Check `RESEND_API_KEY` format
- `Sender email not verified` → Use `onboarding@resend.dev` or verify domain
- `Rate limit exceeded` → Free tier: 3,000 emails/month
- `Invalid recipient` → Check email address format

---

### ✅ Step 7: Debug Code Flow

**Signup Email Flow:**
```
1. User registers → POST /api/auth/register
2. auth.register() creates member
3. sendPendingVerificationMail(memberDetails) called
4. Reads template: templates/application-under-review.html
5. Replaces [name], [application_type], [timeframe]
6. Calls threadedHtmlMailer(email, subject, html)
7. htmlMailer() checks isResendConfigured()
8. If Resend: resend.Emails.send()
9. If SMTP: SMTP.sendmail()
```

**Approval Email Flow:**
```
1. Officer approves → PATCH /api/membership/approve/{id}
2. membership.approveMembership(id) updates member
3. sendAcceptMembershipMail(memberDetails) called
4. Reads template: templates/we-are-pleased-to-inform-membership.html
5. Replaces [name], [link] (needs FRONTEND_APP_URL)
6. Calls threadedHtmlMailer(email, subject, html)
7. htmlMailer() checks isResendConfigured()
8. If Resend: resend.Emails.send()
9. If SMTP: SMTP.sendmail()
```

---

## Common Problems & Solutions

### Problem 1: No emails sent at all

**Symptoms:**
- No `[EMAIL SUCCESS]` or `[EMAIL ERROR]` in logs
- User registered but no email received

**Solutions:**
1. Check if `threadedHtmlMailer()` is being called (check logs)
2. Verify email configuration: `GET /api/auth/test-email`
3. Check if templates exist and are readable
4. Verify `isEmailConfigured()` returns `True`

---

### Problem 2: Signup email works, approval email doesn't

**Symptoms:**
- User receives "application under review" email
- User doesn't receive "approved" email

**Solutions:**
1. Check `FRONTEND_APP_URL` is set (needed for approval email)
2. Verify approval route is being called: `PATCH /api/membership/approve/{id}`
3. Check backend logs when approving - look for `[EMAIL ERROR]`
4. Verify `templates/we-are-pleased-to-inform-membership.html` exists

---

### Problem 3: Approval email works, signup email doesn't

**Symptoms:**
- User receives "approved" email
- User doesn't receive "application under review" email

**Solutions:**
1. Check if `sendPendingVerificationMail()` is called in `auth.register()`
2. Verify `templates/application-under-review.html` exists
3. Check backend logs during registration - look for `[EMAIL ERROR]`
4. Verify email address is valid in registration request

---

### Problem 4: Emails sent but not received

**Symptoms:**
- Logs show `[EMAIL SUCCESS]`
- User doesn't receive email

**Solutions:**
1. Check **Resend Dashboard → Logs** for delivery status
2. Check spam/junk folder
3. Verify recipient email is correct
4. Check if email domain is blocked
5. Verify Resend account hasn't exceeded free tier limit (3,000/month)

---

### Problem 5: SMTP errors on Render

**Symptoms:**
```
[EMAIL ERROR] Failed to send email via SMTP: [Errno 111] Connection refused
```

**Solutions:**
1. **Use Resend instead** (recommended for Render free tier)
2. Set `RESEND_API_KEY` and `RESEND_FROM_EMAIL` in Render environment
3. Render blocks SMTP ports (25, 465, 587) on free tier
4. Resend uses HTTP API, so it works on Render free tier

---

## Testing Commands

### Test Email Configuration
```bash
curl https://your-backend.onrender.com/api/auth/test-email?email=your-email@gmail.com
```

### Test Signup Email (via registration)
```bash
curl -X POST https://your-backend.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "fullname": "Test User",
    "password": "testpass123",
    "applyingAs": "student",
    "srcode": "TEST123",
    "age": 20,
    "sex": "male",
    "campus": "Main",
    "collegeDept": "CS",
    "yrlevelprogram": "BS CS 3",
    "address": "Test Address",
    "contactNum": "1234567890",
    "birthday": "2000-01-01",
    "volunterismExperience": "none",
    "weekdaysTimeDevotion": "2-4 hours",
    "weekendsTimeDevotion": "4-6 hours",
    "paymentOption": "cash",
    "bloodType": "O+",
    "bloodDonation": false
  }'
```

### Test Approval Email (via approval)
```bash
curl -X PATCH https://your-backend.onrender.com/api/membership/approve/{membershipId} \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Debugging Checklist

- [ ] Email configuration test passes (`/api/auth/test-email`)
- [ ] `RESEND_API_KEY` is set and starts with `re_`
- [ ] `RESEND_FROM_EMAIL` is set (or `AUTOMAILER_EMAIL` for SMTP)
- [ ] `FRONTEND_APP_URL` is set (needed for approval email)
- [ ] Template files exist in `templates/` directory
- [ ] Backend logs show `[EMAIL SUCCESS]` or `[EMAIL ERROR]`
- [ ] Resend dashboard shows email activity
- [ ] No rate limit errors in Resend dashboard
- [ ] Email addresses are valid and not blocked
- [ ] Check spam/junk folder

---

## Next Steps

1. **Run the email test endpoint** to verify configuration
2. **Check backend logs** during signup and approval
3. **Check Resend dashboard** for email delivery status
4. **Verify environment variables** are set correctly
5. **Test with a real email address** you can access

If all checks pass but emails still don't work, check:
- Resend account status (not suspended)
- Email domain verification (if using custom domain)
- Rate limits (3,000 emails/month on free tier)
- Backend server logs for detailed error messages

