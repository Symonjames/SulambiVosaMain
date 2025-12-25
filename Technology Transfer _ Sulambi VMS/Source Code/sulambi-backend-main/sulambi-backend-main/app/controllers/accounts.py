from ..models.AccountModel import AccountModel
from flask import request

AccountDb = AccountModel()

def createAccount(accountType):
  matched = AccountDb.getOrSearch(["username"], [
    request.json["username"]
  ])

  if (len(matched) > 0):
    return ({ "message": "Account already exists" }, 403)

  createdAccount = AccountDb.create(
    request.json["username"],
    request.json["password"],
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

  AccountDb.updateSpecific(accountId, ["username", "password"], (
    request.json["username"],
    request.json["password"]
  ))

  return {
    "message": "Successfully updated account",
    "data": AccountDb.get(accountId)
  }