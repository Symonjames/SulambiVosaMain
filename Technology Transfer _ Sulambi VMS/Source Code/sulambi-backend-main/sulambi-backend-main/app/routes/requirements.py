from flask import Blueprint, request
from ..middlewares import tokenCheck
from ..controllers import requirements
from ..middlewares.requiredParams import requirementsParams

RequirementsBlueprint = Blueprint('requirements', __name__, url_prefix="/requirements")

@RequirementsBlueprint.get("/")
def getAllRequirementsRoute():
  return requirements.getAllRequirements()

@RequirementsBlueprint.get("/my")
def getMyRequirementsRoute():
  return requirements.getMyRequirements()

@RequirementsBlueprint.post("/<eventId>")
def uploadRequirementsRoute(eventId):
  return requirements.createNewRequirement(eventId)

@RequirementsBlueprint.patch("/accept/<requirementId>")
def acceptRequirementsRoute(requirementId):
  # ID can be string (UUID or REQ-xxx) or int depending on requirements table
  return requirements.acceptRequirements(requirementId)

@RequirementsBlueprint.patch("/reject/<requirementId>")
def rejectRequirementsRoute(requirementId):
  return requirements.rejectRequirements(requirementId)

@RequirementsBlueprint.before_request
def requirementsMiddleware():
  if (request.method != "OPTIONS"):
    # GET /my is for members; other GET and PATCH require admin/officer
    if (request.method == "GET" and request.path.rstrip("/").endswith("/my")):
      userCheck = tokenCheck.authCheckMiddleware(["member", "admin", "officer"])
      if (userCheck != None):
        return userCheck
    elif (request.method in ["GET", "PATCH"]):
      userCheck = tokenCheck.authCheckMiddleware(["admin", "officer"])
      if (userCheck != None):
        return userCheck

    if (request.method not in ["GET", "DELETE", "PATCH"]):
      missingParams = None

      # create request
      if (request.method == "POST" and request.view_args.get("eventId") != None):
        missingParams = requirementsParams.requirementsParamCheck()

      if (missingParams != None):
        return missingParams