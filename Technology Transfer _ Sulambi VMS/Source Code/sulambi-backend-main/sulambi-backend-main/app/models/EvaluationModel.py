from .Model import Model

class EvaluationModel(Model):
  def __init__(self):
    super().__init__()
    self.table = "evaluation"
    self.primaryKey = "id"
    self.columns = [
      "requirementId",
      "criteria",
      "q13",
      "q14",
      "comment",
      "recommendations",
      "finalized",
    ]

  def create(self,
    requirementId: int,
    criteria: str,
    q13: str, q14: str,
    comment: str,
    recommendations: str,
    finalized: bool):
      return super().create((
        requirementId,
        criteria,
        q13, q14,
        comment,
        recommendations,
        finalized
      ))