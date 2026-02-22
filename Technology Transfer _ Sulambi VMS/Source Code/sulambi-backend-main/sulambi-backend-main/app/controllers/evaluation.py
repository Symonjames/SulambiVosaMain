
from ..models.EvaluationModel import EvaluationModel
from ..models.RequirementsModel import RequirementsModel
from ..models.AccountModel import AccountModel
from ..models.MembershipModel import MembershipModel
from ..models.ExternalEventModel import ExternalEventModel
from ..models.InternalEventModel import InternalEventModel
from flask import request, g

ExternalEventDb = ExternalEventModel()
InternalEventDb = InternalEventModel()
EvaluationDb = EvaluationModel()
RequirementDb = RequirementsModel()
MembershipDb = MembershipModel()
AccountDb = AccountModel()

def getAllEvaluation():
  return {
    "message": "Successfully retrieved all evaluation",
    "data": EvaluationDb.getAll()
  }

def getEvaluationByEvent(eventId: int, eventType: str):
  allEventRequirements = RequirementDb.getAndSearch(["eventId", "type"], [eventId, eventType])
  returnFormat = []

  for requirement in allEventRequirements:
    matchedEvaluation = EvaluationDb.getAndSearch(["requirementId"], [requirement["id"]])
    if (len(matchedEvaluation) == 0):
      continue

    returnFormat.append({
      "requirements": requirement,
      "evaluation": matchedEvaluation[0]
    })

  return {
    "data": returnFormat,
    "message": "Successfully retrieved evaluation data"
  }

def getPersonalEvaluationStatus():
  accountSessionInfo = g.get("accountSessionInfo")
  if not accountSessionInfo:
    return ({ "message": "Not authenticated. Please log in." }, 403)
  accountDetails = AccountDb.get(accountSessionInfo.get("id"))
  if accountDetails is None:
    return ({ "message": "Session expired" }, 403)
  if accountSessionInfo.get("accountType") != "member":
    return ({ "message": "Invalid account type" }, 403)

  membershipId = accountDetails.get("membershipId")
  if not membershipId:
    return { "message": "Successfully retrieved personal evaluation status", "data": [] }
  userDetails = MembershipDb.get(membershipId)
  if not userDetails:
    return { "message": "Successfully retrieved personal evaluation status", "data": [] }
  userEmail = (userDetails.get("email") or "").strip()
  if not userEmail:
    return { "message": "Successfully retrieved personal evaluation status", "data": [] }

  # requirements and evaluation has one-to-one relationship
  matchedReqs = RequirementDb.getOrSearch(["email"], [userEmail])

  formattedResponse = []
  for requirement in matchedReqs:
    evaluation = EvaluationDb.getOrSearch(["requirementId"], [requirement["id"]])
    if (len(evaluation) == 0):
      continue

    # user attendance status
    evaluation = evaluation[0]
    attendanceStatus = "registered"
    if (evaluation["finalized"] == 1 and (evaluation["criteria"] != "")):
      attendanceStatus = "attended"
    if (evaluation["finalized"] == 1 and (evaluation["criteria"] == "" or evaluation["criteria"] == None)):
      attendanceStatus = "not-attended"

    # event details extraction
    if (requirement["type"] == "external"):
      eventData = ExternalEventDb.get(requirement["eventId"])
    else:
      eventData = InternalEventDb.get(requirement["eventId"])

    formattedResponse.append({
      "evaluationId": evaluation["id"],
      "event": eventData,
      "requirement": requirement,
      "eventType": requirement["type"],
      "attendanceStatus": attendanceStatus,
    })
  
  return {
    "message": "Successfully retrieved personal evaluation status",
    "data": formattedResponse
  }

def evaluatable(requirementId):
  matchedRequirement = RequirementDb.get(requirementId)
  if (matchedRequirement == None):
    return False
  if (not matchedRequirement["accepted"]):
    return False

  # check if there's an existing evaluation template for the user
  # Allow access if evaluation exists (whether finalized or not)
  matchedEvaluation = EvaluationDb.getAndSearch(["requirementId"], [requirementId])
  if len(matchedEvaluation) == 0:
    return False
  
  # Only allow submission if not finalized yet
  evaluation = matchedEvaluation[0]
  return evaluation["finalized"] == 0 or evaluation["finalized"] == False

def isEvaluatable(requirementId):
  matchedRequirement = RequirementDb.get(requirementId)
  if (matchedRequirement == None):
    return ({"message": "The requirement ID does not exist"}, 404)
  
  if (not matchedRequirement["accepted"]):
    return ({"message": "Your requirement has not been accepted yet"}, 403)
  
  # Check if evaluation exists
  matchedEvaluation = EvaluationDb.getAndSearch(["requirementId"], [requirementId])
  if len(matchedEvaluation) == 0:
    return ({"message": "No evaluation form available for this requirement"}, 404)
  
  evaluation = matchedEvaluation[0]
  isAlreadySubmitted = evaluation["finalized"] == 1 or evaluation["finalized"] == True
  
  if (evaluatable(requirementId)):
    return {
      "message": "The requirement ID provided is valid",
      "data": RequirementDb.get(requirementId),
      "canSubmit": True,
      "alreadySubmitted": False
    }
  elif isAlreadySubmitted:
    return {
      "message": "Evaluation form has already been submitted",
      "data": RequirementDb.get(requirementId),
      "canSubmit": False,
      "alreadySubmitted": True
    }
  else:
    return ({"message": "The provided requirement is not evaluatable"}, 403)


def evaluateByRequirement(requirementId):
  # condition for already existing evaluation
  if (not evaluatable(requirementId)):
    return ({ "message": "The provided requirement ID cannot be evaluated" }, 403)

  # retrieve evaluation template for the requirement-id
  evaluationTemplates = EvaluationDb.getAndSearch(["requirementId"], [requirementId])
  if (len(evaluationTemplates) == 0):
    return ({ "message": "No evaluation template found for this requirement" }, 404)
  
  evaluationTemplate = evaluationTemplates[0]

  # Get requirement details
  requirement = RequirementDb.get(requirementId)
  if requirement == None:
    return ({ "message": "Requirement not found" }, 404)

  # Single volunteer evaluation endpoint (email link and QR link both use this).
  # Accept and save both rating (criteria) and comment/text fields; no partial validation.
  data = request.get_json(silent=True) or {}
  criteria = data.get("criteria") or {}
  if isinstance(criteria, dict):
    import json
    criteria = json.dumps(criteria)
  q13 = data.get("q13") or ""
  q14 = data.get("q14") or ""
  comment = data.get("comment") or ""
  recommendations = data.get("recommendations") or ""

  EvaluationDb.updateSpecific(evaluationTemplate["id"],
    ["criteria", "q13", "q14", "comment", "recommendations", "finalized"],
    (criteria, q13, q14, comment, recommendations, True)
  )

  # Save to satisfactionSurveys table for analytics
  try:
    from ..database.connection import cursorInstance
    import json
    from datetime import datetime
    
    conn, cursor = cursorInstance()
    
    # Parse criteria to extract ratings
    criteria_data = request.json.get("criteria", {})
    if isinstance(criteria_data, str):
      try:
        criteria_data = json.loads(criteria_data) if criteria_data.startswith('{') else eval(criteria_data)
      except:
        criteria_data = {}
    
    # Map criteria ratings to 1-5 scale
    rating_map = {
      "Excellent": 5,
      "Very Satisfactory": 4,
      "Satisfactory": 3,
      "Fair": 2,
      "Poor": 1
    }
    
    # Extract ratings
    overall_satisfaction = 0
    organization_rating = 0
    communication_rating = 0
    venue_rating = 0
    materials_rating = 0
    support_rating = 0
    
    if isinstance(criteria_data, dict):
      overall_satisfaction = rating_map.get(criteria_data.get('overall', ''), 0)
      organization_rating = rating_map.get(criteria_data.get('appropriateness', ''), 0)
      communication_rating = rating_map.get(criteria_data.get('expectations', ''), 0)
      materials_rating = rating_map.get(criteria_data.get('materials', ''), 0)
      support_rating = rating_map.get(criteria_data.get('session', ''), 0)
    
    # Use q13/q14 as overall if criteria doesn't have it
    q13 = request.json.get("q13", "")
    q14 = request.json.get("q14", "")
    
    if overall_satisfaction == 0:
      if q13:
        try:
          overall_satisfaction = float(q13)
        except:
          pass
      elif q14:
        try:
          overall_satisfaction = float(q14)
        except:
          pass
    
    # Determine respondent type
    respondent_type = "Volunteer"
    if q14 and not q13:
      respondent_type = "Beneficiary"
    elif q13 and q14:
      respondent_type = "Both"
    
    # Convert q13 and q14 to numbers
    volunteer_rating = None
    beneficiary_rating = None
    
    if q13:
      try:
        volunteer_rating = float(q13)
      except:
        pass
    
    if q14:
      try:
        beneficiary_rating = float(q14)
      except:
        pass
    
    # Get event info
    event_id = requirement.get("eventId")
    event_type = requirement.get("type", "internal")
    
    # Get event title
    event_title = ""
    try:
      from ..database.connection import quote_identifier, convert_placeholders
      event_table = "internalEvents" if event_type == "internal" else "externalEvents"
      quoted_table = quote_identifier(event_table)
      query = f"SELECT title FROM {quoted_table} WHERE id = ?"
      query = convert_placeholders(query)
      cursor.execute(query, (event_id,))
      event_row = cursor.fetchone()
      if event_row:
        event_title = event_row[0]
    except:
      pass
    
    # Check if already exists - handle both SQLite and PostgreSQL
    from ..database.connection import DATABASE_URL, quote_identifier, convert_placeholders, convert_boolean_value
    is_postgresql = DATABASE_URL and DATABASE_URL.startswith('postgresql://')
    
    if is_postgresql:
      check_query = """
        SELECT id FROM "satisfactionSurveys" 
        WHERE requirementid = %s AND respondentemail = %s
      """
    else:
      check_query = """
        SELECT id FROM satisfactionSurveys 
        WHERE requirementId = ? AND respondentEmail = ?
      """
    
    cursor.execute(check_query, (requirementId, requirement.get("email", "")))
    
    if not cursor.fetchone():
      # Insert into satisfactionSurveys
      submitted_at = int(datetime.now().timestamp() * 1000)
      
      if is_postgresql:
        # PostgreSQL: Use quoted mixed-case column names to match what analytics.py uses
        # The table has mixed-case columns (eventId, submittedAt as BIGINT, etc.) based on analytics.py queries
        insert_query = """
          INSERT INTO "satisfactionSurveys" (
            "eventId", "eventType", "requirementId", "respondentType", "respondentEmail", "respondentName",
            "overallSatisfaction", "volunteerRating", "beneficiaryRating",
            "organizationRating", "communicationRating", "venueRating", "materialsRating", "supportRating",
            q13, q14, comment, recommendations,
            "wouldRecommend", "areasForImprovement", "positiveAspects",
            "submittedAt", finalized
          ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        finalized_val = convert_boolean_value(True)
        would_recommend_val = convert_boolean_value(overall_satisfaction >= 4 if overall_satisfaction > 0 else None)
      else:
        # SQLite: use unquoted identifiers and ? placeholders
        insert_query = """
          INSERT INTO satisfactionSurveys (
            eventId, eventType, requirementId, respondentType, respondentEmail, respondentName,
            overallSatisfaction, volunteerRating, beneficiaryRating,
            organizationRating, communicationRating, venueRating, materialsRating, supportRating,
            q13, q14, comment, recommendations,
            wouldRecommend, areasForImprovement, positiveAspects,
            submittedAt, finalized
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        finalized_val = True
        would_recommend_val = overall_satisfaction >= 4 if overall_satisfaction > 0 else None
      
      cursor.execute(insert_query, (
        event_id, event_type, requirementId, respondent_type, 
        requirement.get("email", ""), requirement.get("fullname", ""),
        overall_satisfaction, volunteer_rating, beneficiary_rating,
        organization_rating, communication_rating, venue_rating, materials_rating, support_rating,
        q13, q14, request.json.get("comment", ""), request.json.get("recommendations", ""),
        would_recommend_val,
        None,  # Areas for improvement
        request.json.get("comment", "") if overall_satisfaction >= 4 else None,  # Positive aspects
        submitted_at, finalized_val
      ))
      conn.commit()
    
    conn.close()
  except Exception as e:
    # Don't fail the evaluation if satisfaction survey save fails
    print(f"Error saving to satisfactionSurveys: {e}")

  return {
    "message": "Successfully evaluated event",
    "data": EvaluationDb.get(evaluationTemplate["id"])
  }


def _event_ended_within_evaluation_window(duration_end_raw):
  """True if event ended within the last 7 days (evaluation window). duration_end in seconds or ms."""
  from datetime import datetime
  now_ms = int(datetime.now().timestamp() * 1000)
  v = int(duration_end_raw or 0)
  end_ms = v * 1000 if v > 0 and v < 1e12 else v
  if end_ms <= 0:
    return False
  seven_days_ms = 7 * 24 * 60 * 60 * 1000
  return end_ms <= now_ms and end_ms >= (now_ms - seven_days_ms)

def _event_is_eligible_for_evaluation(duration_start_raw, duration_end_raw):
  """True if event is ongoing (started but not ended) OR ended within the last 7 days."""
  from datetime import datetime
  now_ms = int(datetime.now().timestamp() * 1000)
  
  # Check if event is ongoing (started but not ended)
  if duration_start_raw:
    v_start = int(duration_start_raw or 0)
    start_ms = v_start * 1000 if v_start > 0 and v_start < 1e12 else v_start
    if start_ms > 0 and start_ms <= now_ms:
      # Event has started, check if it's still ongoing
      if duration_end_raw:
        v_end = int(duration_end_raw or 0)
        end_ms = v_end * 1000 if v_end > 0 and v_end < 1e12 else v_end
        if end_ms > now_ms:
          # Event is ongoing
          return True
  
  # Check if event ended within 7 days
  return _event_ended_within_evaluation_window(duration_end_raw)


def validateBeneficiaryPin():
  """
  Public endpoint: validate event PIN before showing the survey.
  Expects JSON: eventId (int), eventType ('external'|'internal'), pin (5-digit string).
  Returns 200 with { "valid": true } if PIN matches and event ended within last 7 days, else 400.
  """
  try:
    from ..database.connection import cursorInstance, quote_identifier
    import os
    event_id = request.json.get("eventId")
    event_type = request.json.get("eventType", "external")
    submitted_pin = (request.json.get("pin") or "").strip()

    try:
      if isinstance(event_id, str):
        event_id = int(event_id)
      elif event_id is not None:
        event_id = int(event_id)
      else:
        event_id = None
      if event_id is None or event_id <= 0:
        return {"message": "Invalid event", "success": False, "error": "Event is required."}, 400
    except (ValueError, TypeError):
      return {"message": "Invalid event", "success": False, "error": "Invalid event ID."}, 400

    if len(submitted_pin) != 5 or not submitted_pin.isdigit():
      return {
        "message": "Invalid PIN format",
        "success": False,
        "error": "PIN must be exactly 5 digits."
      }, 400

    DATABASE_URL = os.getenv("DATABASE_URL")
    is_postgresql = DATABASE_URL and DATABASE_URL.startswith("postgresql://")
    event_table = "internalEvents" if event_type == "internal" else "externalEvents"
    quoted_table = quote_identifier(event_table)
    if is_postgresql:
      query = f'SELECT "beneficiaryEvaluationPin", "durationStart", "durationEnd" FROM {quoted_table} WHERE id = %s'
    else:
      query = f"SELECT beneficiaryEvaluationPin, durationStart, durationEnd FROM {quoted_table} WHERE id = ?"
    conn, cursor = cursorInstance()
    cursor.execute(query, (event_id,))
    event_row = cursor.fetchone()
    if not event_row:
      return {"message": "Event not found", "success": False, "error": "Wrong PIN."}, 400
    event_required_pin = (event_row[0] or "").strip() or None
    duration_start = event_row[1] if len(event_row) > 1 else None
    duration_end = event_row[2] if len(event_row) > 2 else None
    if not event_required_pin:
      return {
        "message": "Event not configured",
        "success": False,
        "error": "This event does not have a PIN set. Contact the organizer."
      }, 400
    if not _event_is_eligible_for_evaluation(duration_start, duration_end):
      return {
        "message": "Event no longer open for evaluation",
        "success": False,
        "error": "This event can only be evaluated while it's ongoing or within 7 days after it ended."
      }, 400
    if submitted_pin != event_required_pin:
      return {"message": "Invalid PIN", "success": False, "error": "Wrong PIN."}, 400
    return {"valid": True, "success": True}, 200
  except Exception as e:
    print(f"Error validating beneficiary PIN: {e}")
    import traceback
    traceback.print_exc()
    error_msg = str(e) if str(e) else "Something went wrong. Please try again."
    # Provide more specific error message if possible
    if "connection" in error_msg.lower() or "database" in error_msg.lower():
      error_msg = "Database connection error. Please try again."
    elif "not found" in error_msg.lower():
      error_msg = "Event not found."
    return {"message": "Error validating PIN", "success": False, "error": error_msg}, 500

def submitBeneficiaryEvaluation():
  """
  Submit beneficiary evaluation directly to satisfactionSurveys table
  This allows beneficiaries to submit feedback without a requirementId
  """
  try:
    from ..database.connection import cursorInstance
    import json
    from datetime import datetime
    
    # Get data from request
    event_id = request.json.get("eventId")
    event_type = request.json.get("eventType", "external")
    criteria_data = request.json.get("criteria", {})
    comment = request.json.get("comment", "") or ""
    recommendations = request.json.get("recommendations", "") or ""
    q13 = request.json.get("q13", "") or ""
    q14 = request.json.get("q14", "") or ""
    
    # Validate event_id - PostgreSQL INTEGER range: -2,147,483,648 to 2,147,483,647
    try:
      # Handle both string and int event_id
      if isinstance(event_id, str):
        event_id = int(event_id)
      elif event_id is not None:
        event_id = int(event_id)
      else:
        event_id = None
      
      if event_id is None or event_id <= 0:
        return {
          "message": "Invalid event ID",
          "success": False,
          "error": "eventId is required and must be a positive integer"
        }, 400
      
      # Check if event_id is within PostgreSQL INTEGER range
      INTEGER_MAX = 2147483647
      INTEGER_MIN = -2147483648
      if event_id > INTEGER_MAX or event_id < INTEGER_MIN:
        return {
          "message": "Invalid event ID",
          "success": False,
          "error": f"eventId {event_id} is out of range for PostgreSQL INTEGER type (must be between {INTEGER_MIN} and {INTEGER_MAX})"
        }, 400
    except (ValueError, TypeError) as e:
      return {
        "message": "Invalid event ID",
        "success": False,
        "error": f"eventId must be a valid integer: {str(e)}"
      }, 400
    
    # Beneficiary data
    overall_satisfaction = 0.0
    if isinstance(criteria_data, str):
      try:
        criteria_data = json.loads(criteria_data) if criteria_data.startswith('{') else eval(criteria_data)
      except:
        criteria_data = {}
    
    # Map criteria ratings to 1-5 scale
    rating_map = {
      "Excellent": 5,
      "Very Satisfactory": 4,
      "Satisfactory": 3,
      "Fair": 2,
      "Poor": 1
    }
    
    if isinstance(criteria_data, dict):
      overall_satisfaction = float(rating_map.get(criteria_data.get('overall', ''), 0))
      organization_rating = float(rating_map.get(criteria_data.get('appropriateness', ''), 0))
      communication_rating = float(rating_map.get(criteria_data.get('expectations', ''), 0))
      materials_rating = float(rating_map.get(criteria_data.get('materials', ''), 0))
      support_rating = float(rating_map.get(criteria_data.get('session', ''), 0))
      venue_rating = float(rating_map.get(criteria_data.get('venue', ''), 0))
    else:
      organization_rating = 0.0
      communication_rating = 0.0
      materials_rating = 0.0
      support_rating = 0.0
      venue_rating = 0.0
    
    # Use q14 or calculated overall satisfaction
    if overall_satisfaction == 0.0 and q14:
      try:
        overall_satisfaction = float(q14)
      except (ValueError, TypeError):
        pass
    
    # For beneficiaries, q14 should contain the satisfaction rating
    # If q14 is a number, use it; otherwise use overall_satisfaction
    beneficiary_rating = None
    if q14:
      try:
        beneficiary_rating = float(q14)
        if overall_satisfaction == 0.0:
          overall_satisfaction = beneficiary_rating
      except (ValueError, TypeError):
        pass
    
    if overall_satisfaction == 0.0:
      overall_satisfaction = 0.0
    
    conn, cursor = cursorInstance()
    
    # Verify event exists, get event title and beneficiary PIN requirement
    event_title = ""
    event_required_pin = None
    try:
      from ..database.connection import quote_identifier, convert_placeholders
      import os
      DATABASE_URL = os.getenv("DATABASE_URL")
      is_postgresql = DATABASE_URL and DATABASE_URL.startswith('postgresql://')
      
      event_table = "internalEvents" if event_type == "internal" else "externalEvents"
      quoted_table = quote_identifier(event_table)
      
      if is_postgresql:
        query = f'SELECT title, "beneficiaryEvaluationPin", "durationStart", "durationEnd" FROM {quoted_table} WHERE id = %s'
      else:
        query = f"SELECT title, beneficiaryEvaluationPin, durationStart, durationEnd FROM {quoted_table} WHERE id = ?"

      cursor.execute(query, (event_id,))
      event_row = cursor.fetchone()
      if event_row:
        event_title = event_row[0]
        raw_pin = event_row[1] if len(event_row) > 1 else None
        event_required_pin = (raw_pin or "").strip() or None
        duration_start = event_row[2] if len(event_row) > 2 else None
        duration_end = event_row[3] if len(event_row) > 3 else None
        if not _event_is_eligible_for_evaluation(duration_start, duration_end):
          return {
            "message": "Event no longer open for evaluation",
            "success": False,
            "error": "This event can only be evaluated while it's ongoing or within 7 days after it ended."
          }, 400
      else:
        return {
          "message": "Event not found",
          "success": False,
          "error": "Invalid event ID or event type"
        }, 400
    except Exception as e:
      print(f"Error checking event: {e}")
      import traceback
      traceback.print_exc()
      return {
        "message": "Error verifying event",
        "success": False,
        "error": str(e)
      }, 500

    # Every event has one PIN for beneficiaries; validate it
    if not event_required_pin:
      return {
        "message": "Event not configured for beneficiary evaluation",
        "success": False,
        "error": "This event does not have a beneficiary PIN set. Contact the event organizer."
      }, 400
    submitted_pin = (request.json.get("pin") or "").strip()
    if not submitted_pin:
      return {
        "message": "Event PIN is required",
        "success": False,
        "error": "Please enter the 5-digit event PIN to submit beneficiary feedback."
      }, 400
    if len(submitted_pin) != 5 or not submitted_pin.isdigit():
      return {
        "message": "Invalid PIN format",
        "success": False,
        "error": "Event PIN must be exactly 5 digits (numbers only)."
      }, 400
    if submitted_pin != event_required_pin:
      return {
        "message": "Invalid or missing event PIN",
        "success": False,
        "error": "Please enter the correct event PIN to submit beneficiary feedback."
      }, 400

    # Insert directly into satisfactionSurveys table
    submitted_at = int(datetime.now().timestamp() * 1000)
    
    # Generate a unique requirementId for tracking (using negative ID or UUID)
    import uuid
    requirement_id = str(uuid.uuid4())
    
    # Check if PostgreSQL and use appropriate syntax
    from ..database.connection import DATABASE_URL, quote_identifier, convert_placeholders, convert_boolean_value
    is_postgresql = DATABASE_URL and DATABASE_URL.startswith('postgresql://')
    
    # Get table name with proper quoting
    table_name = quote_identifier('satisfactionSurveys')
    
    if is_postgresql:
      # PostgreSQL: Use lowercase unquoted column names (actual column names from database)
      insert_query = """
        INSERT INTO "satisfactionSurveys" (
          eventid, eventtype, requirementid, respondenttype, respondentemail, respondentname,
          overallsatisfaction, volunteerrating, beneficiaryrating,
          organizationrating, communicationrating, venuerating, materialsrating, supportrating,
          q13, q14, comment, recommendations,
          wouldrecommend, areasforimprovement, positiveaspects,
          submittedat, finalized
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
      """
    else:
      # SQLite: use unquoted identifiers and ? placeholders
      insert_query = f"""
        INSERT INTO {table_name} (
          eventId, eventType, requirementId, respondentType, respondentEmail, respondentName,
          overallSatisfaction, volunteerRating, beneficiaryRating,
          organizationRating, communicationRating, venueRating, materialsRating, supportRating,
          q13, q14, comment, recommendations,
          wouldRecommend, areasForImprovement, positiveAspects,
          submittedAt, finalized
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      """
    
    # Convert boolean for database compatibility - SAME as evaluateByRequirement
    if is_postgresql:
      finalized_val = convert_boolean_value(True)
      would_recommend_val = convert_boolean_value(overall_satisfaction >= 4 if overall_satisfaction > 0 else None)
    else:
      finalized_val = True
      would_recommend_val = overall_satisfaction >= 4 if overall_satisfaction > 0 else None
    
    # Execute INSERT - SAME parameter order as evaluateByRequirement
    try:
      cursor.execute(insert_query, (
        event_id, event_type, requirement_id, "Beneficiary",
        request.json.get("email", "") or "", request.json.get("name", "") or "",
        overall_satisfaction, None, beneficiary_rating,
        organization_rating, communication_rating, venue_rating, materials_rating, support_rating,
        q13, q14, comment, recommendations,
        would_recommend_val,
        None,  # Areas for improvement
        comment if overall_satisfaction >= 4 else None,  # Positive aspects
        submitted_at, finalized_val
      ))
      conn.commit()
      conn.close()
      
      return {
        "message": "Beneficiary evaluation submitted successfully",
        "success": True
      }, 200
    except Exception as db_error:
      conn.rollback()
      conn.close()
      error_msg = str(db_error)
      print(f"Database error submitting beneficiary evaluation: {db_error}")
      import traceback
      traceback.print_exc()
      
      # Provide more specific error message
      param_details = {
        "event_id": event_id,
        "event_id_type": type(event_id).__name__ if event_id is not None else "None",
        "submitted_at": submitted_at,
        "submitted_at_type": type(submitted_at).__name__ if 'submitted_at' in locals() else "unknown",
        "overall_satisfaction": overall_satisfaction_val if 'overall_satisfaction_val' in locals() else "unknown",
        "beneficiary_rating": beneficiary_rating_val if 'beneficiary_rating_val' in locals() else "unknown",
      }
      
      if "integer out of range" in error_msg.lower():
        param_details["event_id_range_check"] = f"INTEGER range: -2147483648 to 2147483647, value: {event_id}"
        param_details["submitted_at_range_check"] = f"BIGINT range: -9223372036854775808 to 9223372036854775807, value: {submitted_at}"
        print(f"[DEBUG] Integer out of range error details: {param_details}")
        
        return {
          "message": f"Database error: {error_msg}",
          "success": False,
          "error": error_msg,
          "details": param_details
        }, 500
      
      return {
        "message": f"Error submitting beneficiary evaluation: {error_msg}",
        "success": False,
        "error": error_msg,
        "details": param_details
      }, 500
    
  except Exception as e:
    print(f"Error submitting beneficiary evaluation: {e}")
    import traceback
    traceback.print_exc()
    return {
      "message": f"Error submitting beneficiary evaluation: {str(e)}",
      "success": False,
      "error": str(e)
    }, 500