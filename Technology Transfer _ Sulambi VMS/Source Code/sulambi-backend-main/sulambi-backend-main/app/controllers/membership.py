from ..models.MembershipModel import MembershipModel
from ..modules.Mailer import threadedHtmlMailer
from dotenv import load_dotenv
import os

load_dotenv()

MembershipDb = MembershipModel()
FRONTEND_APP_URL = os.getenv("FRONTEND_APP_URL")

def getAllMembership():
  all_members = MembershipDb.getAll()
  print(f"[MEMBERSHIP API] Total members retrieved: {len(all_members)}")
  
  # Count members by status for debugging
  pending_count = sum(1 for m in all_members if m.get('accepted') is None)
  approved_count = sum(1 for m in all_members if m.get('accepted') is True or m.get('accepted') == 1)
  rejected_count = sum(1 for m in all_members if m.get('accepted') is False or m.get('accepted') == 0)
  print(f"[MEMBERSHIP API] Status breakdown - Pending: {pending_count}, Approved: {approved_count}, Rejected: {rejected_count}")
  
  # Show sample of pending members for debugging
  pending_members = [m for m in all_members if m.get('accepted') is None]
  if pending_members:
    print(f"[MEMBERSHIP API] Found {len(pending_members)} pending members:")
    for member in pending_members[:5]:  # Show first 5
      print(f"  - ID: {member.get('id')}, Name: {member.get('fullname')}, Email: {member.get('email')}, accepted={member.get('accepted')} (type: {type(member.get('accepted')).__name__})")
  
  if len(all_members) > 0:
    print(f"[MEMBERSHIP API] Sample member: {all_members[0].get('fullname', 'N/A')}, accepted={all_members[0].get('accepted')} (type: {type(all_members[0].get('accepted')).__name__})")
    print(f"[MEMBERSHIP API] Sample member keys: {list(all_members[0].keys())[:10]}")
  
  # Ensure None values are properly serialized (Flask should handle this, but let's be explicit)
  # Convert None to None (which JSON serializes to null) - this should already happen, but let's ensure
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