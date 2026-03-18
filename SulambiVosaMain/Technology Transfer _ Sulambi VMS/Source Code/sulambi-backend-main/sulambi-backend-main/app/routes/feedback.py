from flask import Blueprint, request
from ..controllers import feedback

FeedbackBlueprint = Blueprint('feedback', __name__, url_prefix="/feedback")

@FeedbackBlueprint.get("/<eventType>/<eventId>")
def getFeedback(eventType: str, eventId: int):
    return feedback.getEventFeedback(eventType, eventId)

@FeedbackBlueprint.post("/<eventType>/<eventId>")
def createFeedback(eventType: str, eventId: int):
    if (eventType not in ["external", "internal"]):
        return ({ "message": "Invalid event type" }, 400)
    return feedback.createFeedback(eventType, eventId, request.json.get("feedback"))

@FeedbackBlueprint.put("/<feedbackId>")
def updateFeedback(feedbackId: int):
    userFeedback = request.json.get("feedback")
    return feedback.updateFeedback(feedbackId, userFeedback)
