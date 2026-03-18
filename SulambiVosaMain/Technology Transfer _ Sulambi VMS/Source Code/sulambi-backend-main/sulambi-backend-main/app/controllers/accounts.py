from ..models.AccountModel import AccountModel
from flask import request

AccountDb = AccountModel()

def createAccount(accountType):
  username = (request.json.get("username") or "").strip()
  password = (request.json.get("password") or "").strip()
  if not username or not password:
    return ({ "message": "Username and password are required" }, 400)

  matched = AccountDb.getOrSearch(["username"], [
    username
  ])

  if (len(matched) > 0):
    return ({ "message": "Account already exists" }, 403)

  createdAccount = AccountDb.create(
    username,
    password,
    accountType
  )

  return {
    "message": "Account Successfully created",
    "data": createdAccount
  }

def getAccounts(accountType):
  if (accountType == "admin" or accountType == "officer"):
    return {
      "data": AccountDb.getOrSearch(
        ["accountType", "id", "username", "password", "membershipId"],
        [accountType, None, None, None, None]),
      "message": "Successfully retrieved accounts"
    }

  return {
    "data": AccountDb.getAll(),
    "message": "Successfully retrieved accounts"
  }

def deleteAccount(accountId):
  matchedAccount = AccountDb.get(accountId)
  if (matchedAccount == None):
    return ({ "message": "Account id specified does not exist" }, 404)

  AccountDb.delete(accountId)
  return {
    "message": "Successfully deleted account",
    "data": matchedAccount
  }

def updateAccount(accountId):
  matchedAccount = AccountDb.get(accountId)
  if (matchedAccount == None):
    return ({ "message": "Account id specified does not exist" }, 404)

  username = (request.json.get("username") or "").strip()
  password = (request.json.get("password") or "").strip()
  if not username or not password:
    return ({ "message": "Username and password are required" }, 400)

  AccountDb.updateSpecific(accountId, ["username", "password"], (
    username,
    password
  ))

  return {
    "message": "Successfully updated account",
    "data": AccountDb.get(accountId)
  }