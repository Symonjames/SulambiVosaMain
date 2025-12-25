from ..paramcheck import basicParamCheck

def accountUpdateParamCheck():
  missingParams = basicParamCheck([
    'username',
    'password'
  ])

  if (len(missingParams) > 0):
    return ({
      "fieldError": missingParams,
      "message": "Missing required fields"
    }, 400)
