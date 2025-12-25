from ..database import connection
from .Model import Model
import uuid

class SessionModel(Model):
  def __init__(self):
    super().__init__()
    self.table = "sessions"
    self.primaryKey = "id"
    self.columns = ["token", "userid", "accountType"]

  # overwrite search by token
  def get(self, token: str) -> dict | None:
    matches = super().getOrSearch([self.primaryKey] + self.columns, [None, token, None, None])
    if (len(matches)== 0):
      return None
    return matches[0]

  # overwrite last row retrieval
  def getLastPrimaryKey(self):
    return super().getLastPrimaryKey("token")

  # generates new token for logged in
  def create(self, userid: int, accountType: str):
    return super().create((str(uuid.uuid4()), userid, accountType))

  # clears all user token
  def clearUserToken(self, userId):
    conn, cursor = connection.cursorInstance()
    cursor.execute(f"DELETE FROM {self.table} WHERE userid=?", (userId,))
    conn.close()