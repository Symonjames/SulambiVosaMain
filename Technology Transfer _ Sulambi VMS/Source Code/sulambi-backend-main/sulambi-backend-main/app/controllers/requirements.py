from flask import g, request
from werkzeug.exceptions import BadRequest
from ..models.RequirementsModel import RequirementsModel
from ..models.ExternalEventModel import ExternalEventModel
from ..models.InternalEventModel import InternalEventModel
from ..models.EvaluationModel import EvaluationModel
from ..models.MembershipModel import MembershipModel
from ..models.AccountModel import AccountModel
from ..modules.CallbackTimer import executeDelayedAction
from ..modules.Mailer import threadedHtmlMailer, htmlMailer
from ..database import connection as db_connection

from dotenv import load_dotenv
import os

load_dotenv()

FRONTEND_APP_URL = os.getenv("FRONTEND_APP_URL")

# Map numeric blood donation value to human-readable label for officer/survey display
BLOOD_DONATION_LABELS = {
  0: "I'm eligible to donate.",
  1: "I'm willing to donate.",
  2: "I'm willing but I am not aware if I'm eligible.",
  3: "I'm not willing.",
}

def _blood_donation_label(val):
  if val is None:
    return ""
  if isinstance(val, str) and val.strip() in ("0", "1", "2", "3"):
    return BLOOD_DONATION_LABELS.get(int(val), val)
  if isinstance(val, int):
    return BLOOD_DONATION_LABELS.get(val, str(val))
  return str(val) if val else ""

RequirementsDb = RequirementsModel()
ExternalEventDb = ExternalEventModel()
InternalEventDb = InternalEventModel()
EvaluationDb = EvaluationModel()
MembershipDb = MembershipModel()
AccountDb = AccountModel()

def getMyRequirements():
  """Return current member's requirement event IDs (eventId + type) so frontend can show Joined."""
  accountSessionInfo = g.get("accountSessionInfo")
  if not accountSessionInfo:
    return ({ "message": "Unauthorized" }, 401)
  accountDetails = AccountDb.get(accountSessionInfo["id"])
  if accountDetails is None:
    return ({ "message": "Session expired" }, 403)
  if accountSessionInfo.get("accountType") != "member":
    return ({ "message": "Only members can view their joined events" }, 403)
  membership_id = accountDetails.get("membershipId")
  if not membership_id:
    return ({ "message": "Member profile not found" }, 403)
  user_details = MembershipDb.get(membership_id)
  if not user_details:
    return ({ "message": "Member profile not found" }, 403)
  user_email = (user_details.get("email") or "").strip()
  if not user_email:
    return { "message": "Successfully retrieved my requirements", "data": [] }
  matched = RequirementsDb.getAndSearch(["email"], [user_email])
  data = [{"eventId": r.get("eventId"), "type": r.get("type") or "external"} for r in (matched or [])]
  return { "message": "Successfully retrieved my requirements", "data": data }

def getAllRequirements():
  import time
  start_time = time.time()
  
  try:
    print("[REQUIREMENTS_GET_ALL] ========================================")
    print("[REQUIREMENTS_GET_ALL] Fetching all requirements...")
    
    step_start = time.time()
    # Get all requirements - already sorted by ID DESC in Model.getAll() for requirements table
    requirements = RequirementsDb.getAll()
    
    step_time = time.time() - step_start
    print(f"[REQUIREMENTS_GET_ALL] Retrieved {len(requirements)} requirements from database (sorted by most recent first) ({step_time:.2f}s)")

    # OPTIMIZATION: Batch fetch all events to avoid opening hundreds of database connections
    # Collect all unique event IDs first
    external_event_ids = set()
    internal_event_ids = set()
    
    for requirement in requirements:
      eventType = requirement.get("type", "external")
      eventIdValue = requirement.get("eventId")
      
      if eventIdValue is not None:
        if eventType == "external":
          external_event_ids.add(eventIdValue)
        elif eventType == "internal":
          internal_event_ids.add(eventIdValue)
    
    print(f"[REQUIREMENTS_GET_ALL] Found {len(external_event_ids)} unique external events and {len(internal_event_ids)} unique internal events")
    
    # OPTIMIZATION: Batch fetch only needed events
    step_start = time.time()
    external_events_cache = {}
    if external_event_ids:
      try:
        all_external_events = ExternalEventDb.getAll()
        for event in all_external_events:
          if event and event.get("id") in external_event_ids:
            external_events_cache[event["id"]] = event
        step_time = time.time() - step_start
        print(f"[REQUIREMENTS_GET_ALL] Cached {len(external_events_cache)}/{len(external_event_ids)} external events ({step_time:.2f}s)")
      except Exception as e:
        print(f"[REQUIREMENTS_GET_ALL] Warning: Failed to batch fetch external events: {e}")
    
    # Batch fetch all internal events
    step_start = time.time()
    internal_events_cache = {}
    if internal_event_ids:
      try:
        all_internal_events = InternalEventDb.getAll()
        for event in all_internal_events:
          if event and event.get("id") in internal_event_ids:
            internal_events_cache[event["id"]] = event
        step_time = time.time() - step_start
        print(f"[REQUIREMENTS_GET_ALL] Cached {len(internal_events_cache)}/{len(internal_event_ids)} internal events ({step_time:.2f}s)")
      except Exception as e:
        print(f"[REQUIREMENTS_GET_ALL] Warning: Failed to batch fetch internal events: {e}")

    # OPTIMIZATION: Batch fetch members for backfilling to avoid individual queries
    step_start = time.time()
    emails_to_lookup = set()
    srcodes_to_lookup = set()
    requirements_needing_backfill = []
    
    for index, requirement in enumerate(requirements):
      if not requirement.get("fullname"):
        email = requirement.get("email")
        srcode = requirement.get("srcode")
        if email and str(email).strip():
          emails_to_lookup.add(str(email).strip())
        if srcode and str(srcode).strip():
          srcodes_to_lookup.add(str(srcode).strip())
        requirements_needing_backfill.append(index)
    
    # Batch fetch members by email and srcode
    members_by_email = {}
    members_by_srcode = {}
    
    if emails_to_lookup or srcodes_to_lookup:
      try:
        all_members = MembershipDb.getAll()
        for member in all_members:
          member_email = member.get("email")
          member_srcode = member.get("srcode")
          if member_email and str(member_email).strip() in emails_to_lookup:
            members_by_email[str(member_email).strip()] = member
          if member_srcode and str(member_srcode).strip() in srcodes_to_lookup:
            members_by_srcode[str(member_srcode).strip()] = member
        step_time = time.time() - step_start
        print(f"[REQUIREMENTS_GET_ALL] Cached {len(members_by_email)} members by email, {len(members_by_srcode)} by srcode ({step_time:.2f}s)")
      except Exception as e:
        print(f"[REQUIREMENTS_GET_ALL] Warning: Failed to batch fetch members: {e}")
    
    # Now process requirements using cached events and members (no additional DB connections)
    step_start = time.time()
    for index, requirement in enumerate(requirements):
      # Backfill participant details if missing using cached members
      if index in requirements_needing_backfill:
        try:
          email = requirements[index].get("email")
          srcode = requirements[index].get("srcode")
          
          member = None
          if email and str(email).strip() in members_by_email:
            member = members_by_email[str(email).strip()]
          elif srcode and str(srcode).strip() in members_by_srcode:
            member = members_by_srcode[str(srcode).strip()]
          
          if member:
            requirements[index]["fullname"] = member.get("fullname") or requirements[index].get("fullname")
            requirements[index]["email"] = member.get("email") or requirements[index].get("email")
            requirements[index]["srcode"] = member.get("srcode") or requirements[index].get("srcode")
            requirements[index]["collegeDept"] = member.get("collegeDept") or requirements[index].get("collegeDept")
            requirements[index]["bloodDonation"] = _blood_donation_label(member.get("bloodDonation"))
            requirements[index]["bloodType"] = member.get("bloodType") or ""
        except Exception as e:
          # Non-fatal: still return requirements list
          print("[requirements] Warning: failed to backfill member details:", e)

      eventType = requirements[index].get("type", "external")
      eventIdValue = requirements[index].get("eventId")
      
      if (eventType == "external"):
        matchedEvent = external_events_cache.get(eventIdValue) if eventIdValue is not None else None
        if (matchedEvent == None):
          # If event doesn't exist, provide a placeholder event object
          requirements[index]["eventId"] = {
            "id": eventIdValue,
            "title": "Event Not Found (Deleted or Missing)",
            "status": "unknown"
          }
        else:
          requirements[index]["eventId"] = matchedEvent
      elif (eventType == "internal"):
        matchedEvent = internal_events_cache.get(eventIdValue) if eventIdValue is not None else None
        if (matchedEvent == None):
          # If event doesn't exist, provide a placeholder event object
          requirements[index]["eventId"] = {
            "id": eventIdValue,
            "title": "Event Not Found (Deleted or Missing)",
            "status": "unknown"
          }
        else:
          requirements[index]["eventId"] = matchedEvent
      else:
        # Handle unknown event types - provide placeholder
        requirements[index]["eventId"] = {
          "id": eventIdValue,
          "title": f"Unknown Event Type: {eventType}",
          "status": "unknown"
        }
    
    processing_time = time.time() - step_start
    print(f"[REQUIREMENTS_GET_ALL] Processed {len(requirements)} requirements ({processing_time:.2f}s)")
    
    # Normalize "accepted" to 0/1/null so frontend always gets same shape (avoids
    # PostgreSQL true/false vs SQLite 1/0 or string "1"/"0" mismatch).
    for req in requirements:
      v = req.get("accepted")
      if v is True or v == 1 or v == "1" or (isinstance(v, str) and v.strip().lower() in ("1", "true", "yes")):
        req["accepted"] = 1
      elif v is False or v == 0 or v == "0" or (isinstance(v, str) and v.strip().lower() in ("0", "false", "no")):
        req["accepted"] = 0
      else:
        req["accepted"] = None

    total_time = time.time() - start_time
    print(f"[REQUIREMENTS_GET_ALL] ✅ Successfully processed {len(requirements)} requirements")
    print(f"[REQUIREMENTS_GET_ALL] ⏱️ Total time: {total_time:.2f}s")
    print("[REQUIREMENTS_GET_ALL] ========================================")

    # Prevent caching so the list is always fresh after accept/reject
    headers = {"Cache-Control": "no-store, no-cache, must-revalidate"}
    return (
      {
        "message": "Successfully retrieved all requirements",
        "data": requirements
      },
      200,
      headers
    )
  except Exception as e:
    print(f"[REQUIREMENTS_GET_ALL] ❌ ERROR: {str(e)}")
    import traceback
    print(f"[REQUIREMENTS_GET_ALL] Traceback: {traceback.format_exc()}")
    return ({ "message": f"Server error: {str(e)}" }, 500)

def acceptRequirements(id):
  # id can be string (UUID) or int from URL - requirements table uses string primary key
  id = str(id).strip()
  existence = RequirementsDb.get(id)
  if (existence == None):
    return ({"message": "Requirement ID entered does not exist"}, 404)

  # Update requirement to accepted FIRST so status always persists
  # (mailing is best-effort; missing event must not block accept)
  accepted_db_value = db_connection.convert_boolean_value(True)
  RequirementsDb.updateSpecific(id, ["accepted"], (accepted_db_value,))
  updatedData = RequirementsDb.get(id)

  # Get event details only for mailing (optional)
  if (existence["type"] == "external"):
    eventDetails = ExternalEventDb.get(existence["eventId"])
  else:
    eventDetails = InternalEventDb.get(existence["eventId"])

  if (eventDetails == None):
    print("[REQUIREMENTS_ACCEPT] Warning: No event found for requirement; acceptance saved, mailing skipped")
    return {
      "message": "Successfully accepted requirement",
      "data": updatedData
    }

  # create an evaluation template for user to answer
  EvaluationDb.create(id, "", "", "", "", "", False)

  # Determine when to send evaluation email
  try:
    duration_end_ms = int(eventDetails.get("durationEnd", 0) or 0)
  except (TypeError, ValueError):
    duration_end_ms = 0

  try:
    eval_send_ms = int(eventDetails.get("evaluationSendTime", 0) or 0)
  except (TypeError, ValueError):
    eval_send_ms = 0

  target_epoch_ms = max(duration_end_ms, eval_send_ms)

  if target_epoch_ms <= 0:
    print("[REQUIREMENTS_ACCEPT] Warning: No valid durationEnd/evaluationSendTime; sending evaluation email immediately")
    sendRenderedEvaluationMail(requirementDetails=existence, eventDetails=eventDetails)
  else:
    executeDelayedAction(
      target_epoch_ms,
      lambda: sendRenderedEvaluationMail(requirementDetails=existence, eventDetails=eventDetails),
      execAnyway=False
    )

  sendAcceptedRequirementsMail(existence, eventDetails)

  return {
    "message": "Successfully accepted requirement",
    "data": updatedData
  }

def rejectRequirements(id):
  id = str(id).strip()
  existence = RequirementsDb.get(id)
  if (existence == None):
    return ({"message": "Requirement ID entered does not exist"}, 404)

  rejected_db_value = db_connection.convert_boolean_value(False)
  RequirementsDb.updateSpecific(id, ["accepted"], (rejected_db_value,))
  updatedData = RequirementsDb.get(id)

  if (existence["type"] == "external"):
    eventDetails = ExternalEventDb.get(existence["eventId"])
  else:
    eventDetails = InternalEventDb.get(existence["eventId"])

  if (eventDetails != None):
    sendRejectedRequirementsMail(existence, eventDetails)
  else:
    print("[REQUIREMENTS_REJECT] Warning: No event found; rejection saved, mailing skipped")

  return {
    "message": "Successfully rejected requirement",
    "data": updatedData
  }

def createNewRequirement(eventId: int):
  try:
    print("[REQUIREMENTS_CREATE] ========================================")
    print(f"[REQUIREMENTS_CREATE] Creating requirement for eventId: {eventId}")
    print(f"[REQUIREMENTS_CREATE] Request form keys: {list(request.form.keys())}")
    print(f"[REQUIREMENTS_CREATE] Request files keys: {list(request.files.keys())}")

    # Use Cloudinary for file uploads (validates PDF and images only). Local storage is disabled.
    from app.utils.multipartFileWriter import cloudinaryFileWriter

    try:
      resultingPaths = cloudinaryFileWriter(["medCert", "waiver"], folder="requirements")
      print(f"[REQUIREMENTS_CREATE] ✅ Cloudinary uploads successful")

      medCertUrl = resultingPaths.get("medCert", "")
      waiverUrl = resultingPaths.get("waiver", "")

      if not medCertUrl:
        return ({ "message": "Medical certificate file is required" }, 400)
      if not waiverUrl:
        return ({ "message": "Waiver file is required" }, 400)

      if not medCertUrl.startswith(('http://', 'https://')):
        return ({ "message": "Medical certificate must be uploaded to Cloudinary" }, 400)
      if not waiverUrl.startswith(('http://', 'https://')):
        return ({ "message": "Waiver must be uploaded to Cloudinary" }, 400)

      print(f"[REQUIREMENTS_CREATE] medCert: {medCertUrl[:80]}...")
      print(f"[REQUIREMENTS_CREATE] waiver: {waiverUrl[:80]}...")

    except BadRequest as e:
      print(f"[REQUIREMENTS_CREATE] ❌ BadRequest: {str(e)}")
      return ({ "message": str(e) }, 400)
    except Exception as e:
      error_msg = f"Failed to upload files to Cloudinary: {str(e)}"
      print(f"[REQUIREMENTS_CREATE] ❌ ERROR: {error_msg}")
      return ({ "message": error_msg }, 500)

    medCertUrl = resultingPaths.get("medCert") or ""
    waiverUrl = resultingPaths.get("waiver") or ""
    event_type = request.form.get("type") or "external"

    # Logged-in member: use profile from session/membership; no personal details in form
    account_session = g.get("accountSessionInfo")
    if account_session and account_session.get("accountType") == "member":
      membership_id = account_session.get("membershipId")
      if not membership_id:
        return ({ "message": "Member profile not found. Please contact support." }, 403)
      member_details = MembershipDb.get(membership_id)
      if not member_details:
        return ({ "message": "Member profile not found. Please contact support." }, 403)
      email = (member_details.get("email") or "").strip()
      fullname = (member_details.get("fullname") or "").strip()
      srcode = (member_details.get("srcode") or "").strip()
      age_val = member_details.get("age")
      if age_val is not None and not isinstance(age_val, int):
        try:
          age_val = int(age_val)
        except (TypeError, ValueError):
          age_val = None
      birthday = (member_details.get("birthday") or "").strip()
      sex = (member_details.get("sex") or "").strip()
      campus = (member_details.get("campus") or "").strip()
      collegeDept = (member_details.get("collegeDept") or "").strip()
      yrlevelprogram = (member_details.get("yrlevelprogram") or "").strip()
      address = (member_details.get("address") or "").strip()
      contactNum = (member_details.get("contactNum") or "").strip()
      fblink = (member_details.get("fblink") or "").strip()
      affiliation = (member_details.get("affiliation") or "N/A").strip()
      print(f"[REQUIREMENTS_CREATE] Using member profile for: {email or fullname}")
    else:
      # Public or non-member: require personal details from form
      fullname = (request.form.get("fullname") or "").strip()
      email = (request.form.get("email") or "").strip()
      srcode = (request.form.get("srcode") or "").strip()
      age_str = request.form.get("age") or ""
      age_val = None
      if age_str and age_str.strip():
        try:
          age_val = int(age_str.strip())
        except ValueError:
          age_val = None
      birthday = (request.form.get("birthday") or "").strip()
      sex = (request.form.get("sex") or "").strip()
      campus = (request.form.get("campus") or "").strip()
      collegeDept = (request.form.get("collegeDept") or "").strip()
      yrlevelprogram = (request.form.get("yrlevelprogram") or "").strip()
      address = (request.form.get("address") or "").strip()
      contactNum = (request.form.get("contactNum") or "").strip()
      fblink = (request.form.get("fblink") or "").strip()
      affiliation = (request.form.get("affiliation") or "N/A").strip()

    if not email and not fullname:
      return ({ "message": "Email or full name is required" }, 400)

    # Duplicate check by email
    if email:
      matchedUserRequirement = RequirementsDb.getAndSearch(
        ["eventId", "type", "email"],
        [eventId, event_type, email]
      )
      if len(matchedUserRequirement) > 0:
        print(f"[REQUIREMENTS_CREATE] ❌ Duplicate requirement found for email: {email}")
        return ({ "message": "Your email has already been registered to this event" }, 403)

    print("[REQUIREMENTS_CREATE] Creating requirement in database...")
    print(f"[REQUIREMENTS_CREATE] Saving Cloudinary URLs to database:")
    print(f"  medCert: {medCertUrl[:80]}...")
    print(f"  waiver: {waiverUrl[:80]}...")

    createdRequirement = RequirementsDb.create(
      medCertUrl,
      waiverUrl,
      eventId,
      event_type,
      request.form.get("curriculum") or "",
      request.form.get("destination") or "",
      request.form.get("firstAid") or "",
      request.form.get("fees") or "",
      request.form.get("personnelInCharge") or "",
      request.form.get("personnelRole") or "",
      fullname,
      email,
      srcode,
      age_val,
      birthday,
      sex,
      campus,
      collegeDept,
      yrlevelprogram,
      address,
      contactNum,
      fblink,
      None,
      affiliation
    )

    print(f"[REQUIREMENTS_CREATE] ✅ Requirement created successfully with ID: {createdRequirement.get('id')}")
    print("[REQUIREMENTS_CREATE] ========================================")

    return {
      "message": "Successfully uploaded requirements",
      "data": createdRequirement
    }
  except Exception as e:
    print(f"[REQUIREMENTS_CREATE] ❌ ERROR: {str(e)}")
    import traceback
    print(f"[REQUIREMENTS_CREATE] Traceback: {traceback.format_exc()}")
    return ({ "message": f"Server error: {str(e)}" }, 500)

######################
#  Helper Functions  #
######################
def sendRenderedEvaluationMail(requirementDetails: dict, eventDetails: dict):
  templateHtml = open("templates/evaluation-mail-template.html", "r").read()
  templateHtml = templateHtml.replace("[name]", requirementDetails.get("fullname"))
  templateHtml = templateHtml.replace("[token]", requirementDetails.get("id"))
  templateHtml = templateHtml.replace("[event-title]", eventDetails.get("title"))
  # Build evaluation link safely, even if FRONTEND_APP_URL is not configured
  base_url = FRONTEND_APP_URL or ""
  link = (base_url + "/evaluation/" + str(requirementDetails.get("id"))) if base_url else "/evaluation/" + str(requirementDetails.get("id"))
  templateHtml = templateHtml.replace("[link]", link)
  event_pin = (eventDetails.get("beneficiaryEvaluationPin") or "").strip()
  templateHtml = templateHtml.replace("[event-pin]", event_pin if event_pin else "Not set (beneficiary survey open without PIN)")

  htmlMailer(
    mailTo=requirementDetails.get("email"),
    htmlRendered=templateHtml,
    subject="Evaluation Attendance"
  )

def sendRejectedRequirementsMail(requirementDetails: dict, eventDetails: dict):
  templateHtml = open("templates/we-reject-to-inform-requirements.html", "r").read()
  templateHtml = templateHtml.replace("[name]", requirementDetails.get("fullname"))
  templateHtml = templateHtml.replace("[event]", eventDetails.get("title"))

  threadedHtmlMailer(
    mailTo=requirementDetails.get("email"),
    htmlRendered=templateHtml,
    subject="Requirement Evaluation: Sulambi - VOSA"
  )

def sendAcceptedRequirementsMail(requirementDetails: dict, eventDetails: dict):
  templateHtml = open("templates/we-are-pleased-to-inform-requirements.html", "r").read()
  templateHtml = templateHtml.replace("[name]", requirementDetails.get("fullname") or "")
  templateHtml = templateHtml.replace("[event]", eventDetails.get("title") or "")
  event_pin = (eventDetails.get("beneficiaryEvaluationPin") or "").strip()
  templateHtml = templateHtml.replace("[event-pin]", event_pin if event_pin else "Not set")

  threadedHtmlMailer(
    mailTo=requirementDetails.get("email"),
    htmlRendered=templateHtml,
    subject="Requirement Evaluation: Sulambi - VOSA"
  )
