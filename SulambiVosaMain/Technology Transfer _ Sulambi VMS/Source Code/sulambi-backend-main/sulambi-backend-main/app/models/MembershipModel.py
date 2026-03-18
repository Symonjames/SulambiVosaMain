from .Model import Model
from .AccountModel import AccountModel

class MembershipModel(Model):
  def __init__(self):
    super().__init__()

    self.table = "membership"
    self.primaryKey = "id"
    self.columns = [
      "applyingAs",
      "volunterismExperience",
      "weekdaysTimeDevotion",
      "weekendsTimeDevotion",
      "areasOfInterest",
      "fullname",
      "email",
      "affiliation",
      "srcode",
      "age",
      "birthday",
      "sex",
      "campus",
      "collegeDept",
      "yrlevelprogram",
      "address",
      "contactNum",
      "fblink",
      "bloodType",
      "bloodDonation",
      "medicalCondition",
      "paymentOption",
      "username",
      "password",
      "active",
      "accepted",
      "volunteerExpQ1",
      "volunteerExpQ2",
      "volunteerExpProof",
      "reasonQ1",
      "reasonQ2",
    ]

  def create(self, applyingAs: str, volunterismExperience: bool,
        weekdaysTimeDevotion: str, weekendsTimeDevotion: str, areasOfInterest: str,
        fullname: str, email: str, affiliation: str, srcode: str, age: int, birthday: str, sex: str, campus: str,
        collegeDept: str, yrlevelprogram: str, address: str, contactNum: str,
        fblink: str, bloodType: str, bloodDonation: str, medicalCondition: str, paymentOption: str,
        username: str, password: str, active: bool=True, accepted: bool=None, volunteerExpQ1="", volunteerExpQ2="",
        volunteerExpProof="", reasonQ1="", reasonQ2=""):

    return super().create((
        applyingAs, volunterismExperience, weekdaysTimeDevotion,
        weekendsTimeDevotion, areasOfInterest, fullname,
        email, affiliation, srcode, age, birthday, sex, campus, collegeDept,
        yrlevelprogram, address, contactNum, fblink, bloodType,
        bloodDonation, medicalCondition, paymentOption, username, password,
        active, accepted, volunteerExpQ1, volunteerExpQ2, volunteerExpProof,
        reasonQ1, reasonQ2
    ))
  
  def accept(self, id):
    member = super().get(id)
    if (member == None):
      return None

    super().updateSpecific(id, ["accepted"], (True,))
    account = AccountModel().create(
      accountType="member",
      password=member["password"],
      username=member["username"])

    AccountModel().updateSpecific(account["id"], ["membershipId"], (id,))
    return member

  def reject(self, id):
    member = super().get(id)
    if (member == None):
      return None

    super().updateSpecific(id, ["accepted"], (False,))
    return member

  def activate(self, id):
    memberMatch = super().get(id)
    if (memberMatch == None): return None

    super().updateSpecific(id, ["active"], (True,))
    accountMatch = AccountModel().getOrSearch(["id", "membershipId"], [None, id])
    if (len(accountMatch) > 0):
      AccountModel().activate(accountMatch[0]["id"])
      return {
        "activated": True,
        "account": accountMatch
      }
    return None

  def deactivate(self, id):
    member = super().get(id)
    if (member == None): return None

    super().updateSpecific(id, ["active"], (False,))
    accountMatch = AccountModel().getOrSearch(["id", "membershipId"], [None, id])
    if (len(accountMatch) > 0):
      AccountModel().deactivate(accountMatch[0]["id"])
      return accountMatch
    return None