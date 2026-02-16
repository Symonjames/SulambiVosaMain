from ..models.AccountModel import AccountModel
from ..models.MembershipModel import MembershipModel
from ..models.SessionModel import SessionModel
from ..modules.Mailer import threadedHtmlMailer, isEmailConfigured, validateEmailConfig, htmlMailer
from ..config.cors_and_cookies import (
  is_production_cross_origin,
  cookie_attrs_cross_origin,
  cookie_attrs_same_site,
)
from flask import request, make_response, jsonify
import traceback
import os

# Cookie name for httpOnly auth token (not readable by JS)
SESSION_COOKIE_NAME = "session_token"
SESSION_COOKIE_MAX_AGE = 7 * 24 * 3600  # 7 days


def _is_secure_for_cookie():
  """True if we should set Secure (required for SameSite=None on cross-origin)."""
  if request.is_secure:
    return True
  proto = request.headers.get("X-Forwarded-Proto") or request.headers.get("x-forwarded-proto")
  if proto and str(proto).strip().lower() == "https":
    return True
  host = (request.host or "").lower()
  if "onrender.com" in host or "sulambi" in host or os.getenv("FORCE_SECURE_COOKIE") == "true":
    return True
  if os.getenv("FRONTEND_URL"):
    return True
  return False

AccountDb = AccountModel()
MembershipDb = MembershipModel()
SessionDb = SessionModel()

def login():
  try:
    print("[AUTH_LOGIN] ========================================")
    print("[AUTH_LOGIN] Login request received")
    
    # Check if request has JSON
    if not request.json:
      print("[AUTH_LOGIN] ❌ ERROR: No JSON data in request")
      return ({ "message": "No data provided" }, 400)
    
    username = request.json.get('username')
    password = request.json.get('password')
    
    print(f"[AUTH_LOGIN] Username: {username}")
    print(f"[AUTH_LOGIN] Password: {'*' * len(password) if password else 'None'}")
    
    if not username or not password:
      print("[AUTH_LOGIN] ❌ ERROR: Missing username or password")
      return ({ "message": "Username and password are required" }, 400)
    
    print("[AUTH_LOGIN] Attempting authentication...")
    sessionDetails = AccountDb.authenticate(username, password)
    
    if (sessionDetails == None):
      print("[AUTH_LOGIN] ❌ Authentication failed - Invalid credentials")
      print("[AUTH_LOGIN] ========================================")
      return ({ "message": "Invalid Credentials" }, 403)
    
    print(f"[AUTH_LOGIN] ✅ Authentication successful!")
    print(f"[AUTH_LOGIN] Account Type: {sessionDetails.get('accountType')}")
    print(f"[AUTH_LOGIN] User ID: {sessionDetails.get('userid')}")
    print(f"[AUTH_LOGIN] Token: {sessionDetails.get('token')[:20]}..." if sessionDetails.get('token') else "No token")
    print("[AUTH_LOGIN] ========================================")

    membershipData = None
    if (sessionDetails["accountType"] == "member"):
      print("[AUTH_LOGIN] Fetching member data...")
      accountData = AccountDb.get(sessionDetails["userid"])
      membershipData = MembershipDb.get(accountData["membershipId"])
      print(f"[AUTH_LOGIN] Member data retrieved: {membershipData is not None}")

    payload = {
      "message": "Successfully logged in",
      "session": sessionDetails,
      "memberData": membershipData
    }
    resp = make_response(jsonify(payload))
    is_secure = _is_secure_for_cookie()
    token_val = sessionDetails.get("token", "")
    # Local dev (localhost): always Lax so cookie works over HTTP
    is_local = (request.host or "").lower().startswith("localhost") or "127.0.0.1" in (request.host or "")
    # COOKIE_DOMAIN (e.g. .sulambi-vosa.com): same-site cookie, Lax is enough
    cookie_domain = os.getenv("COOKIE_DOMAIN", "").strip()
    if cookie_domain and cookie_domain.startswith("."):
      attrs = cookie_attrs_same_site(is_secure)
      resp.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token_val,
        domain=cookie_domain,
        **attrs,
      )
      print(f"[AUTH_LOGIN] ✅ Login successful, session_token (Domain={cookie_domain}, SameSite=Lax)")
    elif (is_production_cross_origin() or is_secure) and not is_local:
      # Cross-origin (www.sulambi-vosa.com → Render): SameSite=None; Secure so browser sends cookie
      attrs = cookie_attrs_cross_origin()
      resp.set_cookie(key=SESSION_COOKIE_NAME, value=token_val, **attrs)
      print("[AUTH_LOGIN] ✅ Login successful, session_token (SameSite=None; Secure)")
    else:
      attrs = cookie_attrs_same_site(is_secure)
      resp.set_cookie(key=SESSION_COOKIE_NAME, value=token_val, **attrs)
      print("[AUTH_LOGIN] ✅ Login successful, session_token (SameSite=Lax)")
    return resp
    
  except KeyError as e:
    print(f"[AUTH_LOGIN] ❌ ERROR: Missing key in request: {e}")
    print(f"[AUTH_LOGIN] Traceback: {traceback.format_exc()}")
    return ({ "message": f"Missing required field: {str(e)}" }, 400)
  except Exception as e:
    print(f"[AUTH_LOGIN] ❌ ERROR: Unexpected error: {str(e)}")
    print(f"[AUTH_LOGIN] Traceback: {traceback.format_exc()}")
    return ({ "message": f"Server error: {str(e)}" }, 500)

def logout(usertoken=None):
  # Prefer token from httpOnly cookie (frontend does not send token in URL/body)
  token = usertoken or request.cookies.get(SESSION_COOKIE_NAME)
  if not token:
    resp = jsonify({ "message": "No session cookie (already logged out)" })
    _clear_session_cookie(resp)
    return resp
  matchedToken = SessionDb.get(token)
  if (matchedToken == None):
    resp = jsonify({ "message": "Token does not exist (cannot logout)" })
    _clear_session_cookie(resp)
    return resp
  SessionDb.delete(matchedToken["id"])
  resp = jsonify({ "message": "Successfully logged out token" })
  _clear_session_cookie(resp)
  return resp


def _clear_session_cookie(response):
  """Clear the session cookie on the response."""
  is_secure = _is_secure_for_cookie()
  cookie_domain = os.getenv("COOKIE_DOMAIN", "").strip()
  kwargs = dict(
    key=SESSION_COOKIE_NAME,
    value="",
    httponly=True,
    secure=is_secure,
    samesite="Lax" if cookie_domain else ("None" if is_secure else "Lax"),
    max_age=0,
    path="/",
  )
  if cookie_domain and cookie_domain.startswith("."):
    kwargs["domain"] = cookie_domain
  response.set_cookie(**kwargs)


def me():
  """Return current session info from httpOnly cookie. Used by frontend to restore accountDetails without storing token."""
  token = request.cookies.get(SESSION_COOKIE_NAME)
  if not token:
    return ({ "message": "Not authenticated" }, 403)
  sessionInfo = SessionDb.get(token)
  if sessionInfo is None:
    return ({ "message": "Session invalid or expired" }, 403)
  accountSessionInfo = AccountDb.get(sessionInfo.get("userid"))
  if accountSessionInfo is None:
    return ({ "message": "Account not found" }, 403)
  membershipData = None
  if accountSessionInfo.get("accountType") == "member" and accountSessionInfo.get("membershipId"):
    membershipData = MembershipDb.get(accountSessionInfo["membershipId"])
  return {
    "message": "OK",
    "username": accountSessionInfo.get("username", ""),
    "accountType": accountSessionInfo.get("accountType", ""),
    "memberData": membershipData,
  }

def register():
  try:
    print("[AUTH_REGISTER] ========================================")
    print("[AUTH_REGISTER] Registration request received")
    
    # Check if request has JSON
    if not request.json:
      print("[AUTH_REGISTER] ❌ ERROR: No JSON data in request")
      return ({ "message": "No data provided" }, 400)
    
    print(f"[AUTH_REGISTER] Request keys: {list(request.json.keys())}")
    
    applyingAs = request.json.get("applyingAs")
    volunterismExperience = request.json.get("volunterismExperience")
    weekdaysTimeDevotion = request.json.get("weekdaysTimeDevotion")
    weekendsTimeDevotion = request.json.get("weekendsTimeDevotion")
    fullname = request.json.get("fullname")
    email = request.json.get("email")
    affiliation = request.json.get("affiliation")
    srcode = request.json.get("srcode")
    age = request.json.get("age")
    birthday = request.json.get("birthday")
    sex = request.json.get("sex")
    campus = request.json.get("campus")
    collegeDept = request.json.get("collegeDept")
    yrlevelprogram = request.json.get("yrlevelprogram")
    address = request.json.get("address")
    contactNum = request.json.get("contactNum")
    fblink = request.json.get("fblink")
    bloodType = request.json.get("bloodType")
    bloodDonation = request.json.get("bloodDonation")
    paymentOption = request.json.get("paymentOption")
    username = request.json.get("username")
    password = request.json.get("password")

    # optional fields
    medicalCondition = request.json.get("medicalCondition") or ""
    areasOfInterest = request.json.get("areasOfInterest") or ""
    volunteerExpQ1 = request.json.get("volunteerExpQ1") or ""
    volunteerExpQ2 = request.json.get("volunteerExpQ2") or ""
    volunteerExpProof = request.json.get("volunteerExpProof") or ""
    reasonQ1 = request.json.get("reasonQ1") or ""
    reasonQ2 = request.json.get("reasonQ2") or ""

    # check for existence of member
    memberMatch = MembershipDb.getOrSearch(["username", "email", "srcode"], [username, email, srcode])
    if (len(memberMatch) > 0):
      fieldError = []
      for member in memberMatch:
        if (member["username"] == username and fieldError.count("username") == 0):
          fieldError.append("username")
        if (member["email"] == email and fieldError.count("email") == 0):
          fieldError.append("email")
        if (member["srcode"] == srcode and fieldError.count("email") == 0):
          fieldError.append("srcode")

      return ({
        "message": "Membership for your account already exists",
        "fieldError": fieldError
      }, 400)

    # register membership for approval
    # Explicitly set accepted=None to ensure it's pending (NULL in database)
    createdMember = MembershipDb.create(
      address=address,
      age=age,
      applyingAs=applyingAs,
      areasOfInterest=areasOfInterest,
      birthday=birthday,
      bloodDonation=bloodDonation,
      bloodType=bloodType,
      campus=campus,
      collegeDept=collegeDept,
      contactNum=contactNum,
      email=email,
      affiliation=affiliation,
      fblink=fblink,
      fullname=fullname,
      medicalCondition=medicalCondition,
      password=password,
      paymentOption=paymentOption,
      reasonQ1=reasonQ1,
      reasonQ2=reasonQ2,
      sex=sex,
      srcode=srcode,
      username=username,
      volunterismExperience=volunterismExperience,
      volunteerExpQ1=volunteerExpQ1,
      volunteerExpQ2=volunteerExpQ2,
      weekdaysTimeDevotion=weekdaysTimeDevotion,
      weekendsTimeDevotion=weekendsTimeDevotion,
      yrlevelprogram=yrlevelprogram,
      volunteerExpProof=volunteerExpProof,
      accepted=None,  # Explicitly set to None for pending status
      active=True     # Set active to True by default
    )
    
    print(f"[AUTH_REGISTER] Member created with ID: {createdMember.get('id')}")
    print(f"[AUTH_REGISTER] Member accepted status: {createdMember.get('accepted')} (should be None for pending)")
    print(f"[AUTH_REGISTER] Member active status: {createdMember.get('active')}")

    # Send pending verification email
    sendPendingVerificationMail(createdMember)

    print("[AUTH_REGISTER] ✅ Registration successful, returning response")
    print("[AUTH_REGISTER] ========================================")
    
    return {
      "member": createdMember,
      "message": "Member successfully created"
    }
    
  except KeyError as e:
    print(f"[AUTH_REGISTER] ❌ ERROR: Missing key in request: {e}")
    print(f"[AUTH_REGISTER] Traceback: {traceback.format_exc()}")
    return ({ "message": f"Missing required field: {str(e)}" }, 400)
  except Exception as e:
    print(f"[AUTH_REGISTER] ❌ ERROR: Unexpected error: {str(e)}")
    print(f"[AUTH_REGISTER] Traceback: {traceback.format_exc()}")
    return ({ "message": f"Server error: {str(e)}" }, 500)

######################
#  Helper Functions  #
######################
def sendPendingVerificationMail(memberDetails):
  """Send email notification to user that their application is under review"""
  try:
    print(f"[EMAIL] Sending pending verification email to {memberDetails.get('email')}")
    templateHtml = open("templates/application-under-review.html", "r").read()
    templateHtml = templateHtml.replace("[name]", memberDetails.get("fullname").split(" ")[0])
    templateHtml = templateHtml.replace("[application_type]", "membership")
    templateHtml = templateHtml.replace("[timeframe]", "3-5 business days")

    threadedHtmlMailer(
      mailTo=memberDetails.get("email"),
      htmlRendered=templateHtml,
      subject="Application Received - Pending Officer Verification | Sulambi VOSA"
    )
    print(f"[EMAIL] Pending verification email queued for {memberDetails.get('email')}")
  except FileNotFoundError as e:
    print(f"[EMAIL ERROR] Template file not found: {e}")
    print(f"[EMAIL ERROR] Cannot send pending verification email to {memberDetails.get('email')}")
  except Exception as e:
    print(f"[EMAIL ERROR] Failed to send pending verification email: {str(e)}")
    import traceback
    traceback.print_exc()

def checkApplicationStatus():
  """Check membership application status by email"""
  email = request.json.get("email")
  
  if not email:
    return ({"message": "Email is required"}, 400)
  
  # Search for membership by email
  memberMatch = MembershipDb.getOrSearch(["email"], [email])
  
  if len(memberMatch) == 0:
    return ({"message": "No application found with this email address"}, 404)
  
  member = memberMatch[0]
  
  # Determine status
  status = "pending"
  if member["accepted"] is True:
    status = "approved"
  elif member["accepted"] is False:
    status = "rejected"
  
  return {
    "message": "Application status retrieved successfully",
    "data": {
      "fullname": member["fullname"],
      "email": member["email"],
      "srcode": member["srcode"],
      "status": status,
      "applyingAs": member["applyingAs"],
      "campus": member["campus"],
      "collegeDept": member["collegeDept"],
      "submittedDate": member.get("created_at", "Unknown")
    }
  }

def testEmail():
  """Test email system configuration and send a test email"""
  from flask import request
  
  try:
    # Check email configuration
    is_configured = isEmailConfigured()
    
    if not is_configured:
      return {
        "success": False,
        "configured": False,
        "message": "Email not configured. AUTOMAILER_EMAIL and AUTOMAILER_PASSW must be set.",
        "smtp_test": None
      }
    
    # Test SMTP connection (with timeout protection)
    try:
      validation = validateEmailConfig()
    except Exception as e:
      # If validation itself throws an exception, catch it
      validation = {
        "configured": False,
        "message": f"Email validation error: {str(e)}"
      }
    
    # Get test email from query parameter or use the configured email
    test_email = request.args.get('email', None)
    
    result = {
      "success": True,
      "configured": True,
      "smtp_test": validation,
      "provider": validation.get("provider", "Unknown"),
      "message": validation.get("message", "Email configuration check completed")
    }
    
    # If test email provided, try to send
    if test_email:
      test_html = """
      <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
          <h2 style="color: #c07f00;">Test Email from Sulambi VOSA</h2>
          <p>This is a test email to verify the email system is working correctly in deployment.</p>
          <p>If you received this email, the email system is configured and functioning properly!</p>
          <hr style="margin: 20px 0;">
          <p style="color: #666; font-size: 12px;">Sent from Sulambi VOSA System - Deployment Test</p>
        </body>
      </html>
      """
      
      email_sent = htmlMailer(test_email, "Test Email - Sulambi VOSA Email System", test_html)
      
      result["test_email_sent"] = email_sent
      result["test_email_address"] = test_email
      if email_sent:
        result["message"] = f"Email configuration is valid and test email sent to {test_email}"
      else:
        result["message"] = f"Email configuration check passed but failed to send test email to {test_email}"
    
    return result
    
  except Exception as e:
    import traceback
    traceback.print_exc()
    return {
      "success": False,
      "configured": False,
      "message": f"Error testing email system: {str(e)}",
      "smtp_test": None
    }