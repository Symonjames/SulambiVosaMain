from ..models.SignatoriesModel import SignatoriesModel
from flask import request

def updateSignatories(id: int):
  currentSignatory = SignatoriesModel().get(id)
  
  if currentSignatory is None:
    return ({ "message": "Signatory not found" }, 404)

  # Use existing values if new values are not provided (preserve existing data)
  # If field exists in request.json, use it (even if empty string). If not in request, preserve existing.
  preparedBy = request.json.get("preparedBy") if "preparedBy" in request.json else currentSignatory.get("preparedBy", "")
  reviewedBy = request.json.get("reviewedBy") if "reviewedBy" in request.json else currentSignatory.get("reviewedBy", "")
  recommendingApproval1 = request.json.get("recommendingApproval1") if "recommendingApproval1" in request.json else currentSignatory.get("recommendingApproval1", "")
  recommendingApproval2 = request.json.get("recommendingApproval2") if "recommendingApproval2" in request.json else currentSignatory.get("recommendingApproval2", "")
  approvedBy = request.json.get("approvedBy") if "approvedBy" in request.json else currentSignatory.get("approvedBy", "")
  
  # Titles: preserve existing or use defaults
  preparedTitle = request.json.get("preparedTitle") if "preparedTitle" in request.json else currentSignatory.get("preparedTitle", "Asst. Director, GAD Advocacies/GAD Head Secretariat/Coordinator")
  reviewedTitle = request.json.get("reviewedTitle") if "reviewedTitle" in request.json else currentSignatory.get("reviewedTitle", "Director, Extension Services/Head, Extension Services")
  approvedTitle = request.json.get("approvedTitle") if "approvedTitle" in request.json else currentSignatory.get("approvedTitle", "University President/Chancellor")
  recommendingSignatory1 = request.json.get("recommendingSignatory1") if "recommendingSignatory1" in request.json else currentSignatory.get("recommendingSignatory1", "Vice President/Vice Chancellor for Research, Development and Extension Services")
  recommendingSignatory2 = request.json.get("recommendingSignatory2") if "recommendingSignatory2" in request.json else currentSignatory.get("recommendingSignatory2", "Vice President/Vice Chancellor for Administration and Finance")

  SignatoriesModel().updateSpecific(id,
    [
      "preparedBy",
      "reviewedBy",
      "recommendingApproval1",
      "recommendingApproval2",
      "approvedBy",
      "preparedTitle",
      "reviewedTitle",
      "approvedTitle",
      "recommendingSignatory1",
      "recommendingSignatory2",
    ],
    (
      preparedBy if preparedBy is not None else "",
      reviewedBy if reviewedBy is not None else "",
      recommendingApproval1 if recommendingApproval1 is not None else "",
      recommendingApproval2 if recommendingApproval2 is not None else "",
      approvedBy if approvedBy is not None else "",
      preparedTitle if preparedTitle is not None else "Asst. Director, GAD Advocacies/GAD Head Secretariat/Coordinator",
      reviewedTitle if reviewedTitle is not None else "Director, Extension Services/Head, Extension Services",
      approvedTitle if approvedTitle is not None else "University President/Chancellor",
      recommendingSignatory1 if recommendingSignatory1 is not None else "Vice President/Vice Chancellor for Research, Development and Extension Services",
      recommendingSignatory2 if recommendingSignatory2 is not None else "Vice President/Vice Chancellor for Administration and Finance",
    )
  )

  return {
    "data": SignatoriesModel().get(id),
    "message": "Successfully updated signatories data"
  }

def getSignatoriesData(id: int):
  matchedSignatory = SignatoriesModel().get(id)
  if matchedSignatory:
    return {
      "data": matchedSignatory,
      "message": "Signatories data retrieved successfully"
    }
  return {
    "data": None,
    "message": "Signatories not found"
  }

