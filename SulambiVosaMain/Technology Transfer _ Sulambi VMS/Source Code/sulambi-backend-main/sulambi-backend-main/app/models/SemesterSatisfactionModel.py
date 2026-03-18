from .Model import Model
from datetime import datetime
from typing import Optional


class SemesterSatisfactionModel(Model):
  def __init__(self):
    super().__init__()
    self.table = "semester_satisfaction"
    self.primaryKey = "id"
    self.createdAtCol = ""
    self.columns = [
      "year",
      "semester",
      "overall",
      "volunteers",
      "beneficiaries",
      "totalEvaluations",
      "eventIds",
      "topIssues",
      "updatedAt",
    ]

  def create(
      self,
      year: int,
      semester: int,
      overall: float,
      volunteers: float,
      beneficiaries: float,
      totalEvaluations: int,
      eventIds: str,
      topIssues: str,
      updatedAt: Optional[str] = None,
  ):
    if updatedAt is None:
      updatedAt = datetime.now().replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
    return super().create((
      year,
      semester,
      overall,
      volunteers,
      beneficiaries,
      totalEvaluations,
      eventIds,
      topIssues,
      updatedAt,
    ))














