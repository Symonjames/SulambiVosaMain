from flask import Blueprint, request
from ..middlewares import tokenCheck
from ..middlewares.requiredParams import accountsParams
from ..controllers import accounts

AccountsBlueprint = Blueprint('accounts', __name__, url_prefix="/accounts")

@AccountsBlueprint.get("/")
def getAllAccountsRoute():
  return accounts.getAccounts("")

@AccountsBlueprint.get("/admin")
def getAdminAccountsRoute():
  return accounts.getAccounts("admin")

@AccountsBlueprint.get("/officer")
def getOfficerAccountsRoute():
  return accounts.getAccounts("officer")

@AccountsBlueprint.delete("/<id>")
def deleteAccountRoute(id):
  return accounts.deleteAccount(id)

@AccountsBlueprint.put("/<id>")
def updateAccountRoute(id):
  return accounts.updateAccount(id)

@AccountsBlueprint.post("/admin")
def createAdminAcc():
  return accounts.createAccount("admin")

@AccountsBlueprint.post("/officer")
def createOfficerAcc():
  return accounts.createAccount("officer")

@AccountsBlueprint.before_request
def accountsMiddleware():
  if (request.method != "OPTIONS"):
    userCheck = tokenCheck.authCheckMiddleware(["admin", "officer"])
    if (userCheck != None):
      return userCheck

    missingParams = None
    if (request.method not in ["GET", "DELETE", "PATCH"]):
      if ("/api/accounts/" in request.path) or ("/api/accounts/" in request.path and request.view_args.get("id")):
        missingParams = accountsParams.accountUpdateParamCheck()

      if (missingParams != None):
        return missingParams
