from flask import Blueprint, request
from ..middlewares import tokenCheck
from ..middlewares.requiredParams import eventParams
from ..controllers import events
from ..controllers import signatories

EventsBlueprint = Blueprint('events', __name__, url_prefix="/events")

@EventsBlueprint.get("/")
def getAllEventsRoute():
  return events.getAll()

@EventsBlueprint.get("/signatories/<signatoriesId>")
def updateEventSignatories(signatoriesId):
  return signatories.getSignatoriesData(signatoriesId)

@EventsBlueprint.put("/signatories/<signatoriesId>")
def getEventSignatories(signatoriesId):
  return signatories.updateSignatories(signatoriesId)

@EventsBlueprint.get("/external/<id>")
def getOneExternalEvent(id):
  return events.getOne(id, "external")

@EventsBlueprint.get("/internal/<id>")
def getOneInternalEvent(id):
  return events.getOne(id, "internal")

@EventsBlueprint.get("/external/analyze/<id>")
def analyzeExternalEvaluationRoute(id):
  return events.getAnalysis(id, "external")

@EventsBlueprint.get("/internal/analyze/<id>")
def analyzeInternalEvaluationRoute(id):
  return events.getAnalysis(id, "internal")

@EventsBlueprint.get("/public")
def getAllPublicEventsRoute():
  return events.getPublicEvents()

###############################
#  EXTERNAL EVENT OPERATIONS  #
###############################
@EventsBlueprint.post("/external")
def createExternalEventRoute():
  return events.createExternalEvent()

@EventsBlueprint.patch("/external/submit/<id>")
def submitExternalEventRoute(id):
  return events.editExternalEventStatus(id, "submitted")

@EventsBlueprint.patch("/external/accept/<id>")
def acceptExternalEventRoute(id):
  return events.editExternalEventStatus(id, "accepted")

@EventsBlueprint.patch("/external/reject/<id>")
def rejectExternalEventRoute(id):
  return events.editExternalEventStatus(id, "rejected")

@EventsBlueprint.patch("/external/to-public/<id>")
def makeExternalEventPublic(id):
  return events.makeEventPublic(id, "external")

@EventsBlueprint.put("/external/<id>")
def updateExternalEvent(id):
  return events.updateEvent(id, "external")

###############################
#  INTERNAL EVENT OPERATIONS  #
###############################
@EventsBlueprint.post("/internal")
def createInternalEventRoute():
  return events.createInternalEvent()

@EventsBlueprint.patch("/internal/submit/<id>")
def submitInternalEventRoute(id):
  return events.editInternalEventStatus(id, "submitted")

@EventsBlueprint.patch("/internal/accept/<id>")
def acceptInternalEventRoute(id):
  return events.editInternalEventStatus(id, "accepted")

@EventsBlueprint.patch("/internal/reject/<id>")
def rejectInternalEventRoute(id):
  return events.editInternalEventStatus(id, "rejected")

@EventsBlueprint.patch("/internal/to-public/<id>")
def makeInternalEventPublic(id):
  return events.makeEventPublic(id, "internal")

@EventsBlueprint.put("/internal/<id>")
def updateInternalEvent(id):
  return events.updateEvent(id, "internal")

@EventsBlueprint.before_request
def eventsMiddleware():
  # skip checks for public routes here
  if (request.path in ["/api/events/public"]):
    pass

  elif (request.method != "OPTIONS"):
    # user authentication check
    userCheck = tokenCheck.authCheckMiddleware()
    if (userCheck != None):
      return userCheck

    # parameter parsing
    missingParams = None
    if (request.method not in ["GET", "DELETE", "PATCH"]):
      if (request.path == "/api/events/external" or (("/api/events/external" in request.path) and request.view_args.get("id"))):
        missingParams = eventParams.externalEventParamCheck()

      if (request.path == "/api/events/internal" or (("/api/events/internal" in request.path) and request.view_args.get("id"))):
        missingParams = eventParams.internalEventParamCheck()

      if (missingParams != None):
        return missingParams