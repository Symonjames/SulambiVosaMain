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
    print(f"[AUTH_MODEL] Authenticating user: {username}")
    conn, cursor = connection.cursorInstance()
    
    table_name = self._get_table_name()
    # Convert boolean value for database compatibility
    from ..database.connection import convert_boolean_value
    active_value = convert_boolean_value(True)
    
    query = f"SELECT {','.join([self.primaryKey] + self.columns)} FROM {table_name} WHERE username=? AND password=? AND active=?"
    # Convert placeholders for PostgreSQL
    query = connection.convert_placeholders(query)
    # Convert boolean conditions for PostgreSQL
    query = connection.convert_boolean_condition(query)
    print(f"[AUTH_MODEL] Executing query: SELECT ... FROM {table_name} WHERE username=? AND password=? AND active=?")
    print(f"[AUTH_MODEL] Query parameters: username={username}, password={'*' * len(password)}, active={active_value}")
    
    cursor.execute(query, (username, password, active_value))
    result = cursor.fetchone()
    print(f"[AUTH_MODEL] Query result: {result is not None}")
    
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