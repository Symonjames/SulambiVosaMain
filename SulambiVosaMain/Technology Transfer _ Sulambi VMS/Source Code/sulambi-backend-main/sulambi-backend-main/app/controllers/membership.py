from ..models.MembershipModel import MembershipModel
from ..modules.Mailer import threadedHtmlMailer
from dotenv import load_dotenv
import os

load_dotenv()

MembershipDb = MembershipModel()
FRONTEND_APP_URL = os.getenv("FRONTEND_APP_URL")

BLOOD_DONATION_LABELS = {
  0: "I'm eligible to donate.",
  1: "I'm willing to donate.",
  2: "I'm willing but I am not aware if I'm eligible.",
  3: "I'm not willing.",
}

def _blood_donation_label(val):
  if val is None:
    return ""
  if isinstance(val, str) and val.strip() in ("0", "1", "2", "3"):
    return BLOOD_DONATION_LABELS.get(int(val), val)
  if isinstance(val, int):
    return BLOOD_DONATION_LABELS.get(val, str(val))
  return str(val) if val else ""

def getAllMembership():
  all_members = MembershipDb.getAll()
  print(f"[MEMBERSHIP API] Total members retrieved: {len(all_members)}")

  # Normalize accepted and active to 0/1/null so frontend works (PostgreSQL returns True/False)
  # Map numeric bloodDonation to human-readable label for display
  for m in all_members:
    v = m.get("accepted")
    if v is True or v == 1 or v == "1" or (isinstance(v, str) and v.strip().lower() in ("1", "true", "yes")):
      m["accepted"] = 1
    elif v is False or v == 0 or v == "0" or (isinstance(v, str) and v.strip().lower() in ("0", "false", "no")):
      m["accepted"] = 0
    else:
      m["accepted"] = None
    a = m.get("active")
    if a is True or a == 1 or a == "1" or (isinstance(a, str) and str(a).strip() == "1"):
      m["active"] = 1
    elif a is False or a == 0 or a == "0" or (isinstance(a, str) and str(a).strip() == "0"):
      m["active"] = 0
    else:
      m["active"] = 0
    m["bloodDonation"] = _blood_donation_label(m.get("bloodDonation"))

  return {
    "message": "Successfully retrieved membership data",
    "data": all_members
  }

def approveMembership(id):
  approvedMembership = MembershipDb.accept(id)
  if (approvedMembership == None):
    return ({"message": "Error occured in approving membership"}, 400)

  sendAcceptMembershipMail(approvedMembership)
  return {
    "message": "Membership request approved",
    "data": approvedMembership
  }

def rejectMembership(id):
  rejectedMembership = MembershipDb.reject(id)
  if (rejectedMembership == None):
    return ({"message": "Error occured in rejecting membership"}, 400)

  sendRejectMembershipMail(rejectedMembership)
  return {
    "message": "Membership request successfully rejected",
    "data": rejectedMembership
  }

def activateMembership(id):
  activated = MembershipDb.activate(id)
  if (activated == None):
    return ({"message": "Error occured in re-activating membership"}, 400)
  return { "message": "Successfully re-activated membership" }

def deactivateMembership(id):
  deactivated = MembershipDb.deactivate(id)
  if (deactivated == None):
    return ({"message": "Error occured in deactivating membership"}, 400)
  return { "message": "Successfully deactivated membership" }


######################
#  Helper Functions  #
######################
def sendRejectMembershipMail(memberDetails):
  templateHtml = open("templates/we-reject-to-inform-membership.html", "r").read()
  templateHtml = templateHtml.replace("[name]", memberDetails.get("fullname").split(" ")[0])

  threadedHtmlMailer(
    mailTo=memberDetails.get("email"),
    htmlRendered=templateHtml,
    subject="SULAMBI - VOSA Membership Application"
  )

def sendAcceptMembershipMail(memberDetails):
  try:
    print(f"[EMAIL] Sending approval email to {memberDetails.get('email')}")
    templateHtml = open("templates/we-are-pleased-to-inform-membership.html", "r").read()
    templateHtml = templateHtml.replace("[name]", memberDetails.get("fullname").split(" ")[0])
    # Use FRONTEND_APP_URL if set, otherwise use a placeholder
    login_link = (FRONTEND_APP_URL + "/login") if FRONTEND_APP_URL else "[Login URL - Please set FRONTEND_APP_URL environment variable]"
    templateHtml = templateHtml.replace("[link]", login_link)
    
    if not FRONTEND_APP_URL:
      print(f"[EMAIL WARNING] FRONTEND_APP_URL not set - approval email will have placeholder login link")

    threadedHtmlMailer(
      mailTo=memberDetails.get("email"),
      htmlRendered=templateHtml,
      subject="SULAMBI - VOSA Membership Application"
    )
    print(f"[EMAIL] Approval email queued for {memberDetails.get('email')}")
  except FileNotFoundError as e:
    print(f"[EMAIL ERROR] Template file not found: {e}")
    print(f"[EMAIL ERROR] Cannot send approval email to {memberDetails.get('email')}")
  except Exception as e:
    print(f"[EMAIL ERROR] Failed to send approval email: {str(e)}")
    import traceback
    traceback.print_exc()