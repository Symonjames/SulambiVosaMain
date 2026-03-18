from .Model import Model
from .ExternalEventModel import ExternalEventModel
from .InternalEventModel import InternalEventModel
from ..modules.Mailer import htmlMailer, threadedHtmlMailer
import os

OFFICER_NOTIF_EMAIL = os.getenv("SULAMBI_OFFICER_MAIL")

class FeedbackModel(Model):
    def __init__(self):
        super().__init__()
        self.primaryKey = "id"
        self.table = "feedback"
        self.columns = [
            "message",
            "state",
        ]


    def create(self,
            message: str,
            state: str):

        return super().create((
            message,
            state,
        ))

    def getFeedbackForEvent(self, eventId: int, eventType: str) -> dict:
        print(eventId, eventType)

        event = None
        if eventType == "external":
            event = ExternalEventModel().get(eventId)
        elif eventType == "internal":
            event = InternalEventModel().get(eventId)

        if event is None:
            return ({ "message": "Event not found" }, 404)

        feedbackId = event["feedback_id"]
        if feedbackId is None:
            return ({ "message": "No Feedback for event found" }, 404)

        return super().get(feedbackId)


    def createFeedbackForEvent(self, eventId: int, eventType: str, message: str, status: str) -> dict:
        createdFeedback = self.create(message, status)

        if eventType == "external":
            event = ExternalEventModel().get(eventId)
            if (event is not None and event.get("feedback_id") is not None):
                return None

            ExternalEventModel().updateSpecific(eventId, ["feedback_id"], (createdFeedback["id"], ))
            threadedHtmlMailer(
                mailTo=OFFICER_NOTIF_EMAIL,
                subject=f"Feedback Submitted to {event.get('title')}",
                htmlRendered="<p>Good day!</p><br/><p>A Feedback was submitted to your proposed event, kindly check the feedback on your event proposal</p><p>Thank you!</p>"
            )

        elif eventType == "internal":
            event = InternalEventModel().get(eventId)
            if (event is not None and event.get("feedback_id") is not None):
                return None

            InternalEventModel().updateSpecific(eventId, ["feedback_id"], (createdFeedback["id"], ))
            threadedHtmlMailer(
                mailTo=OFFICER_NOTIF_EMAIL,
                subject=f"Feedback Submitted to {event.get('title')}",
                htmlRendered="<p>Good day!</p><br/><p>A Feedback was submitted to your proposed event, kindly check the feedback on your event proposal</p><p>Thank you!</p>"
            )

        return createdFeedback
