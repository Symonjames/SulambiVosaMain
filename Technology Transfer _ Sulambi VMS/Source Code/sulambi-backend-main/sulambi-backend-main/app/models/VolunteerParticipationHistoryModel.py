from .Model import Model

class VolunteerParticipationHistoryModel(Model):
  def __init__(self):
    super().__init__()
    self.table = "volunteerParticipationHistory"
    self.primaryKey = "id"
    self.columns = [
      "volunteerEmail",
      "volunteerName",
      "membershipId",
      "semester",
      "semesterYear",
      "semesterNumber",
      "eventsJoined",
      "eventsAttended",
      "eventsDropped",
      "attendanceRate",
      "firstEventDate",
      "lastEventDate",
      "daysActiveInSemester",
      "participationConsistency",
      "engagementLevel",
      "calculatedAt",
      "lastUpdated",
    ]

















