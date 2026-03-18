from ..database import connection
from .SessionModel import SessionModel
from .Model import Model

class AccountModel(Model):
  def __init__(self):
    super().__init__()
    self.table = "accounts"
    self.primaryKey = "id"
    self.filteredColumns = ["password"]
    self.columns = ["username", "password", "accountType", "membershipId", "active"]

  def create(self, username: str, password: str, accountType: str, membershipId: int=None, active: bool=True):
    return super().create((username, password, accountType, membershipId, active))

  def updatePassword(self, id: int, password: str):
    return super().updateSpecific(id, ["password"], (password,))

  def authenticate(self, username: str, password: str):
    username = (username or "").strip()
    password = (password or "").strip()
    print(f"[AUTH_MODEL] Authenticating user: {username}")
    conn, cursor = connection.cursorInstance()
    
    table_name = self._get_table_name()
    
    # For PostgreSQL, use boolean literal in query; for SQLite use integer
    # psycopg2 handles Python True/False correctly, so we can use Python boolean
    # But we need to ensure the query uses proper boolean comparison
    from ..database.connection import DATABASE_URL
    from ..database.connection import is_postgresql_url
    is_postgresql = is_postgresql_url(DATABASE_URL)
    
    if is_postgresql:
      # PostgreSQL: use boolean True directly (psycopg2 handles it)
      active_value = True
    else:
      # SQLite: use integer 1
      active_value = 1
    
    columns_list = [self.primaryKey] + self.columns
    normalized_columns = self._normalize_column_list(columns_list)
    column_query = ",".join(normalized_columns)
    query = f"SELECT {column_query} FROM {table_name} WHERE username=? AND password=? AND active=?"
    # Convert placeholders for PostgreSQL
    query = connection.convert_placeholders(query)
    print(f"[AUTH_MODEL] Executing query: SELECT ... FROM {table_name} WHERE username=? AND password=? AND active=?")
    print(f"[AUTH_MODEL] Query: {query}")
    print(f"[AUTH_MODEL] Query parameters: username={username}, password={'*' * len(password)}, active={active_value} (type: {type(active_value).__name__})")
    
    cursor.execute(query, (username, password, active_value))
    result = cursor.fetchone()
    print(f"[AUTH_MODEL] Query result: {result is not None}")

    # Backward-compatibility fallback for rows accidentally saved with leading/trailing spaces.
    if result is None:
      trim_query = f"SELECT {column_query} FROM {table_name} WHERE TRIM(username)=? AND TRIM(password)=? AND active=?"
      trim_query = connection.convert_placeholders(trim_query)
      print(f"[AUTH_MODEL] Trying trimmed credential fallback query")
      cursor.execute(trim_query, (username, password, active_value))
      result = cursor.fetchone()
      print(f"[AUTH_MODEL] Trimmed fallback result: {result is not None}")
    
    parsed = self.parseResponse(result)

    if (parsed == None):
      print(f"[AUTH_MODEL] ❌ No matching account found or account is inactive")
      conn.close()
      return None

    print(f"[AUTH_MODEL] ✅ Account found: ID={parsed.get('id')}, Type={parsed.get('accountType')}")

    # clears current user's current token
    SessionDb = SessionModel()

    # provide users their newly created token
    print(f"[AUTH_MODEL] Creating session token...")
    session = SessionDb.create(parsed["id"], parsed["accountType"])
    print(f"[AUTH_MODEL] ✅ Session created: token={session.get('token')[:20] if session.get('token') else 'None'}...")
    conn.close()
    return session

  def deactivate(self, id: int):
    matchedAccount = super().get(id)
    if (matchedAccount == None):
      return None

    super().updateSpecific(id, ["active"], (False,))
    return matchedAccount

  def activate(self, id: int):
    matchedAccount = super().get(id)
    if (matchedAccount == None):
      return None

    super().updateSpecific(id, ["active"], (True,))
    return matchedAccount