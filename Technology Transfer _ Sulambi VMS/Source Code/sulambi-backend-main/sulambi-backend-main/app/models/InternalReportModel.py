from .Model import Model
from ..database import connection

class InternalReportModel(Model):
  def __init__(self):
    super().__init__()
    self.table = "internalReport"
    self.primaryKey = "id"
    self.columns = [
      "eventId",
      "narrative",
      "approvedBudget",
      "approvedBudgetSrc",
      "budgetUtilized",
      "budgetUtilizedSrc",
      "psAttribution",
      "psAttributionSrc",
      "photos",
      "photoCaptions",
      "signatoriesId"
    ]

  def get_event_ids_with_reports(self):
    """Return set of event IDs that have at least one report. One query instead of N."""
    conn, cursor = connection.cursorInstance()
    table = self._get_table_name()
    col = self._normalize_column_name("eventId")
    query = f'SELECT DISTINCT {col} FROM {table}'
    cursor.execute(query)
    ids = set(row[0] for row in cursor.fetchall())
    conn.close()
    return ids

  def create(self, eventId: int, narrative: str, approvedBudget: int | str, approvedBudgetSrc: str, budgetUtilized: int | str, budgetUtilizedSrc: str, psAttribution: int | str, psAttributionSrc: str, photos, photoCaptions: str, signatoriesId: int | None=None):
    return super().create((
      eventId, narrative, approvedBudget, approvedBudgetSrc, budgetUtilized, budgetUtilizedSrc, psAttribution, psAttributionSrc, photos, photoCaptions, signatoriesId
    ))