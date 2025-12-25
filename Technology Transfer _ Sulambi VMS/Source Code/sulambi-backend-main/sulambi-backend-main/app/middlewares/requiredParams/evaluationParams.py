from ..paramcheck import basicParamCheck

def evaluationParamCheck():
  missingParams = basicParamCheck([
    "criteria",
    "q13",
    "q14",
    "comment",
    "recommendations"
  ], True)

  if (len(missingParams) > 0):
    return ({
      "fieldError": missingParams,
      "message": "Missing required fields"
    }, 400)