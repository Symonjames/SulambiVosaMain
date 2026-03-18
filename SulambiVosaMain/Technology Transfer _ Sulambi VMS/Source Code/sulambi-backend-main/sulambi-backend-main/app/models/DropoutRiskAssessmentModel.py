from .Model import Model

class DropoutRiskAssessmentModel(Model):
  def __init__(self):
    super().__init__()
    self.table = "dropoutRiskAssessment"
    self.primaryKey = "id"
    self.columns = [
      "membershipId",
      "volunteerEmail",
      "volunteerName",
      "totalEventsAttended",
      "eventsLastSemester",
      "eventsLastMonth",
      "averageEventsPerSemester",
      "lastEventDate",
      "daysSinceLastEvent",
      "longestInactivityPeriod",
      "riskScore",
      "riskLevel",
      "riskFactors",
      "engagementTrend",
      "participationRate",
      "retentionProbability",
      "semester",
      "calculatedAt",
      "isAtRisk",
      "interventionNeeded",
      "notes",
    ]

  def create(self,
    membershipId: int,
    volunteerEmail: str,
    volunteerName: str,
    totalEventsAttended: int = 0,
    eventsLastSemester: int = 0,
    eventsLastMonth: int = 0,
    averageEventsPerSemester: float = 0,
    lastEventDate: int = None,
    daysSinceLastEvent: int = 0,
    longestInactivityPeriod: int = 0,
    riskScore: int = 0,
    riskLevel: str = "Low",
    riskFactors: str = "",
    engagementTrend: str = "Stable",
    participationRate: float = 0,
    retentionProbability: float = 100,
    semester: str = "",
    calculatedAt: int = None,
    isAtRisk: bool = False,
    interventionNeeded: bool = False,
    notes: str = ""):
      import time
      if calculatedAt is None:
        calculatedAt = int(time.time() * 1000)
      
      return super().create((
        membershipId,
        volunteerEmail,
        volunteerName,
        totalEventsAttended,
        eventsLastSemester,
        eventsLastMonth,
        averageEventsPerSemester,
        lastEventDate,
        daysSinceLastEvent,
        longestInactivityPeriod,
        riskScore,
        riskLevel,
        riskFactors,
        engagementTrend,
        participationRate,
        retentionProbability,
        semester,
        calculatedAt,
        isAtRisk,
        interventionNeeded,
        notes,
      ))

















