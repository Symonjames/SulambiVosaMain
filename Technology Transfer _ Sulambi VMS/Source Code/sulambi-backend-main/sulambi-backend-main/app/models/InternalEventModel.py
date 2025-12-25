from .Model import Model
from datetime import datetime

class InternalEventModel(Model):
  def __init__(self):
    super().__init__()

    self.table = "internalEvents"
    self.primaryKey = "id"
    self.createdAtCol = "createdAt"
    self.columns = [
      "title",
      "durationStart",
      "durationEnd",
      "venue",
      "modeOfDelivery",
      "projectTeam",
      "partner",
      "participant",
      "maleTotal",
      "femaleTotal",
      "rationale",
      "objectives",
      "description",
      "workPlan",
      "financialRequirement",
      "evaluationMechanicsPlan",
      "sustainabilityPlan",
      "createdBy",
      "status",
      "toPublic",
      "evaluationSendTime",
      "signatoriesId",
      "createdAt",
      "feedback_id",
      "eventProposalType"
    ]

  def create(self,
    title: str,
    durationStart: int,
    durationEnd: int,
    venue: str,
    modeOfDelivery: str,
    projectTeam: str,
    partner: str,
    participant: str,
    maleTotal: str,
    femaleTotal: str,
    rationale: str,
    objectives: str,
    description: str,
    workPlan: str,
    financialRequirement: str,
    evaluationMechanicsPlan: str,
    sustainabilityPlan: str,
    createdBy: int,
    status: str,
    toPublic: bool,
    evaluationSendTime: int,
    signatoriesId: int | None = None,
    createdAt: datetime=datetime.now().replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S"),
    feedback_id: int | None = None,
    eventProposalType: str = "[]"):

    return super().create((
      title, durationStart, durationEnd, venue,
      modeOfDelivery, projectTeam,
      partner, participant, maleTotal,
      femaleTotal, rationale, objectives,
      description, workPlan, financialRequirement,
      evaluationMechanicsPlan, sustainabilityPlan,
      createdBy, status, toPublic, evaluationSendTime,
      signatoriesId, createdAt,
      feedback_id, eventProposalType
    ))
