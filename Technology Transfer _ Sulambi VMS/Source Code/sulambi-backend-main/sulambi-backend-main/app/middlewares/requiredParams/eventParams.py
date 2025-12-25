from ..paramcheck import basicParamCheck

def externalEventParamCheck():
  missingParams = basicParamCheck([
    "extensionServiceType",
    "externalServiceType",
    "eventProposalType",
    "title",
    "location",
    "durationStart",
    "durationEnd",
    "sdg",
    "orgInvolved",
    "programInvolved",
    "projectLeader",
    "partners",
    "beneficiaries",
    "totalCost",
    "sourceOfFund",
    "rationale",
    "objectives",
    "expectedOutput",
    "description",
    "financialPlan",
    "dutiesOfPartner",
    "evaluationMechanicsPlan",
    "sustainabilityPlan",
    "evaluationSendTime"
  ], True)

  if (len(missingParams) > 0):
    return ({
      "fieldError": missingParams,
      "message": "Missing required fields"
    }, 400)

def internalEventParamCheck():
  missingParams = basicParamCheck([
    "title",
    "venue",
    "durationStart",
    "durationEnd",
    "modeOfDelivery",
    "projectTeam",
    "partner",
    "participant",
    "maleTotal",
    "femaleTotal",
    "rationale",
    "objectives",
    "description",
    "workPlan",
    "financialRequirement",
    "evaluationMechanicsPlan",
    "sustainabilityPlan",
    "eventProposalType",
    "evaluationSendTime"
  ], True)

  if (len(missingParams) > 0):
    return ({
      "fieldError": missingParams,
      "message": "Missing required fields"
    }, 400)
