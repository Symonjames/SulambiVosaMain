from flask import Blueprint, request
from ..middlewares import tokenCheck
from ..controllers import requirements
from ..middlewares.requiredParams import requirementsParams

RequirementsBlueprint = Blueprint('requirements', __name__, url_prefix="/requirements")

@RequirementsBlueprint.get("/")
def getAllRequirementsRoute():
  return requirements.getAllRequirements()

@RequirementsBlueprint.post("/public-event/<int:eventId>/join")
def publicEventJoinRoute(eventId):
  return requirements.createPublicEventJoin(eventId)

@RequirementsBlueprint.post("/<eventId>")
def uploadRequirementsRoute(eventId):
  return requirements.createNewRequirement(eventId)

@RequirementsBlueprint.patch("/accept/<requirementId>")
def acceptRequirementsRoute(requirementId):
  return requirements.acceptRequirements(requirementId)

@RequirementsBlueprint.patch("/reject/<requirementId>")
def rejectRequirementsRoute(requirementId):
  return requirements.rejectRequirements(requirementId)

@RequirementsBlueprint.before_request
def requirementsMiddleware():
  if (request.method != "OPTIONS"):
    # Public join: no auth required (non-members joining a public event as temporary volunteers)
    if request.method == "POST" and "public-event" in request.path and "/join" in request.path:
      pass
    else:
      # Add authentication check for GET requests (viewing requirements)
      if (request.method == "GET"):
        userCheck = tokenCheck.authCheckMiddleware(["admin", "officer"])
        if (userCheck != None):
          return userCheck

      if (request.method not in ["GET", "DELETE", "PATCH"]):
        missingParams = None

        # create request (skip param check for public-event join; controller validates)
        if (request.method == "POST" and request.view_args.get("eventId") != None and "public-event" not in request.path):
          missingParams = requirementsParams.requirementsParamCheck()

        if (missingParams != None):
          return missingParams