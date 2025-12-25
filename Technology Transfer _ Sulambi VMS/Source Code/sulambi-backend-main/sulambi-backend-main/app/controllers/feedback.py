from ..models.FeedbackModel import FeedbackModel

def createFeedback(eventType: str, eventId: int, feedback: str):
    createdFeedback = FeedbackModel().createFeedbackForEvent(
        eventType=eventType,
        eventId=eventId,
        message=feedback,
        status="editing"
    )

    if createdFeedback is None:
        return ({ "message": "Failed to create feedback due to existing feedback" }, 400)
    return { "data": createdFeedback, "message": "Feedback created successfully" }

def updateFeedback(feedbackId: int, feedback: str):
    FeedbackModel().updateSpecific(
        feedbackId, ['message'], (feedback, )
    )

    return FeedbackModel().get(feedbackId)

def deleteFeedback(feedbackId: int):
    return FeedbackModel().delete(feedbackId)

def getEventFeedback(eventType: str, eventId: int):
    return FeedbackModel().getFeedbackForEvent(eventId, eventType)