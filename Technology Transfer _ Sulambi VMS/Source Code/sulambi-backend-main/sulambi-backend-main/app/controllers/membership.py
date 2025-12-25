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
  if len(all_members) > 0:
    print(f"[MEMBERSHIP API] Sample member: {all_members[0].get('fullname', 'N/A')}")
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
  templateHtml = open("templates/we-are-pleased-to-inform-membership.html", "r").read()
  templateHtml = templateHtml.replace("[name]", memberDetails.get("fullname").split(" ")[0])
  templateHtml = templateHtml.replace("[link]", FRONTEND_APP_URL + "/login")

  threadedHtmlMailer(
    mailTo=memberDetails.get("email"),
    htmlRendered=templateHtml,
    subject="SULAMBI - VOSA Membership Application"
  )