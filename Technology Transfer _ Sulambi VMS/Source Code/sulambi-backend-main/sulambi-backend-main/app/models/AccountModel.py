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
    conn, cursor = connection.cursorInstance()
    cursor.execute(f"SELECT {','.join([self.primaryKey] + self.columns)} FROM {self.table} WHERE username=? AND password=? AND active=?", (username, password, True))
    parsed = self.parseResponse(cursor.fetchone())

    if (parsed == None):
      return None

    # clears current user's current token
    SessionDb = SessionModel()

    # provide users their newly created token
    session = SessionDb.create(parsed["id"], parsed["accountType"])
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