from ..paramcheck import basicParamCheck

def loginParamCheck():
  missingParams = basicParamCheck([
    'username',
    'password'
  ])

  if (len(missingParams) > 0):
    return ({
      "fieldError": missingParams,
      "message": "Missing required fields"
    }, 400)

def registerParamCheck():
  missingParams = basicParamCheck([
    "applyingAs",
    "volunterismExperience",
    "weekdaysTimeDevotion",
    "weekendsTimeDevotion",
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
    "paymentOption",
    "username",
    "areasOfInterest",
    "password",
    # "medicalCondition",
    # "volunteerExpQ1",
    # "volunteerExpQ2",
    # "reasonQ1",
    # "reasonQ2",
  ], True)

  if (len(missingParams) > 0):
    return ({
      "fieldError": missingParams,
      "message": "Missing required fields"
    }, 400)