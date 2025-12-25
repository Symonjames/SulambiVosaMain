from flask import Blueprint
from ..controllers import membership
from ..middlewares import tokenCheck

MembershipBlueprint = Blueprint('membership', __name__, url_prefix="/membership")

@MembershipBlueprint.get("/")
def getAllMembershipRoute():
  return membership.getAllMembership()

@MembershipBlueprint.patch("/approve/<membershipRequestId>")
def approveMembership(membershipRequestId):
  return membership.approveMembership(membershipRequestId)

@MembershipBlueprint.patch("/reject/<membershipRequestId>")
def rejectMembership(membershipRequestId):
  return membership.rejectMembership(membershipRequestId)

@MembershipBlueprint.patch("/activate/<membershipRequestId>")
def activateMembership(membershipRequestId):
  return membership.activateMembership(membershipRequestId)

@MembershipBlueprint.patch("/deactivate/<membershipRequestId>")
def deactivateMembership(membershipRequestId):
  return membership.deactivateMembership(membershipRequestId)
