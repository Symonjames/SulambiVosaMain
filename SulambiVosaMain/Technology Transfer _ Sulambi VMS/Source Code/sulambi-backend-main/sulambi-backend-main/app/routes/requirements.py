from flask import Blueprint, request
from ..controllers import requirements
from ..middlewares.requiredParams import requirementsParams

RequirementsBlueprint = Blueprint('requirements', __name__, url_prefix="/requirements")

# More specific routes first so /my is not matched by /<eventId>
@RequirementsBlueprint.get("/my")
def getMyRequirementsRoute():
  return requirements.getMyRequirements()

@RequirementsBlueprint.get("/")
def getAllRequirementsRoute():
  return requirements.getAllRequirements()

@RequirementsBlueprint.post("/<int:eventId>")
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
  # Auth + RBAC handled by global_api_auth; only param validation here
  if (request.method != "OPTIONS"):
    if (request.method not in ["GET", "DELETE", "PATCH"]):
      missingParams = None

      # create request
      if (request.method == "POST" and request.view_args.get("eventId") != None):
        missingParams = requirementsParams.requirementsParamCheck()

      if (missingParams != None):
        return missingParams