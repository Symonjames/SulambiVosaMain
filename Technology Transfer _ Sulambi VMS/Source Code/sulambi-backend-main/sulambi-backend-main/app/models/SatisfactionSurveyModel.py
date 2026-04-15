import os

from .Model import Model
from ..database import connection

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
    self._pg_columns_cache = None

  def _is_pg(self) -> bool:
    return connection.is_postgresql_url(os.getenv("DATABASE_URL"))

  def _load_pg_columns(self):
    if self._pg_columns_cache is not None:
      return self._pg_columns_cache
    self._pg_columns_cache = set()
    if not self._is_pg():
      return self._pg_columns_cache
    try:
      conn, cursor = connection.cursorInstance()
      cursor.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND lower(table_name) = 'satisfactionsurveys'
        """
      )
      self._pg_columns_cache = {row[0] for row in cursor.fetchall()}
      conn.close()
    except Exception:
      self._pg_columns_cache = set()
    return self._pg_columns_cache

  def _normalize_column_name(self, column_name):
    if not self._is_pg():
      return column_name
    pg_columns = self._load_pg_columns()
    if column_name in pg_columns:
      return f'"{column_name}"'
    lower = column_name.lower()
    if lower in pg_columns:
      return lower
    return f'"{column_name}"'

  def _normalize_column_list(self, columns):
    if not self._is_pg():
      return columns
    return [self._normalize_column_name(col) for col in columns]

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

















