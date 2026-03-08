from ..models.ExternalEventModel import ExternalEventModel
from ..models.InternalEventModel import InternalEventModel
from ..models.ExternalReportModel import ExternalReportModel
from ..models.InternalReportModel import InternalReportModel
from ..models.SignatoriesModel import SignatoriesModel

from ..models.AccountModel import AccountModel
from ..models.RequirementsModel import RequirementsModel
from ..models.EvaluationModel import EvaluationModel

from ..modules.LSIAlgorithm import LSICosineSimilarityMatch

from flask import request, g
from datetime import datetime
import random
from ..database import connection
from ..database.connection import table_name_for_query, convert_placeholders

ExternalEventDb = ExternalEventModel()
InternalEventDb = InternalEventModel()
ExternalReportDb = ExternalReportModel()
InternalReportDb = InternalReportModel()
RequirementsDb  = RequirementsModel()
SignatoriesDb = SignatoriesModel()
EvaluationDb = EvaluationModel()
AccountDb = AccountModel()

def _validate_beneficiary_pin(pin_val):
  """Validate beneficiary evaluation PIN: exactly 5 digits, numbers only. Returns (ok, message_or_pin)."""
  pin_val = (pin_val or "").strip()
  if not pin_val:
    return False, "Beneficiary evaluation PIN is required. Every event has one PIN that all beneficiaries use to submit feedback for this event."
  if len(pin_val) != 5 or not pin_val.isdigit():
    return False, "Beneficiary evaluation PIN must be exactly 5 digits (numbers only)."
  return True, pin_val

def _coerce_or_generate_beneficiary_pin(pin_val):
  """Return a valid 5-digit PIN; auto-generate when missing/invalid (for backward-compatible edits)."""
  ok, result = _validate_beneficiary_pin(pin_val)
  if ok:
    return result
  return f"{random.randint(10000, 99999)}"

def getAll():
  try:
    # manual mapping of user details
    accountSessionInfo = g.get("accountSessionInfo")
    if not accountSessionInfo:
      return ({"message": "Authentication required. Please log in."}, 403)
    
    externalEvents = ExternalEventDb.getAll()
    internalEvents = InternalEventDb.getAll()

    combinedEvents = []

    if (accountSessionInfo.get("accountType") == "admin"):
      externalEvents = [event for event in externalEvents if event.get("status") != "editing"]
      internalEvents = [event for event in internalEvents if event.get("status") != "editing"]

    # Members see all accepted, not-ended events (including not-yet-public). Only homepage uses toPublic.
    if (accountSessionInfo.get("accountType") == "member"):
      timeNow = int(datetime.now().timestamp() * 1000)
      externalEvents = [event for event in externalEvents if event.get("status") == "accepted" and event.get("durationEnd", 0) - timeNow > 0]
      internalEvents = [event for event in internalEvents if event.get("status") == "accepted" and event.get("durationEnd", 0) - timeNow > 0]

    # Batch fetch all related data to avoid N+1 queries
    # Collect all unique IDs
    all_created_by_ids = set()
    all_signatory_ids = set()
    all_external_event_ids = []
    all_internal_event_ids = []
    
    for event in externalEvents:
      if event.get("createdBy"):
        all_created_by_ids.add(event["createdBy"])
      if event.get("signatoriesId"):
        all_signatory_ids.add(event["signatoriesId"])
      if event.get("id"):
        all_external_event_ids.append(event["id"])
    
    for event in internalEvents:
      if event.get("createdBy"):
        all_created_by_ids.add(event["createdBy"])
      if event.get("signatoriesId"):
        all_signatory_ids.add(event["signatoriesId"])
      if event.get("id"):
        all_internal_event_ids.append(event["id"])
    
    # Batch fetch accounts/signatories with a single query per table (with safe fallback)
    accounts_map = {}
    signatories_map = {}
    try:
      conn, cursor = connection.cursorInstance()

      if all_created_by_ids:
        account_ids = list(all_created_by_ids)
        placeholders = ",".join(["?" for _ in account_ids])
        accounts_table = table_name_for_query("accounts")
        account_query = convert_placeholders(
          f"SELECT * FROM {accounts_table} WHERE id IN ({placeholders})"
        )
        cursor.execute(account_query, tuple(account_ids))
        rows = cursor.fetchall() or []
        col_names = [d[0] for d in cursor.description] if cursor.description else []
        for row in rows:
          row_dict = {col_names[i]: row[i] for i in range(len(col_names))}
          if row_dict.get("id") is not None:
            accounts_map[row_dict["id"]] = row_dict

      if all_signatory_ids:
        signatory_ids = list(all_signatory_ids)
        placeholders = ",".join(["?" for _ in signatory_ids])
        signatories_table = table_name_for_query("eventSignatories")
        signatory_query = convert_placeholders(
          f"SELECT * FROM {signatories_table} WHERE id IN ({placeholders})"
        )
        cursor.execute(signatory_query, tuple(signatory_ids))
        rows = cursor.fetchall() or []
        col_names = [d[0] for d in cursor.description] if cursor.description else []
        for row in rows:
          row_dict = {col_names[i]: row[i] for i in range(len(col_names))}
          if row_dict.get("id") is not None:
            signatories_map[row_dict["id"]] = row_dict
      conn.close()
    except Exception as e:
      print(f"Bulk account/signatory fetch failed, using fallback: {e}")
      for account_id in all_created_by_ids:
        try:
          account = AccountDb.get(account_id)
          if account:
            accounts_map[account_id] = account
        except Exception:
          pass
      for signatory_id in all_signatory_ids:
        try:
          signatory = SignatoriesDb.get(signatory_id)
          if signatory:
            signatories_map[signatory_id] = signatory
        except Exception:
          pass
    
    # Batch check for reports (one query per report type instead of per event)
    try:
      external_event_ids_with_reports = ExternalReportDb.get_event_ids_with_reports()
      external_reports_map = {eid: True for eid in external_event_ids_with_reports}
    except Exception as e:
      print(f"Error batch-fetching external report event IDs: {e}")
      external_reports_map = {}
    try:
      internal_event_ids_with_reports = InternalReportDb.get_event_ids_with_reports()
      internal_reports_map = {eid: True for eid in internal_event_ids_with_reports}
    except Exception as e:
      print(f"Error batch-fetching internal report event IDs: {e}")
      internal_reports_map = {}
    
    # external events formatting using cached data
    for i in range(len(externalEvents)):
      try:
        event_id = externalEvents[i].get("id")
        created_by_id = externalEvents[i].get("createdBy")
        signatory_id = externalEvents[i].get("signatoriesId")
        
        externalEvents[i]["createdBy"] = accounts_map.get(created_by_id) if created_by_id else None
        externalEvents[i]["hasReport"] = external_reports_map.get(event_id, False)
        externalEvents[i]["eventTypeIndicator"] = "external"
        externalEvents[i]["signatoriesId"] = signatories_map.get(signatory_id) if signatory_id else None
      except Exception as e:
        print(f"Error formatting external event {externalEvents[i].get('id', 'unknown')}: {e}")
        # Continue with next event

    # internal events formatting using cached data
    for i in range(len(internalEvents)):
      try:
        event_id = internalEvents[i].get("id")
        created_by_id = internalEvents[i].get("createdBy")
        signatory_id = internalEvents[i].get("signatoriesId")
        
        internalEvents[i]["createdBy"] = accounts_map.get(created_by_id) if created_by_id else None
        internalEvents[i]["hasReport"] = internal_reports_map.get(event_id, False)
        internalEvents[i]["eventTypeIndicator"] = "internal"
        internalEvents[i]["signatoriesId"] = signatories_map.get(signatory_id) if signatory_id else None
      except Exception as e:
        print(f"Error formatting internal event {internalEvents[i].get('id', 'unknown')}: {e}")
        # Continue with next event

    # sort combined events
    combinedEvents: list = externalEvents + internalEvents
    combinedEvents.sort(key=lambda x: x.get("createdAt", 0) or 0, reverse=True)

    return {
      "events": combinedEvents,
      "external": externalEvents,
      "internal": internalEvents,
      "message": "Successfully retrieved all events"
    }
  except Exception as e:
    print(f"Error in getAll events: {e}")
    import traceback
    traceback.print_exc()
    return ({
      "message": f"Error retrieving events: {str(e)}"
    }, 500)

def getOne(id: int, eventType: str):
  try:
    if (eventType == "external"):
      eventData = ExternalEventDb.get(id)
      if not eventData:
        return ({
          "message": "External event not found"
        }, 404)
      return {
        "data": eventData,
        "message": "Successfully retrieved external event"
      }

    if (eventType == "internal"):
      eventData = InternalEventDb.get(id)
      
      if not eventData:
        return ({
          "message": "Internal event not found"
        }, 404)
      
      # Query activity_month_assignments table
      activities = []
      try:
        conn, cursor = connection.cursorInstance()
        from ..database.connection import quote_identifier, convert_placeholders
        table_name = quote_identifier('activity_month_assignments')
        query = f"""
          SELECT activity_name, month 
          FROM {table_name}
          WHERE eventid = ?
          ORDER BY activity_name, month
        """
        query = convert_placeholders(query)
        cursor.execute(query, (id,))
        
        assignments = cursor.fetchall()
        
        # Group assignments by activity name
        activities_dict = {}
        for activity_name, month in assignments:
          if activity_name not in activities_dict:
            activities_dict[activity_name] = []
          activities_dict[activity_name].append(month)
        
        # Convert to list format with months array
        activities = [
          {"activity_name": name, "months": sorted(months)}
          for name, months in activities_dict.items()
        ]
        
        conn.close()
      except Exception as e:
        print(f"Error fetching activity_month_assignments: {e}")
        import traceback
        traceback.print_exc()
        # If table doesn't exist or error occurs, activities will remain empty list
      
      # Add activities to event data
      if eventData:
        eventData["activities"] = activities
      
      return {
        "data": eventData,
        "message": "Successfully retrieved internal event"
      }
    
    return ({
      "message": "Invalid event type"
    }, 400)
  except Exception as e:
    print(f"Error in getOne event: {e}")
    import traceback
    traceback.print_exc()
    return ({
      "message": f"Error retrieving event: {str(e)}"
    }, 500)

def getPublicEvents():
  # Public route - no authentication required. Used for the homepage only.
  # Only events with toPublic=True are shown here. Logged-in members see all approved
  # events (including non-public) on their Events page via getAll().
  allExternalEvents = ExternalEventDb.getAll()
  allInternalEvents = InternalEventDb.getAll()
  
  # Homepage: only events marked "For public" and not yet finished (durationEnd > now).
  # Members with accounts see all approved events on their Events page even if not public.
  time_now_ms = int(datetime.now().timestamp() * 1000)
  externalEvents = []
  for event in allExternalEvents:
    status_lower = str(event.get("status", "")).lower().strip()
    to_public = event.get("toPublic") in (True, 1, "true", "1")
    duration_end = int(event.get("durationEnd") or 0)
    not_finished = duration_end > time_now_ms
    if status_lower not in ["editing", "rejected"] and to_public and not_finished:
      event["eventTypeIndicator"] = "external"
      externalEvents.append(event)
    else:
      pass  # excluded
  internalEvents = []
  for event in allInternalEvents:
    status_lower = str(event.get("status", "")).lower().strip()
    to_public = event.get("toPublic") in (True, 1, "true", "1")
    duration_end = int(event.get("durationEnd") or 0)
    not_finished = duration_end > time_now_ms
    if status_lower not in ["editing", "rejected"] and to_public and not_finished:
      event["eventTypeIndicator"] = "internal"
      internalEvents.append(event)
    else:
      pass  # excluded
  
  return {
    "external": externalEvents,
    "internal": internalEvents,
    "message": "Successfully retrieved all public events"
  }

def _duration_end_ms(value):
  """Normalize durationEnd to milliseconds (DB may store seconds or ms)."""
  v = int(value or 0)
  if v <= 0:
    return 0
  if v < 1e12:
    return v * 1000
  return v

def _duration_start_ms(value):
  """Normalize durationStart to milliseconds (DB may store seconds or ms)."""
  v = int(value or 0)
  if v <= 0:
    return 0
  if v < 1e12:
    return v * 1000
  return v

def _is_event_open_for_beneficiary_evaluation(duration_start, duration_end, now_ms):
  """Eligible when ongoing OR ended within last 7 days."""
  start_ms = _duration_start_ms(duration_start)
  end_ms = _duration_end_ms(duration_end)
  if start_ms <= 0 or end_ms <= 0:
    return False
  ongoing = start_ms <= now_ms < end_ms
  ended_within_week = end_ms <= now_ms and end_ms >= (now_ms - (7 * 24 * 60 * 60 * 1000))
  return ongoing or ended_within_week


def getBeneficiaryEligibleEvents():
  """
  Public route. Returns events eligible for beneficiary evaluation:
  public, accepted (or similar), and within evaluation window
  (ongoing OR ended within the last 7 days).
  Each event includes requiresBeneficiaryPin (true if event has a PIN set).
  """
  time_now_ms = int(datetime.now().timestamp() * 1000)

  allExternalEvents = ExternalEventDb.getAll()
  allInternalEvents = InternalEventDb.getAll()

  externalList = []
  for event in allExternalEvents:
    status_lower = str(event.get("status", "")).lower().strip()
    to_public = event.get("toPublic") in (True, 1, "true", "1")
    in_window = _is_event_open_for_beneficiary_evaluation(event.get("durationStart"), event.get("durationEnd"), time_now_ms)
    if status_lower not in ["editing", "rejected"] and to_public and in_window:
      pin_val = (event.get("beneficiaryEvaluationPin") or "").strip()
      if not pin_val:
        continue  # every event must have a PIN for beneficiary evaluation; skip if missing
      e = dict(event)
      e.pop("beneficiaryEvaluationPin", None)  # never expose PIN to frontend
      e["eventTypeIndicator"] = "external"
      e["requiresBeneficiaryPin"] = True
      externalList.append(e)

  internalList = []
  for event in allInternalEvents:
    status_lower = str(event.get("status", "")).lower().strip()
    to_public = event.get("toPublic") in (True, 1, "true", "1")
    in_window = _is_event_open_for_beneficiary_evaluation(event.get("durationStart"), event.get("durationEnd"), time_now_ms)
    if status_lower not in ["editing", "rejected"] and to_public and in_window:
      pin_val = (event.get("beneficiaryEvaluationPin") or "").strip()
      if not pin_val:
        continue  # every event must have a PIN for beneficiary evaluation; skip if missing
      e = dict(event)
      e.pop("beneficiaryEvaluationPin", None)  # never expose PIN to frontend
      e["eventTypeIndicator"] = "internal"
      e["requiresBeneficiaryPin"] = True
      internalList.append(e)

  return {
    "external": externalList,
    "internal": internalList,
    "message": "Successfully retrieved events eligible for beneficiary evaluation"
  }

def getAnalysis(id: int, eventType: str):
  eventDetails = None
  if (eventType == "external"):
    eventDetails = ExternalEventDb.get(id)

  if (eventType == "internal"):
    eventDetails = InternalEventDb.get(id)

  if (eventDetails == None):
    return ({ "message": "Cannot find event specified" }, 404)

  matchedRequirements = RequirementsDb.getAndSearch(["eventId", "type"], [id, eventType])
  if (len(matchedRequirements) == 0):
    return ({ "message": "No Requirements for the specified event found" }, 406)

  textToAnalyze = []
  for requirement in matchedRequirements:
    matchedEvaluation = EvaluationDb.getAndSearch(["requirementId"], [requirement["id"]])
    if (len(matchedEvaluation) == 0):
      continue

    matchedEvaluation = matchedEvaluation[0]
    textToAnalyze.append(matchedEvaluation["recommendations"])

  analysis = LSICosineSimilarityMatch(textToAnalyze)
  normalized = averageAnalysis(analysis)

  return {
    "analysis": normalized,
    "message": "Successfully returned analysis"
  }

def createExternalEvent():
  import traceback
  try:
    accountSessionInfo = g.get("accountSessionInfo")
    print(f"[CREATE_EXTERNAL_EVENT] Starting event creation for user {accountSessionInfo.get('id')}")

    # Create signatories first
    print("[CREATE_EXTERNAL_EVENT] Creating signatories...")
    try:
      createdSignatories = SignatoriesDb.create(
        approvedBy="NAME",
        preparedBy="NAME",
        recommendingApproval1="NAME",
        recommendingApproval2="NAME",
        reviewedBy="NAME"
      )
      print(f"[CREATE_EXTERNAL_EVENT] Signatories created with ID: {createdSignatories.get('id')}")
    except Exception as e:
      print(f"[CREATE_EXTERNAL_EVENT] ERROR creating signatories: {str(e)}")
      traceback.print_exc()
      return ({
        "message": "Failed to create signatories",
        "error": str(e)
      }, 500)

    # Validate required fields
    required_fields = [
      "extensionServiceType", "title", "location", "durationStart", "durationEnd",
      "sdg", "orgInvolved", "programInvolved", "projectLeader", "partners",
      "beneficiaries", "totalCost", "sourceOfFund", "rationale", "objectives",
      "expectedOutput", "description", "financialPlan", "dutiesOfPartner",
      "evaluationMechanicsPlan", "sustainabilityPlan", "evaluationSendTime"
    ]
    
    missing_fields = [field for field in required_fields if field not in request.json]
    if missing_fields:
      print(f"[CREATE_EXTERNAL_EVENT] Missing required fields: {missing_fields}")
      return ({
        "message": f"Missing required fields: {', '.join(missing_fields)}",
        "missingFields": missing_fields
      }, 400)

    beneficiary_pin_raw = (request.json.get("beneficiaryEvaluationPin") or "").strip()
    ok, beneficiary_pin_result = _validate_beneficiary_pin(beneficiary_pin_raw)
    if not ok:
      return ({"message": beneficiary_pin_result}, 400)
    beneficiary_pin = beneficiary_pin_result

    print("[CREATE_EXTERNAL_EVENT] Creating external event...")
    print(f"[CREATE_EXTERNAL_EVENT] Event data - title: {request.json.get('title')}, location: {request.json.get('location')}")
    
    try:
      createdExternalEvent = ExternalEventDb.create(
        request.json["extensionServiceType"],
        request.json["title"],
        request.json["location"],
        request.json["durationStart"],
        request.json["durationEnd"],
        request.json["sdg"],
        request.json["orgInvolved"],
        request.json["programInvolved"],
        request.json["projectLeader"],
        request.json["partners"],
        request.json["beneficiaries"],
        request.json["totalCost"],
        request.json["sourceOfFund"],
        request.json["rationale"],
        request.json["objectives"],
        request.json["expectedOutput"],
        request.json["description"],
        request.json["financialPlan"],
        request.json["dutiesOfPartner"],
        request.json["evaluationMechanicsPlan"],
        request.json["sustainabilityPlan"],
        accountSessionInfo["id"],
        "editing",
        request.json["evaluationSendTime"],
        signatoriesId=createdSignatories["id"],
        externalServiceType=request.json["externalServiceType"] or "[]",
        eventProposalType=request.json["eventProposalType"] or "[]",
        beneficiaryEvaluationPin=beneficiary_pin
      )
      print(f"[CREATE_EXTERNAL_EVENT] Event created successfully with ID: {createdExternalEvent.get('id')}")
      
      return {
        "data": createdExternalEvent,
        "message": "Successfully created a new external event!"
      }
    except Exception as e:
      print(f"[CREATE_EXTERNAL_EVENT] ERROR creating event: {str(e)}")
      print(f"[CREATE_EXTERNAL_EVENT] Error type: {type(e).__name__}")
      traceback.print_exc()
      return ({
        "message": "Failed to create external event",
        "error": str(e),
        "errorType": type(e).__name__
      }, 500)
      
  except Exception as e:
    print(f"[CREATE_EXTERNAL_EVENT] FATAL ERROR: {str(e)}")
    print(f"[CREATE_EXTERNAL_EVENT] Error type: {type(e).__name__}")
    traceback.print_exc()
    return ({
      "message": "Internal server error while creating event",
      "error": str(e),
      "errorType": type(e).__name__
    }, 500)

def createInternalEvent():
  import traceback
  try:
    accountSessionInfo = g.get("accountSessionInfo")
    print(f"[CREATE_INTERNAL_EVENT] Starting event creation for user {accountSessionInfo.get('id')}")

    # Create signatories first
    print("[CREATE_INTERNAL_EVENT] Creating signatories...")
    try:
      createdSignatories = SignatoriesDb.create(
        approvedBy="NAME",
        preparedBy="NAME",
        recommendingApproval1="NAME",
        recommendingApproval2="NAME",
        reviewedBy="NAME"
      )
      print(f"[CREATE_INTERNAL_EVENT] Signatories created with ID: {createdSignatories.get('id')}")
    except Exception as e:
      print(f"[CREATE_INTERNAL_EVENT] ERROR creating signatories: {str(e)}")
      import traceback
      traceback.print_exc()
      return ({
        "message": "Failed to create signatories",
        "error": str(e)
      }, 500)

    # Validate required fields
    required_fields = [
      "title", "durationStart", "durationEnd", "venue", "modeOfDelivery",
      "projectTeam", "partner", "participant", "maleTotal", "femaleTotal",
      "rationale", "objectives", "description", "workPlan", "financialRequirement",
      "evaluationMechanicsPlan", "sustainabilityPlan", "evaluationSendTime"
    ]
    
    missing_fields = [field for field in required_fields if field not in request.json]
    if missing_fields:
      print(f"[CREATE_INTERNAL_EVENT] Missing required fields: {missing_fields}")
      return ({
        "message": f"Missing required fields: {', '.join(missing_fields)}",
        "missingFields": missing_fields
      }, 400)

    beneficiary_pin_raw = (request.json.get("beneficiaryEvaluationPin") or "").strip()
    ok, beneficiary_pin_result = _validate_beneficiary_pin(beneficiary_pin_raw)
    if not ok:
      return ({"message": beneficiary_pin_result}, 400)
    beneficiary_pin = beneficiary_pin_result

    print("[CREATE_INTERNAL_EVENT] Creating internal event...")
    print(f"[CREATE_INTERNAL_EVENT] Event data - title: {request.json.get('title')}, venue: {request.json.get('venue')}")
    
    try:
      createdInternalEvent = InternalEventDb.create(
        request.json["title"],
        request.json["durationStart"],
        request.json["durationEnd"],
        request.json["venue"],
        request.json["modeOfDelivery"],
        request.json["projectTeam"],
        request.json["partner"],
        request.json["participant"],
        request.json["maleTotal"],
        request.json["femaleTotal"],
        request.json["rationale"],
        request.json["objectives"],
        request.json["description"],
        request.json["workPlan"],
        request.json["financialRequirement"],
        request.json["evaluationMechanicsPlan"],
        request.json["sustainabilityPlan"],
        accountSessionInfo["id"],
        "editing",
        False,
        request.json["evaluationSendTime"],
        createdSignatories["id"],
        eventProposalType=request.json.get("eventProposalType") or "[]",
        beneficiaryEvaluationPin=beneficiary_pin
      )
      print(f"[CREATE_INTERNAL_EVENT] Event created successfully with ID: {createdInternalEvent.get('id')}")
      
      return {
        "data": createdInternalEvent,
        "message": "Successfully created a new internal event!"
      }
    except Exception as e:
      print(f"[CREATE_INTERNAL_EVENT] ERROR creating event: {str(e)}")
      print(f"[CREATE_INTERNAL_EVENT] Error type: {type(e).__name__}")
      traceback.print_exc()
      return ({
        "message": "Failed to create internal event",
        "error": str(e),
        "errorType": type(e).__name__
      }, 500)
      
  except Exception as e:
    print(f"[CREATE_INTERNAL_EVENT] FATAL ERROR: {str(e)}")
    print(f"[CREATE_INTERNAL_EVENT] Error type: {type(e).__name__}")
    traceback.print_exc()
    return ({
      "message": "Internal server error while creating event",
      "error": str(e),
      "errorType": type(e).__name__
    }, 500)

def editExternalEventStatus(id, status: str):
  accountSessionInfo = g.get("accountSessionInfo")
  externalEvent = ExternalEventDb.get(id)

  if (externalEvent == None):
    return ({ "message": "The specified event does not exist" }, 404)

  if (externalEvent["createdBy"] != accountSessionInfo["id"] and status == "submitted"):
    return ({ "message": "You have no permission to submit this event" }, 403)

  update_fields = ["status"]
  update_values = [status]
  # Newly approved events should be visible on homepage/public feeds.
  if str(status).lower().strip() == "accepted":
    update_fields.append("toPublic")
    update_values.append(True)
  ExternalEventDb.updateSpecific(id, update_fields, tuple(update_values))
  updatedData = ExternalEventDb.get(id)
  return {
    "data": updatedData,
    "message": "Event successfully submitted"
  }

def editInternalEventStatus(id, status: str):
  accountSessionInfo = g.get("accountSessionInfo")
  internalEvent = InternalEventDb.get(id)

  if (internalEvent == None):
    return ({ "message": "The specified event does not exist" }, 404)

  if (internalEvent["createdBy"] != accountSessionInfo["id"] and status == "submitted"):
    return ({ "message": "You have no permission to submit this event" }, 403)

  update_fields = ["status"]
  update_values = [status]
  # Newly approved events should be visible on homepage/public feeds.
  if str(status).lower().strip() == "accepted":
    update_fields.append("toPublic")
    update_values.append(True)
  InternalEventDb.updateSpecific(id, update_fields, tuple(update_values))
  updatedData = InternalEventDb.get(id)
  return {
    "data": updatedData,
    "message": "Event successfully submitted"
  }

def makeEventPublic(id, eventType: str):
  accountSessionInfo = g.get("accountSessionInfo")

  # make external event public
  if (eventType == "external"):
    if (ExternalEventDb.get(id) != None):
      ExternalEventDb.updateSpecific(id, ["toPublic"], (True,))
      return { "message": "Successfully made to public" }
    else:
      return ({ "message": "Specified event ID does not exist" }, 404)

  # make internal event public
  if (eventType == "internal"):
    if (InternalEventDb.get(id) != None):
      InternalEventDb.updateSpecific(id, ["toPublic"], (True,))
      return { "message": "Successfully made to public" }
    else:
      return ({ "message": "Specified event ID does not exist" }, 404)

def updateEvent(id, eventType: str):
  accountSessionInfo = g.get("accountSessionInfo")

  if (eventType == "internal"):
      try:
        matchedEvent = InternalEventDb.get(id)
        if (matchedEvent == None): return ({
          "message": "Internal Event provided does not exist"
        }, 404)

        import json
        
        # Ensure workPlan is a string (JSON stringified)
        workPlan = request.json.get("workPlan")
        print(f"[UPDATE_EVENT] workPlan from request: {type(workPlan)}, value: {str(workPlan)[:100] if workPlan else None}")
        if workPlan is None:
          workPlan = matchedEvent.get("workPlan", "{}")
          print(f"[UPDATE_EVENT] workPlan was None, using existing: {str(workPlan)[:100]}")
        elif isinstance(workPlan, dict):
          workPlan = json.dumps(workPlan)
          print(f"[UPDATE_EVENT] workPlan was dict, stringified to: {str(workPlan)[:100]}")
        elif not isinstance(workPlan, str):
          workPlan = json.dumps(workPlan) if workPlan else "{}"
          print(f"[UPDATE_EVENT] workPlan was not string, converted to: {str(workPlan)[:100]}")
        # If it's already a string, use as-is
        print(f"[UPDATE_EVENT] Final workPlan to save: {str(workPlan)[:100]}")

        # Ensure financialRequirement and evaluationMechanicsPlan are strings
        financialRequirement = request.json.get("financialRequirement")
        if financialRequirement is None:
          financialRequirement = matchedEvent.get("financialRequirement", "{}")
        elif isinstance(financialRequirement, dict):
          financialRequirement = json.dumps(financialRequirement)
        elif not isinstance(financialRequirement, str):
          financialRequirement = json.dumps(financialRequirement) if financialRequirement else "{}"

        evaluationMechanicsPlan = request.json.get("evaluationMechanicsPlan")
        if evaluationMechanicsPlan is None:
          evaluationMechanicsPlan = matchedEvent.get("evaluationMechanicsPlan", "{}")
        elif isinstance(evaluationMechanicsPlan, dict):
          evaluationMechanicsPlan = json.dumps(evaluationMechanicsPlan)
        elif not isinstance(evaluationMechanicsPlan, str):
          evaluationMechanicsPlan = json.dumps(evaluationMechanicsPlan) if evaluationMechanicsPlan else "{}"

        # Use request values if provided, otherwise fallback to existing event values
        title = request.json.get("title")
        if title is None:
          title = matchedEvent.get("title", "")
        
        durationStart = request.json.get("durationStart")
        if durationStart is None:
          durationStart = matchedEvent.get("durationStart", 0)
        
        durationEnd = request.json.get("durationEnd")
        if durationEnd is None:
          durationEnd = matchedEvent.get("durationEnd", 0)
        
        venue = request.json.get("venue")
        if venue is None:
          venue = matchedEvent.get("venue", "")
        
        modeOfDelivery = request.json.get("modeOfDelivery")
        if modeOfDelivery is None:
          modeOfDelivery = matchedEvent.get("modeOfDelivery", "")
        
        projectTeam = request.json.get("projectTeam")
        if projectTeam is None:
          projectTeam = matchedEvent.get("projectTeam", "")
        
        partner = request.json.get("partner")
        if partner is None:
          partner = matchedEvent.get("partner", "")
        
        participant = request.json.get("participant")
        if participant is None:
          participant = matchedEvent.get("participant", "")
        
        maleTotal = request.json.get("maleTotal")
        if maleTotal is None:
          maleTotal = matchedEvent.get("maleTotal", "")
        
        femaleTotal = request.json.get("femaleTotal")
        if femaleTotal is None:
          femaleTotal = matchedEvent.get("femaleTotal", "")
        
        rationale = request.json.get("rationale")
        if rationale is None:
          rationale = matchedEvent.get("rationale", "")
        
        objectives = request.json.get("objectives")
        if objectives is None:
          objectives = matchedEvent.get("objectives", "")
        
        description = request.json.get("description")
        if description is None:
          description = matchedEvent.get("description", "")
        
        sustainabilityPlan = request.json.get("sustainabilityPlan")
        if sustainabilityPlan is None:
          sustainabilityPlan = matchedEvent.get("sustainabilityPlan", "")
        
        evaluationSendTime = request.json.get("evaluationSendTime")
        if evaluationSendTime is None:
          evaluationSendTime = matchedEvent.get("evaluationSendTime", 0)
        
        eventProposalType = request.json.get("eventProposalType")
        if eventProposalType is None:
          eventProposalType = matchedEvent.get("eventProposalType", "[]")

        # Convert createdAt to proper format if it's a timestamp (bigint)
        createdAt = matchedEvent.get("createdAt")
        if isinstance(createdAt, (int, float)):
          # Convert timestamp (milliseconds or seconds) to datetime string
          if createdAt > 1e10:  # milliseconds
            createdAt = datetime.fromtimestamp(createdAt / 1000).strftime("%Y-%m-%d %H:%M:%S")
          else:  # seconds
            createdAt = datetime.fromtimestamp(createdAt).strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(createdAt, datetime):
          createdAt = createdAt.strftime("%Y-%m-%d %H:%M:%S")
        elif createdAt is None:
          # Use current time if not set
          createdAt = datetime.now().replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S")

        beneficiary_pin_raw = (request.json.get("beneficiaryEvaluationPin") or matchedEvent.get("beneficiaryEvaluationPin") or "").strip()
        beneficiaryEvaluationPin = _coerce_or_generate_beneficiary_pin(beneficiary_pin_raw)

        print(f"[UPDATE_EVENT] Updating event {id} with workPlan length: {len(str(workPlan))}")
        updatedEvent = InternalEventDb.update(id, (
          title,
          durationStart,
          durationEnd,
          venue,
          modeOfDelivery,
          projectTeam,
          partner,
          participant,
          maleTotal,
          femaleTotal,
          rationale,
          objectives,
          description,
          workPlan,
          financialRequirement,
          evaluationMechanicsPlan,
          sustainabilityPlan,
          accountSessionInfo["id"],
          "editing",
          False,
          evaluationSendTime,
          matchedEvent.get("signatoriesId"),
          createdAt,
          matchedEvent.get("feedback_id"),
          eventProposalType,
          beneficiaryEvaluationPin
        ))
        
        # Verify workPlan was saved
        saved_workPlan = updatedEvent.get("workPlan", "NOT_FOUND")
        print(f"[UPDATE_EVENT] Saved workPlan length: {len(str(saved_workPlan))}, first 100 chars: {str(saved_workPlan)[:100]}")
        
        return {
          "data": updatedEvent,
          "message": "Successfully updated internal event"
        }
      except Exception as e:
        print(f"Error updating internal event: {e}")
        import traceback
        traceback.print_exc()
        return ({
          "message": f"Error updating event: {str(e)}"
        }, 500)

  if (eventType == "external"):
    import json
    matchedEvent = ExternalEventDb.get(id)
    if (matchedEvent == None): return ({
      "message": "External Event provided does not exist"
    }, 404)

    j = request.json if request.json is not None else {}
    ext_beneficiary_pin_raw = (j.get("beneficiaryEvaluationPin") or matchedEvent.get("beneficiaryEvaluationPin") or "").strip()
    ext_beneficiary_pin = _coerce_or_generate_beneficiary_pin(ext_beneficiary_pin_raw)

    def _to_str(v, fallback):
      if v is None:
        return fallback if fallback is not None else ""
      if isinstance(v, (dict, list)):
        try:
          return json.dumps(v)
        except Exception:
          return fallback if fallback is not None else ""
      return str(v) if v != "" else (fallback if fallback is not None else "")

    def _to_float(v, fallback):
      if v is None:
        return float(fallback) if fallback is not None else 0.0
      try:
        return float(v)
      except (TypeError, ValueError):
        return float(fallback) if fallback is not None else 0.0

    def _to_int(v, fallback):
      if v is None:
        return int(fallback) if fallback is not None else 0
      try:
        return int(float(v))
      except (TypeError, ValueError):
        return int(fallback) if fallback is not None else 0

    def _to_timestamp_str(v):
      """Convert createdAt to a string PostgreSQL timestamp (timestamp without time zone) accepts."""
      if v is None:
        return datetime.now().replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
      if isinstance(v, datetime):
        return v.strftime("%Y-%m-%d %H:%M:%S")
      if isinstance(v, (int, float)):
        if v > 1e10:  # milliseconds
          return datetime.fromtimestamp(v / 1000).strftime("%Y-%m-%d %H:%M:%S")
        return datetime.fromtimestamp(v).strftime("%Y-%m-%d %H:%M:%S")
      if isinstance(v, str) and v.strip():
        return v
      return datetime.now().replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S")

    eval_plan = j.get("evaluationMechanicsPlan") if j.get("evaluationMechanicsPlan") is not None else matchedEvent.get("evaluationMechanicsPlan")
    financial_plan = j.get("financialPlan") if j.get("financialPlan") is not None else matchedEvent.get("financialPlan")
    ext_svc = j.get("externalServiceType") if j.get("externalServiceType") is not None else matchedEvent.get("externalServiceType")
    evt_proposal = j.get("eventProposalType") if j.get("eventProposalType") is not None else matchedEvent.get("eventProposalType")

    try:
      duration_start = _to_int(j.get("durationStart"), matchedEvent.get("durationStart"))
      duration_end = _to_int(j.get("durationEnd"), matchedEvent.get("durationEnd"))
      evaluation_send_time = _to_int(j.get("evaluationSendTime"), matchedEvent.get("evaluationSendTime"))
      created_by_id = accountSessionInfo.get("id")
      if created_by_id is None:
        return ({"message": "Session error: missing account id"}, 401)
      try:
        created_by_id = int(created_by_id)
      except (TypeError, ValueError):
        return ({"message": "Session error: invalid account id"}, 401)

      updatedEvent = ExternalEventDb.update(id, (
        j.get("extensionServiceType") or matchedEvent.get("extensionServiceType") or "",
        j.get("title") or matchedEvent.get("title") or "",
        j.get("location") or matchedEvent.get("location") or "",
        duration_start,
        duration_end,
        j.get("sdg") or matchedEvent.get("sdg") or "",
        j.get("orgInvolved") or matchedEvent.get("orgInvolved") or "",
        j.get("programInvolved") or matchedEvent.get("programInvolved") or "",
        j.get("projectLeader") or matchedEvent.get("projectLeader") or "",
        j.get("partners") or matchedEvent.get("partners") or "",
        j.get("beneficiaries") or matchedEvent.get("beneficiaries") or "",
        _to_float(j.get("totalCost"), matchedEvent.get("totalCost")),
        j.get("sourceOfFund") or matchedEvent.get("sourceOfFund") or "",
        j.get("rationale") or matchedEvent.get("rationale") or "",
        j.get("objectives") or matchedEvent.get("objectives") or "",
        j.get("expectedOutput") or matchedEvent.get("expectedOutput") or "",
        j.get("description") or matchedEvent.get("description") or "",
        _to_str(financial_plan, matchedEvent.get("financialPlan")),
        j.get("dutiesOfPartner") or matchedEvent.get("dutiesOfPartner") or "",
        _to_str(eval_plan, matchedEvent.get("evaluationMechanicsPlan")),
        j.get("sustainabilityPlan") or matchedEvent.get("sustainabilityPlan") or "",
        created_by_id,
        "editing",
        evaluation_send_time,
        False,
        matchedEvent.get("signatoriesId"),
        _to_timestamp_str(matchedEvent.get("createdAt")),
        matchedEvent.get("feedback_id"),
        _to_str(ext_svc, matchedEvent.get("externalServiceType") or "[]"),
        _to_str(evt_proposal, matchedEvent.get("eventProposalType") or "[]"),
        ext_beneficiary_pin
      ))
    except Exception as e:
      print(f"[UPDATE_EXTERNAL_EVENT] Error: {e}")
      import traceback
      traceback.print_exc()
      return ({"message": f"Error updating external event: {str(e)}"}, 500)

  return {
    "message": "Successfully updated event",
    "data": updatedEvent
  }

def deleteMyEvents():
  """
  Permanently delete all events created by the currently authenticated user.
  Related records are cleaned up to prevent orphaned rows.
  """
  accountSessionInfo = g.get("accountSessionInfo")
  if not accountSessionInfo:
    return ({"message": "Authentication required. Please log in."}, 403)

  try:
    account_id = int(accountSessionInfo.get("id"))
  except (TypeError, ValueError):
    return ({"message": "Invalid session account information."}, 401)

  conn, cursor = connection.cursorInstance()
  try:
    external_table = table_name_for_query("externalEvents")
    internal_table = table_name_for_query("internalEvents")
    requirements_table = table_name_for_query("requirements")
    evaluation_table = table_name_for_query("evaluation")
    external_report_table = table_name_for_query("externalReport")
    internal_report_table = table_name_for_query("internalReport")
    satisfaction_table = table_name_for_query("satisfactionSurveys")
    assignments_table = table_name_for_query("activity_month_assignments")
    signatories_table = table_name_for_query("eventSignatories")
    feedback_table = table_name_for_query("feedback")

    def _affected_rows():
      rc = cursor.rowcount
      return rc if isinstance(rc, int) and rc >= 0 else 0

    def _in_placeholders(values_count: int):
      return ",".join(["?"] * values_count)

    def _fetch_user_event_rows(table_name: str):
      query = convert_placeholders(
        f"SELECT id, signatoriesid, feedback_id FROM {table_name} WHERE createdby=?"
      )
      cursor.execute(query, (account_id,))
      rows = cursor.fetchall() or []

      event_ids = []
      signatory_ids = []
      feedback_ids = []

      for row in rows:
        if row[0] is not None:
          event_ids.append(int(row[0]))
        if len(row) > 1 and row[1] is not None:
          signatory_ids.append(int(row[1]))
        if len(row) > 2 and row[2] is not None:
          feedback_ids.append(int(row[2]))

      return event_ids, signatory_ids, feedback_ids

    deleted_counts = {
      "externalEvents": 0,
      "internalEvents": 0,
      "externalReports": 0,
      "internalReports": 0,
      "requirements": 0,
      "evaluations": 0,
      "satisfactionSurveys": 0,
      "activityMonthAssignments": 0,
      "eventSignatories": 0,
      "feedback": 0,
    }

    external_event_ids, external_signatory_ids, external_feedback_ids = _fetch_user_event_rows(external_table)
    internal_event_ids, internal_signatory_ids, internal_feedback_ids = _fetch_user_event_rows(internal_table)

    if not external_event_ids and not internal_event_ids:
      conn.close()
      return {
        "message": "No events found for your account.",
        "deleted": deleted_counts,
        "totalEventsDeleted": 0,
      }

    def _delete_event_related_rows(event_ids: list[int], event_type: str):
      if not event_ids:
        return []

      placeholders = _in_placeholders(len(event_ids))

      # Collect linked requirements first so linked evaluations can be removed.
      req_query = convert_placeholders(
        f"SELECT id FROM {requirements_table} WHERE eventid IN ({placeholders}) AND type=?"
      )
      cursor.execute(req_query, tuple(event_ids) + (event_type,))
      requirement_ids = [row[0] for row in (cursor.fetchall() or []) if row and row[0] is not None]

      if requirement_ids:
        req_placeholders = _in_placeholders(len(requirement_ids))
        delete_eval_query = convert_placeholders(
          f"DELETE FROM {evaluation_table} WHERE requirementid IN ({req_placeholders})"
        )
        cursor.execute(delete_eval_query, tuple(requirement_ids))
        deleted_counts["evaluations"] += _affected_rows()

      delete_requirements_query = convert_placeholders(
        f"DELETE FROM {requirements_table} WHERE eventid IN ({placeholders}) AND type=?"
      )
      cursor.execute(delete_requirements_query, tuple(event_ids) + (event_type,))
      deleted_counts["requirements"] += _affected_rows()

      delete_satisfaction_query = convert_placeholders(
        f"DELETE FROM {satisfaction_table} WHERE eventid IN ({placeholders}) AND eventtype=?"
      )
      cursor.execute(delete_satisfaction_query, tuple(event_ids) + (event_type,))
      deleted_counts["satisfactionSurveys"] += _affected_rows()

      return requirement_ids

    _delete_event_related_rows(external_event_ids, "external")
    _delete_event_related_rows(internal_event_ids, "internal")

    if external_event_ids:
      ext_placeholders = _in_placeholders(len(external_event_ids))

      delete_external_reports_query = convert_placeholders(
        f"DELETE FROM {external_report_table} WHERE eventid IN ({ext_placeholders})"
      )
      cursor.execute(delete_external_reports_query, tuple(external_event_ids))
      deleted_counts["externalReports"] += _affected_rows()

      delete_external_events_query = convert_placeholders(
        f"DELETE FROM {external_table} WHERE id IN ({ext_placeholders}) AND createdby=?"
      )
      cursor.execute(delete_external_events_query, tuple(external_event_ids) + (account_id,))
      deleted_counts["externalEvents"] += _affected_rows()

    if internal_event_ids:
      int_placeholders = _in_placeholders(len(internal_event_ids))

      delete_internal_reports_query = convert_placeholders(
        f"DELETE FROM {internal_report_table} WHERE eventid IN ({int_placeholders})"
      )
      cursor.execute(delete_internal_reports_query, tuple(internal_event_ids))
      deleted_counts["internalReports"] += _affected_rows()

      delete_assignments_query = convert_placeholders(
        f"DELETE FROM {assignments_table} WHERE eventid IN ({int_placeholders})"
      )
      cursor.execute(delete_assignments_query, tuple(internal_event_ids))
      deleted_counts["activityMonthAssignments"] += _affected_rows()

      delete_internal_events_query = convert_placeholders(
        f"DELETE FROM {internal_table} WHERE id IN ({int_placeholders}) AND createdby=?"
      )
      cursor.execute(delete_internal_events_query, tuple(internal_event_ids) + (account_id,))
      deleted_counts["internalEvents"] += _affected_rows()

    # Delete signatories only if no remaining event/report row points to them.
    all_signatory_ids = sorted(set(external_signatory_ids + internal_signatory_ids))
    for signatory_id in all_signatory_ids:
      ref_query = convert_placeholders(
        f"""
        SELECT
          (SELECT COUNT(*) FROM {external_table} WHERE signatoriesid=?) +
          (SELECT COUNT(*) FROM {internal_table} WHERE signatoriesid=?) +
          (SELECT COUNT(*) FROM {external_report_table} WHERE signatoriesid=?) +
          (SELECT COUNT(*) FROM {internal_report_table} WHERE signatoriesid=?)
        """
      )
      cursor.execute(ref_query, (signatory_id, signatory_id, signatory_id, signatory_id))
      still_referenced = (cursor.fetchone() or [0])[0]

      if int(still_referenced or 0) == 0:
        delete_signatory_query = convert_placeholders(
          f"DELETE FROM {signatories_table} WHERE id=?"
        )
        cursor.execute(delete_signatory_query, (signatory_id,))
        deleted_counts["eventSignatories"] += _affected_rows()

    # Delete feedback rows only when no event references them anymore.
    all_feedback_ids = sorted(set(external_feedback_ids + internal_feedback_ids))
    for feedback_id in all_feedback_ids:
      feedback_ref_query = convert_placeholders(
        f"""
        SELECT
          (SELECT COUNT(*) FROM {external_table} WHERE feedback_id=?) +
          (SELECT COUNT(*) FROM {internal_table} WHERE feedback_id=?)
        """
      )
      cursor.execute(feedback_ref_query, (feedback_id, feedback_id))
      still_referenced = (cursor.fetchone() or [0])[0]

      if int(still_referenced or 0) == 0:
        delete_feedback_query = convert_placeholders(
          f"DELETE FROM {feedback_table} WHERE id=?"
        )
        cursor.execute(delete_feedback_query, (feedback_id,))
        deleted_counts["feedback"] += _affected_rows()

    conn.commit()

    total_events_deleted = deleted_counts["externalEvents"] + deleted_counts["internalEvents"]
    return {
      "message": "Successfully and permanently deleted your events.",
      "deleted": deleted_counts,
      "totalEventsDeleted": total_events_deleted,
    }
  except Exception as e:
    print(f"Error deleting user events: {e}")
    import traceback
    traceback.print_exc()
    try:
      conn.rollback()
    except Exception:
      pass
    return ({"message": f"Failed to delete your events: {str(e)}"}, 500)
  finally:
    try:
      conn.close()
    except Exception:
      pass

def averageAnalysis(data):
  avg_data = {}
  for key in data:
      for sub_key, value in data[key].items():
          if sub_key not in avg_data:
              avg_data[sub_key] = {"sum": 0, "count": 0}
          avg_data[sub_key]["sum"] += value
          avg_data[sub_key]["count"] += 1

  for sub_key, stats in avg_data.items():
      avg_data[sub_key] = stats["sum"] / stats["count"]

  return avg_data

def normalizeOutput(data):
  total = 0
  data = averageAnalysis(data)
  normalizedValue = {}

  for keys in data:
    total += data[keys]
  for keys in data:
    normalizedValue[keys] = data[keys] / total

  return normalizedValue