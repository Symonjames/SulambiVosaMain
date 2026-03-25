from ..utils.multipartFileWriter import cloudinaryFileWriter
from werkzeug.exceptions import BadRequest
from ..models.ExternalEventModel import ExternalEventModel
from ..models.ExternalReportModel import ExternalReportModel
from ..models.InternalEventModel import InternalEventModel
from ..models.InternalReportModel import InternalReportModel
from ..models.RequirementsModel import RequirementsModel
from ..models.EvaluationModel import EvaluationModel
from ..models.SignatoriesModel import SignatoriesModel

from flask import request
import json

ExternalEventDb = ExternalEventModel()
ExternalReportDb = ExternalReportModel()
EvaluationDb = EvaluationModel()
InternalEventDb = InternalEventModel()
InternalReportDb = InternalReportModel()
RequirementsDb = RequirementsModel()
SignatoriesDb = SignatoriesModel()

def _normalize_numeric_input(value):
  """
  Accept currency-like input (e.g., "PHP 1,234.50") and normalize to an integer string.
  Returns None when invalid.
  """
  raw = str(value or "").strip()
  if raw == "":
    return "0"
  try:
    import re
    # Keep digits, decimal point and sign; strip currency labels/symbols and spaces.
    cleaned = re.sub(r"[^0-9.\-]", "", raw.replace(",", ""))
    if cleaned in ("", "-", ".", "-."):
      return None
    parsed = float(cleaned)
    # DB columns are INTEGER; accept decimal-style input and coerce to nearest whole value.
    return str(int(round(parsed)))
  except Exception:
    return None

def _validate_internal_financial_fields(form):
  amount_fields = [
    "approvedBudget",
    "budgetUtilized",
    "psAttribution",
  ]
  source_fields = [
    "approvedBudgetSrc",
    "budgetUtilizedSrc",
    "psAttributionSrc",
  ]
  cleaned = {}
  invalid = []
  for field in amount_fields:
    normalized = _normalize_numeric_input(form.get(field))
    if normalized is None:
      invalid.append(field)
    else:
      cleaned[field] = normalized
  for field in source_fields:
    cleaned[field] = str(form.get(field) or "").strip()
  return cleaned, invalid

def getAllReports():
  externalReports = ExternalReportDb.getAll()
  internalReports = InternalReportDb.getAll()

  returnableExternal = []
  returnableInternal = []

  # manual join the external event details
  for report in externalReports:
    matchedEvent = ExternalEventDb.get(report["eventId"])
    if (matchedEvent == None): continue
    report["eventId"] = matchedEvent
    report["signatoriesId"] = SignatoriesDb.get(report["signatoriesId"])
    report["photos"] = report["photos"].split(",") if report["photos"] else []
    report["photoCaptions"] = report["photoCaptions"].split(",") if report.get("photoCaptions") else []
    returnableExternal.append(report)

  # manual join the internal event details
  for report in internalReports:
    matchedEvent = InternalEventDb.get(report["eventId"])
    if (matchedEvent == None): continue
    report["eventId"] = matchedEvent
    report["signatoriesId"] = SignatoriesDb.get(report["signatoriesId"])
    report["photos"] = report["photos"].split(",") if report["photos"] else []
    report["photoCaptions"] = report["photoCaptions"].split(",") if report.get("photoCaptions") else []
    returnableInternal.append(report)

  return {
    "external": returnableExternal,
    "internal": returnableInternal,
    "message": "Successfully retrieved all reports"
  }

def getPublicReports():
  """Same as getAllReports but for public (landing page carousel). No auth required."""
  return getAllReports()

def getReportCalculations(eventId: int, eventType: str):
  from ..database.connection import convert_boolean_value
  accepted_value = convert_boolean_value(1)
  registeredUsers = RequirementsDb.getAndSearch(
    ["eventId", "type", "accepted"],
    [eventId, eventType, accepted_value])

  # filter only the one who attended
  onlyAttendedUsers = []
  onlyAttendedEvals = []
  for requirement in registeredUsers:
    evaluationMatch = EvaluationDb.getAndSearch(["requirementId"], [requirement["id"]])
    if (len(evaluationMatch) == 0):
      continue

    evaluationMatch = evaluationMatch[0]
    if (evaluationMatch["finalized"] == 1):
      onlyAttendedUsers.append(requirement)
      onlyAttendedEvals.append(evaluationMatch)

  # get specific signatories for the event mentioned
  signatoriesData = {}
  if (eventType == "external"):
    matchedEvent = ExternalEventDb.get(eventId)
    signId = matchedEvent.get("signatoriesId")
    signatoriesData = SignatoriesDb.get(signId)
  else:
    matchedEvent = InternalEventDb.get(eventId)
    signId = matchedEvent.get("signatoriesId")
    signatoriesData = SignatoriesDb.get(signId)

  # Participant stats based on accepted/joined requirements.
  participantStats = {
    "totalJoined": len(registeredUsers),
    "maleJoined": 0,
    "femaleJoined": 0,
    "insiderJoined": 0,   # BatStateU / with affiliation
    "outsiderJoined": 0,  # outside institutions / N/A affiliation
  }
  for req in registeredUsers:
    sex = str(req.get("sex") or "").lower().strip()
    affiliation = req.get("affiliation")
    if sex == "male":
      participantStats["maleJoined"] += 1
    elif sex == "female":
      participantStats["femaleJoined"] += 1
    if affiliation == "N/A" or affiliation is None or str(affiliation).strip() == "":
      participantStats["outsiderJoined"] += 1
    else:
      participantStats["insiderJoined"] += 1

  # Prefer analytics from satisfactionSurveys (new survey flow), fallback to evaluation table logic below.
  try:
    from ..database.connection import (
      table_name_for_query,
      convert_placeholders,
      DATABASE_URL,
      is_postgresql_url,
    )
    is_postgresql = is_postgresql_url(DATABASE_URL)
    conn, cursor = connection.cursorInstance()

    sat_table = table_name_for_query("satisfactionSurveys")
    req_table = table_name_for_query("requirements")
    sat_event_col = '"eventId"' if is_postgresql else "eventId"
    sat_type_col = '"eventType"' if is_postgresql else "eventType"
    sat_finalized_col = "finalized"
    sat_score_col = '"overallSatisfaction"' if is_postgresql else "overallSatisfaction"
    sat_req_id_col = '"requirementId"' if is_postgresql else "requirementId"
    req_id_col = "id"
    req_sex_col = "sex"
    req_aff_col = "affiliation"

    finalized_true = convert_boolean_value(True)
    sat_query = convert_placeholders(
      f"""
      SELECT ss.{sat_score_col}, ss.{sat_req_id_col}, r.{req_sex_col}, r.{req_aff_col}
      FROM {sat_table} ss
      LEFT JOIN {req_table} r ON ss.{sat_req_id_col} = r.{req_id_col}
      WHERE ss.{sat_event_col} = ? AND ss.{sat_type_col} = ? AND ss.{sat_finalized_col} = ?
      """
    )
    cursor.execute(sat_query, (eventId, eventType, finalized_true))
    survey_rows = cursor.fetchall() or []
    conn.close()

    def _score_to_bucket(score):
      try:
        val = float(score)
      except Exception:
        return None
      if val >= 4.5:
        return "excellent"
      if val >= 3.5:
        return "verySatisfactory"
      if val >= 2.5:
        return "satisfactory"
      if val >= 1.5:
        return "fair"
      if val > 0:
        return "poor"
      return None

    if len(survey_rows) > 0:
      if eventType == "external":
        def _blank_eval():
          return {
            "excellent": 0,
            "verySatisfactory": 0,
            "satisfactory": 0,
            "fair": 0,
            "poor": 0,
          }

        response = {
          "outsider": {
            "sex": {"male": 0, "female": 0},
            "evaluation": {"overall": _blank_eval(), "timeline": _blank_eval()},
          },
          "insider": {
            "sex": {"male": 0, "female": 0},
            "evaluation": {"overall": _blank_eval(), "timeline": _blank_eval()},
          },
          "signatoriesData": signatoriesData,
        }

        for score, _req_id, sex, affiliation in survey_rows:
          bucket = _score_to_bucket(score)
          if not bucket:
            continue
          grp = "outsider" if (affiliation == "N/A" or affiliation is None or str(affiliation).strip() == "") else "insider"
          sx = (str(sex or "").lower().strip())
          if sx in ["male", "female"]:
            response[grp]["sex"][sx] += 1
          response[grp]["evaluation"]["overall"][bucket] += 1
          # No dedicated timeline score in satisfactionSurveys; mirror overall bucket for continuity.
          response[grp]["evaluation"]["timeline"][bucket] += 1

        response["ratingTotals"] = {
          "excellent": response["insider"]["evaluation"]["overall"]["excellent"] + response["outsider"]["evaluation"]["overall"]["excellent"],
          "verySatisfactory": response["insider"]["evaluation"]["overall"]["verySatisfactory"] + response["outsider"]["evaluation"]["overall"]["verySatisfactory"],
          "satisfactory": response["insider"]["evaluation"]["overall"]["satisfactory"] + response["outsider"]["evaluation"]["overall"]["satisfactory"],
          "fair": response["insider"]["evaluation"]["overall"]["fair"] + response["outsider"]["evaluation"]["overall"]["fair"],
          "poor": response["insider"]["evaluation"]["overall"]["poor"] + response["outsider"]["evaluation"]["overall"]["poor"],
        }
        response["participantStats"] = participantStats

        return {
          "data": response,
          "message": "Successfully retrieved event report analytics (from surveys)"
        }

      if eventType == "internal":
        response = {
          "sex": {"male": 0, "female": 0},
          "evalResult": {
            "male": {"excellent": 0, "verySatisfactory": 0, "satisfactory": 0, "fair": 0, "poor": 0},
            "female": {"excellent": 0, "verySatisfactory": 0, "satisfactory": 0, "fair": 0, "poor": 0},
          },
          "signatoriesData": signatoriesData,
        }

        for score, _req_id, sex, _affiliation in survey_rows:
          bucket = _score_to_bucket(score)
          sx = str(sex or "").lower().strip()
          if not bucket or sx not in ["male", "female"]:
            continue
          response["sex"][sx] += 1
          response["evalResult"][sx][bucket] += 1

        response["ratingTotals"] = {
          "excellent": response["evalResult"]["male"]["excellent"] + response["evalResult"]["female"]["excellent"],
          "verySatisfactory": response["evalResult"]["male"]["verySatisfactory"] + response["evalResult"]["female"]["verySatisfactory"],
          "satisfactory": response["evalResult"]["male"]["satisfactory"] + response["evalResult"]["female"]["satisfactory"],
          "fair": response["evalResult"]["male"]["fair"] + response["evalResult"]["female"]["fair"],
          "poor": response["evalResult"]["male"]["poor"] + response["evalResult"]["female"]["poor"],
        }
        response["participantStats"] = participantStats

        return {
          "data": response,
          "message": "Successfully retrieved report analytics (from surveys)"
        }
  except Exception as survey_error:
    print(f"[REPORT_ANALYTICS] satisfactionSurveys query failed, using fallback: {survey_error}")

  if (eventType == "external"):
    # users sex details
    attendedOutsiderMale = 0
    attendedOutsiderFemale = 0
    attendedBsuMale = 0
    attendedBsuFemale = 0

    # users overall experience details
    outsiderExcellent = 0
    outsiderVerySatisfactory = 0
    outsiderSatisfactory = 0
    outsiderFair = 0
    outsiderPoor = 0
    bsuExcellent = 0
    bsuVerySatisfactory = 0
    bsuSatisfactory = 0
    bsuFair = 0
    bsuPoor = 0

    # user overall experience with the timeline
    timelineoutsiderExcellent = 0
    timelineoutsiderVerySatisfactory = 0
    timelineoutsiderSatisfactory = 0
    timelineoutsiderFair = 0
    timelineoutsiderPoor = 0
    timelinebsuExcellent = 0
    timelinebsuVerySatisfactory = 0
    timelinebsuSatisfactory = 0
    timelinebsuFair = 0
    timelinebsuPoor = 0

    # im too tired to think of solution...
    for requirement, evaluation in zip(onlyAttendedUsers, onlyAttendedEvals):
      # count satisfactory of users outside campus
      evalCriteriaString = evaluation["criteria"]
      evalCriteriaDict: dict = safeJsonParser(evalCriteriaString)

      # safe parsable test
      if (not evalCriteriaDict):
        continue

      if (requirement["affiliation"] == "N/A"):
        # count sex outside of campus
        if (requirement["sex"].lower() == "male"):
          attendedOutsiderMale += 1
        else:
          attendedOutsiderFemale += 1

        if ((evalCriteriaDict.get("overall") or "").lower() == "excellent"):
          outsiderExcellent += 1
        if ((evalCriteriaDict.get("overall") or "").lower() == "very satisfactory"):
          outsiderVerySatisfactory += 1
        if ((evalCriteriaDict.get("overall") or "").lower() == "satisfactory"):
          outsiderSatisfactory += 1
        if ((evalCriteriaDict.get("overall") or "").lower() == "fair"):
          outsiderFair += 1
        if ((evalCriteriaDict.get("overall") or "").lower() == "poor"):
          outsiderPoor += 1

        # timeline calculation
        if ((evalCriteriaDict.get("time") or "").lower() == "excellent"):
          timelineoutsiderExcellent += 1
        if ((evalCriteriaDict.get("time") or "").lower() == "very satisfactory"):
          timelineoutsiderVerySatisfactory += 1
        if ((evalCriteriaDict.get("time") or "").lower() == "satisfactory"):
          timelineoutsiderSatisfactory += 1
        if ((evalCriteriaDict.get("time") or "").lower() == "fair"):
          timelineoutsiderFair += 1
        if ((evalCriteriaDict.get("time") or "").lower() == "poor"):
          timelineoutsiderPoor += 1
      else:
        # count bsu sex volunteer
        if ((requirement.get("sex") or "").lower() == "male"):
          attendedBsuMale += 1
        else:
          attendedBsuFemale += 1

        # overall performance
        if ((evalCriteriaDict.get("overall") or "").lower() == "excellent"):
          bsuExcellent += 1
        if ((evalCriteriaDict.get("overall") or "").lower() == "very satisfactory"):
          bsuVerySatisfactory += 1
        if ((evalCriteriaDict.get("overall") or "").lower() == "satisfactory"):
          bsuSatisfactory += 1
        if ((evalCriteriaDict.get("overall") or "").lower() == "fair"):
          bsuFair += 1
        if ((evalCriteriaDict.get("overall") or "").lower() == "poor"):
          bsuPoor += 1

        # timeline performance
        if ((evalCriteriaDict.get("time") or "").lower() == "excellent"):
          timelinebsuExcellent += 1
        if ((evalCriteriaDict.get("time") or "").lower() == "very satisfactory"):
          timelinebsuVerySatisfactory += 1
        if ((evalCriteriaDict.get("time") or "").lower() == "satisfactory"):
          timelinebsuSatisfactory += 1
        if ((evalCriteriaDict.get("time") or "").lower() == "fair"):
          timelinebsuFair += 1
        if ((evalCriteriaDict.get("time") or "").lower() == "poor"):
          timelinebsuPoor += 1

    return {
      "data": {
        "outsider": {
          "sex": {
            "male": attendedOutsiderMale,
            "female": attendedOutsiderFemale
          },
          "evaluation": {
            "overall": {
              "excellent": outsiderExcellent,
              "verySatisfactory": outsiderVerySatisfactory,
              "satisfactory": outsiderSatisfactory,
              "fair": outsiderFair,
              "poor": outsiderPoor
            },
            "timeline": {
              "excellent": timelineoutsiderExcellent,
              "verySatisfactory": timelineoutsiderVerySatisfactory,
              "satisfactory": timelineoutsiderSatisfactory,
              "fair": timelineoutsiderFair,
              "poor": timelineoutsiderPoor
            }
          }
        },
        "insider": {
          "sex": {
            "male": attendedBsuMale,
            "female": attendedBsuFemale
          },
          "evaluation": {
            "overall": {
              "excellent": bsuExcellent,
              "verySatisfactory": bsuVerySatisfactory,
              "satisfactory": bsuSatisfactory,
              "fair": bsuFair,
              "poor": bsuPoor
            },
            "timeline": {
              "excellent": timelinebsuExcellent,
              "verySatisfactory": timelinebsuVerySatisfactory,
              "satisfactory": timelinebsuSatisfactory,
              "fair": timelinebsuFair,
              "poor": timelinebsuPoor
            }
          }
        },
        "signatoriesData": signatoriesData,
        "ratingTotals": {
          "excellent": outsiderExcellent + bsuExcellent,
          "verySatisfactory": outsiderVerySatisfactory + bsuVerySatisfactory,
          "satisfactory": outsiderSatisfactory + bsuSatisfactory,
          "fair": outsiderFair + bsuFair,
          "poor": outsiderPoor + bsuPoor,
        },
        "participantStats": participantStats
      },
      "message": "Successfully retrieved event report analytics"
    }
  
  responseFormat = {
    "sex": {
      "male": 0,
      "female": 0
    },
    "evalResult": {
      "male": {
        "excellent": 0,
        "verySatisfactory": 0,
        "satisfactory": 0,
        "fair": 0,
        "poor": 0
      },
      "female": {
        "excellent": 0,
        "verySatisfactory": 0,
        "satisfactory": 0,
        "fair": 0,
        "poor": 0
      }
    },
    "signatoriesData": signatoriesData
  }

  if (eventType == "internal"):
    for requirement, evaluation in zip(onlyAttendedUsers, onlyAttendedEvals):
      evalCriteriaString = evaluation["criteria"]
      evalCriteriaDict: dict = safeJsonParser(evalCriteriaString)

      if (requirement["sex"] == "male"):
        responseFormat["sex"]["male"] += 1
        if (evalCriteriaDict.get("overall").lower() == "excellent"):
          responseFormat["evalResult"]["male"]["excellent"] += 1
        if (evalCriteriaDict.get("overall").lower() == "very satisfactory"):
          responseFormat["evalResult"]["male"]["verySatisfactory"] += 1
        if (evalCriteriaDict.get("overall").lower() == "satisfactory"):
          responseFormat["evalResult"]["male"]["satisfactory"] += 1
        if (evalCriteriaDict.get("overall").lower() == "fair"):
          responseFormat["evalResult"]["male"]["fair"] += 1
        if (evalCriteriaDict.get("overall").lower() == "poor"):
          responseFormat["evalResult"]["male"]["poor"] += 1
      else:
        responseFormat["sex"]["female"] += 1
        if (evalCriteriaDict.get("overall").lower() == "excellent"):
          responseFormat["evalResult"]["female"]["excellent"] += 1
        if (evalCriteriaDict.get("overall").lower() == "very satisfactory"):
          responseFormat["evalResult"]["female"]["verySatisfactory"] += 1
        if (evalCriteriaDict.get("overall").lower() == "satisfactory"):
          responseFormat["evalResult"]["female"]["satisfactory"] += 1
        if (evalCriteriaDict.get("overall").lower() == "fair"):
          responseFormat["evalResult"]["female"]["fair"] += 1
        if (evalCriteriaDict.get("overall").lower() == "poor"):
          responseFormat["evalResult"]["female"]["poor"] += 1

    responseFormat["ratingTotals"] = {
      "excellent": responseFormat["evalResult"]["male"]["excellent"] + responseFormat["evalResult"]["female"]["excellent"],
      "verySatisfactory": responseFormat["evalResult"]["male"]["verySatisfactory"] + responseFormat["evalResult"]["female"]["verySatisfactory"],
      "satisfactory": responseFormat["evalResult"]["male"]["satisfactory"] + responseFormat["evalResult"]["female"]["satisfactory"],
      "fair": responseFormat["evalResult"]["male"]["fair"] + responseFormat["evalResult"]["female"]["fair"],
      "poor": responseFormat["evalResult"]["male"]["poor"] + responseFormat["evalResult"]["female"]["poor"],
    }
    responseFormat["participantStats"] = participantStats

    return {
      "data": responseFormat,
      "message": "Successfully retrieved report analytics"
    }


def getReportByEventId(eventId: int, eventType: str):
  if (eventType == "external"):
    matchedEvent = ExternalEventDb.get(eventId)
    if (matchedEvent == None):
      return ({"message": "Event ID does not exist"}, 404)

    matchedReport = ExternalReportDb.getAndSearch(["eventId"], [id])
    if (matchedReport == None):
      return ({"message": "No report submitted for this event"}, 404)

    return {
      "data": matchedReport,
      "message": "Successfully retrieved report"
    }

  if (eventType == "internal"):
    matchedEvent = InternalEventDb.get(eventId)
    if (matchedEvent == None):
      return ({"message": "Event ID does not exist"}, 404)

    matchedReport = InternalEventDb.getAndSearch(["eventId"], [id])
    if (matchedReport == None):
      return ({"message": "No report submitted for this event"}, 403)

    return {
      "data": matchedReport,
      "message": "Successfully retrieved report"
    }

def createReport(eventId: int, eventType: str):
  try:
    photoPath = cloudinaryFileWriter(["photo_0", "photo_1", "photos"], folder="reports")
  except BadRequest as e:
    return ({"message": str(e)}, 400)
  except Exception as e:
    return ({"message": f"Failed to upload photos: {str(e)}"}, 500)
  photoNames = ",".join([photoPath[key] for key in sorted(photoPath)])
  
  # Extract photo captions from form data
  photoCaptions = []
  for key in photoPath:
    captionKey = f"photo_caption_{list(photoPath.keys()).index(key)}"
    caption = request.form.get(captionKey, "")
    photoCaptions.append(caption)
  photoCaptionsStr = ",".join(photoCaptions)

  # checks if report has been submitted to the event id
  if (eventType == "external"):
    matchedEvent = ExternalEventDb.get(eventId)

    if (matchedEvent == None):
      return ({"message": "Event ID does not exist"}, 404)

    matchedReport = ExternalReportDb.getAndSearch(["eventId"], [eventId])
    if (len(matchedReport) > 0):
      return ({"message": "A report for this event has already been submitted"}, 403)


    # creation of external report
    createdReport = ExternalReportDb.create(
      eventId=eventId,
      narrative=request.form.get("narrative"),
      photos=photoNames,
      photoCaptions=photoCaptionsStr,
      signatoriesId=matchedEvent.get("signatoriesId")
    )

    # assigning of signatories
    # ExternalReportDb.updateSpecific([])
    createdReport["eventId"] = matchedEvent
    return {
      "data": createdReport,
      "message": "Successfully submitted report"
    }

  # checks if report has been submitted to the event id
  if (eventType == "internal"):
    matchedEvent = InternalEventDb.get(eventId)

    if (matchedEvent == None):
      return ({"message": "Event ID does not exist"}, 404)

    matchedReport = InternalReportDb.getAndSearch(["eventId"], [eventId])
    if (len(matchedReport) > 0):
      return ({"message": "A report for this event has already been submitted"}, 403)

    cleanedFinancial, invalidFinancial = _validate_internal_financial_fields(request.form)
    if invalidFinancial:
      return ({
        "fieldError": invalidFinancial,
        "message": "Financial amount fields must contain valid numbers"
      }, 400)

    createdReport = InternalReportDb.create(
      eventId=eventId,
      narrative=request.form.get("narrative"),
      approvedBudget=cleanedFinancial["approvedBudget"],
      approvedBudgetSrc=cleanedFinancial["approvedBudgetSrc"],
      budgetUtilized=cleanedFinancial["budgetUtilized"],
      budgetUtilizedSrc=cleanedFinancial["budgetUtilizedSrc"],
      psAttribution=cleanedFinancial["psAttribution"],
      psAttributionSrc=cleanedFinancial["psAttributionSrc"],
      photos=photoNames,
      photoCaptions=photoCaptionsStr,
      signatoriesId=matchedEvent.get("signatoriesId")
    )

    createdReport["eventId"] = matchedEvent
    return {
      "data": createdReport,
      "message": "Successfully submitted report"
    }

def updateReport(reportId: int, reportType: str):
  """Update a report by ID and type"""
  try:
    print(f"Attempting to update {reportType} report with ID: {reportId}")
    
    try:
      photoPath = cloudinaryFileWriter(["photo_0", "photo_1", "photos"], folder="reports")
    except BadRequest as e:
      return ({"message": str(e)}, 400)
    except Exception as e:
      return ({"message": f"Failed to upload photos: {str(e)}"}, 500)
    photoNames = ",".join([photoPath[key] for key in sorted(photoPath)])
    
    # Extract photo captions from form data
    photoCaptions = []
    for key in photoPath:
      captionKey = f"photo_caption_{list(photoPath.keys()).index(key)}"
      caption = request.form.get(captionKey, "")
      photoCaptions.append(caption)
    photoCaptionsStr = ",".join(photoCaptions)
    
    if reportType == "external":
      # Check if report exists
      existingReport = ExternalReportDb.get(reportId)
      if not existingReport:
        print(f"External report with ID {reportId} not found")
        return ({"message": "External report not found"}, 404)
      
      # Update specific fields - only update photos/captions if new photos were uploaded
      updateFields = ["narrative"]
      updateValues = [request.form.get("narrative")]
      
      # Only update photos if new photos were uploaded
      if photoNames:
        updateFields.extend(["photos", "photoCaptions"])
        updateValues.extend([photoNames, photoCaptionsStr])
      
      ExternalReportDb.updateSpecific(reportId, updateFields, tuple(updateValues))
      
      updatedReport = ExternalReportDb.get(reportId)
      updatedReport["eventId"] = ExternalEventDb.get(updatedReport["eventId"])
      updatedReport["signatoriesId"] = SignatoriesDb.get(updatedReport["signatoriesId"])
      updatedReport["photos"] = updatedReport["photos"].split(",") if updatedReport["photos"] else []
      updatedReport["photoCaptions"] = updatedReport["photoCaptions"].split(",") if updatedReport.get("photoCaptions") else []
      
      return {
        "data": updatedReport,
        "message": "External report updated successfully"
      }
    
    elif reportType == "internal":
      # Check if report exists
      existingReport = InternalReportDb.get(reportId)
      if not existingReport:
        print(f"Internal report with ID {reportId} not found")
        return ({"message": "Internal report not found"}, 404)
      
      cleanedFinancial, invalidFinancial = _validate_internal_financial_fields(request.form)
      if invalidFinancial:
        return ({
          "fieldError": invalidFinancial,
          "message": "Financial amount fields must contain valid numbers"
        }, 400)

      # Update specific fields
      updateFields = [
        "narrative",
        "approvedBudget",
        "approvedBudgetSrc",
        "budgetUtilized",
        "budgetUtilizedSrc",
        "psAttribution",
        "psAttributionSrc",
      ]
      updateValues = [
        request.form.get("narrative"),
        cleanedFinancial["approvedBudget"],
        cleanedFinancial["approvedBudgetSrc"],
        cleanedFinancial["budgetUtilized"],
        cleanedFinancial["budgetUtilizedSrc"],
        cleanedFinancial["psAttribution"],
        cleanedFinancial["psAttributionSrc"]
      ]
      
      # Only update photos if new photos were uploaded
      if photoNames:
        updateFields.extend(["photos", "photoCaptions"])
        updateValues.extend([photoNames, photoCaptionsStr])
      
      InternalReportDb.updateSpecific(reportId, updateFields, tuple(updateValues))
      
      updatedReport = InternalReportDb.get(reportId)
      updatedReport["eventId"] = InternalEventDb.get(updatedReport["eventId"])
      updatedReport["signatoriesId"] = SignatoriesDb.get(updatedReport["signatoriesId"])
      updatedReport["photos"] = updatedReport["photos"].split(",") if updatedReport["photos"] else []
      updatedReport["photoCaptions"] = updatedReport["photoCaptions"].split(",") if updatedReport.get("photoCaptions") else []
      
      return {
        "data": updatedReport,
        "message": "Internal report updated successfully"
      }
    
    else:
      print(f"Invalid report type: {reportType}")
      return ({"message": "Invalid report type"}, 400)
      
  except Exception as e:
    print(f"Error updating {reportType} report with ID {reportId}: {str(e)}")
    import traceback
    traceback.print_exc()
    return ({"message": f"Error updating report: {str(e)}"}, 500)

def deleteReport(reportId: int, reportType: str):
  """Delete a report by ID and type"""
  try:
    print(f"Attempting to delete {reportType} report with ID: {reportId}")
    
    if reportType == "external":
      # Check if report exists
      existingReport = ExternalReportDb.get(reportId)
      if not existingReport:
        print(f"External report with ID {reportId} not found")
        return ({"message": "External report not found"}, 404)
      
      print(f"Found external report: {existingReport}")
      # Delete the report
      deletedReport = ExternalReportDb.delete(reportId)
      print(f"Successfully deleted external report: {deletedReport}")
      return {
        "message": "External report deleted successfully",
        "deletedReport": deletedReport
      }
    
    elif reportType == "internal":
      # Check if report exists
      existingReport = InternalReportDb.get(reportId)
      if not existingReport:
        print(f"Internal report with ID {reportId} not found")
        return ({"message": "Internal report not found"}, 404)
      
      print(f"Found internal report: {existingReport}")
      # Delete the report
      deletedReport = InternalReportDb.delete(reportId)
      print(f"Successfully deleted internal report: {deletedReport}")
      return {
        "message": "Internal report deleted successfully",
        "deletedReport": deletedReport
      }
    
    else:
      print(f"Invalid report type: {reportType}")
      return ({"message": "Invalid report type"}, 400)
      
  except Exception as e:
    print(f"Error deleting {reportType} report with ID {reportId}: {str(e)}")
    return ({"message": f"Error deleting report: {str(e)}"}, 500)


def safeJsonParser(jsonStr: str) -> dict:
  try:
    return json.loads(jsonStr)
  except:
    return False