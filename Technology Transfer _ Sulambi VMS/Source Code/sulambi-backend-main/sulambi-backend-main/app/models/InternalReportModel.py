import os

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
    self._pg_columns_cache = None

  def _is_pg(self) -> bool:
    return connection.is_postgresql_url(os.getenv("DATABASE_URL"))

  def _load_pg_columns(self):
    """Read live PostgreSQL column names to tolerate mixed-case legacy schemas."""
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
        WHERE table_schema = 'public' AND table_name = 'internalreport'
        """
      )
      self._pg_columns_cache = {row[0] for row in cursor.fetchall()}
      conn.close()
    except Exception:
      self._pg_columns_cache = set()
    return self._pg_columns_cache

  def _normalize_column_name(self, column_name):
    """
    PostgreSQL fallback:
    - use exact quoted camelCase if present
    - else use lowercase column if present
    - else default to exact quoted name
    """
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