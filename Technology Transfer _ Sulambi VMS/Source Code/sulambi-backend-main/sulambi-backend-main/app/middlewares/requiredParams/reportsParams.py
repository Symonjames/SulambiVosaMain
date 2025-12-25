from flask import request
from ..paramcheck import basicParamFormCheck, basicParamFileCheck

def createExternalReportParamCheck():
  missingParams = []
  missingParams += basicParamFormCheck([
    "narrative"
  ])

  # missingParams += basicParamFileCheck([
  #   "photos"
  # ])

  if (len(missingParams) > 0):
    return ({
      "fieldError": missingParams,
      "message": "Missing required fields"
    }, 400)

def createInternalReportParamCheck():
  missingParams = []
  missingParams += basicParamFormCheck([
    "narrative",
    "budgetUtilized",
    "budgetUtilizedSrc",
    "psAttribution",
    "psAttributionSrc",
  ])

  # missingParams += basicParamFileCheck([
  #   "photos"
  # ])

  if (len(missingParams) > 0):
    return ({
      "fieldError": missingParams,
      "message": "Missing required fields"
    }, 400)