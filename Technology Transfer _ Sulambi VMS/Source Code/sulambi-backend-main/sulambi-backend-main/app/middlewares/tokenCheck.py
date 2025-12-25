from flask import request, g
from ..models.AccountModel import AccountModel
from ..models.SessionModel import SessionModel

AccountDb = AccountModel()
SessionDb = SessionModel()

def authCheckMiddleware(accountType=[]):

  userToken = request.headers.get("authorization") or ""
  userToken = userToken.replace("Bearer ", "")

  # unassigned bearer token
  if (userToken == ""): return ({
    "message": "Unauthorized action"
  }, 403)

  # expired/invalid token
  sessionInfo = SessionDb.get(userToken)
  if (sessionInfo == None): return ({
      "message": "Token invalid"
    }, 403)

  # account type permssion checking
  accountSessionInfo = AccountDb.get(sessionInfo.get("userid"))
  if (accountSessionInfo == None):
    return ({ "message": "Session expired" }, 403)
  if (len(accountType) > 0 and accountSessionInfo["accountType"] not in accountType):
    return ({
      "message": "User not permitted for action"
    }, 403)

  g.setdefault("accountSessionInfo", accountSessionInfo)