from .Model import Model

class SatisfactionSurveyModel(Model):
  def __init__(self):
    super().__init__()
    self.table = "satisfactionSurveys"
    self.primaryKey = "id"
    self.columns = [
      "eventId",
      "eventType",
      "requirementId",
      "respondentType",
      "respondentEmail",
      "respondentName",
      "overallSatisfaction",
      "volunteerRating",
      "beneficiaryRating",
      "organizationRating",
      "communicationRating",
      "venueRating",
      "materialsRating",
      "supportRating",
      "q13",
      "q14",
      "comment",
      "recommendations",
      "wouldRecommend",
      "areasForImprovement",
      "positiveAspects",
      "submittedAt",
      "finalized",
    ]

  def create(self,
    eventId: int,
    eventType: str,
    requirementId: str,
    respondentType: str,
    respondentEmail: str,
    respondentName: str,
    overallSatisfaction: float,
    volunteerRating: float = None,
    beneficiaryRating: float = None,
    organizationRating: float = None,
    communicationRating: float = None,
    venueRating: float = None,
    materialsRating: float = None,
    supportRating: float = None,
    q13: str = "",
    q14: str = "",
    comment: str = "",
    recommendations: str = "",
    wouldRecommend: bool = None,
    areasForImprovement: str = "",
    positiveAspects: str = "",
    submittedAt: int = None,
    finalized: bool = False):
      import time
      if submittedAt is None:
        submittedAt = int(time.time() * 1000)
      
      return super().create((
        eventId,
        eventType,
        requirementId,
        respondentType,
        respondentEmail,
        respondentName,
        overallSatisfaction,
        volunteerRating,
        beneficiaryRating,
        organizationRating,
        communicationRating,
        venueRating,
        materialsRating,
        supportRating,
        q13,
        q14,
        comment,
        recommendations,
        wouldRecommend,
        areasForImprovement,
        positiveAspects,
        submittedAt,
        finalized
      ))

















