from flask import request
from ..models.ExternalEventModel import ExternalEventModel
from ..models.InternalEventModel import InternalEventModel
from ..models.MembershipModel import MembershipModel
from ..models.AccountModel import AccountModel
from ..models.RequirementsModel import RequirementsModel
from ..models.EvaluationModel import EvaluationModel
from ..database.connection import convert_boolean_value
from ..database.connection import (
  cursorInstance,
  table_name_for_query,
  convert_placeholders,
  convert_boolean_condition,
  IS_POSTGRESQL,
)

from datetime import datetime

'''
Data needed:
 - total approved events
 - pending events
 - rejected events
 - done events
 - total accounts
 - total pending membership
 - total members
 - total active members
'''

def getSummary():
  try:
    conn, cursor = cursorInstance()
    current_time = int(datetime.now().timestamp()) * 1000

    external_table = table_name_for_query("externalEvents")
    internal_table = table_name_for_query("internalEvents")
    membership_table = table_name_for_query("membership")
    accounts_table = table_name_for_query("accounts")
    duration_end_col = '"durationEnd"' if IS_POSTGRESQL else "durationEnd"

    # Aggregate events from both tables in one pass.
    events_query = f"""
      SELECT
        SUM(CASE WHEN status = 'accepted' THEN 1 ELSE 0 END) AS approved,
        SUM(CASE WHEN status = 'submitted' THEN 1 ELSE 0 END) AS pending,
        SUM(CASE WHEN status NOT IN ('accepted', 'submitted', 'editing') THEN 1 ELSE 0 END) AS rejected,
        SUM(CASE WHEN status = 'accepted' AND {duration_end_col} < ? THEN 1 ELSE 0 END) AS implemented
      FROM (
        SELECT status, {duration_end_col} FROM {external_table}
        UNION ALL
        SELECT status, {duration_end_col} FROM {internal_table}
      ) ev
      WHERE status != 'editing'
    """
    events_query = convert_placeholders(events_query)
    cursor.execute(events_query, (current_time,))
    approved, pending, rejected, implemented = cursor.fetchone() or (0, 0, 0, 0)

    membership_query = f"""
      SELECT
        COUNT(*) AS total_all_members,
        SUM(CASE WHEN accepted = 1 THEN 1 ELSE 0 END) AS total_members,
        SUM(CASE WHEN accepted = 1 AND active = 1 THEN 1 ELSE 0 END) AS total_active_members,
        SUM(CASE WHEN accepted IS NULL OR accepted = '' THEN 1 ELSE 0 END) AS total_pending_members
      FROM {membership_table}
    """
    membership_query = convert_boolean_condition(membership_query)
    cursor.execute(membership_query)
    (
      total_all_members,
      total_members,
      total_active_members,
      total_pending_members,
    ) = cursor.fetchone() or (0, 0, 0, 0)

    cursor.execute(f"SELECT COUNT(*) FROM {accounts_table}")
    total_accounts = (cursor.fetchone() or [0])[0]
    conn.close()
  except Exception:
    # Fallback to model-based path for compatibility across unexpected schemas.
    externalEvents = ExternalEventModel().getAll()
    internalEvents = InternalEventModel().getAll()
    allMembers = MembershipModel().getAll()
    allAccounts = AccountModel().getAll()

    totalApprovedEvents = 0
    pendingEvents = 0
    rejectedEvents = 0
    implementedEvent = 0
    totalMembers = 0
    totalPendingMembers = 0
    totalActiveMembers = 0
    totalAccounts = len(allAccounts)
    currentTime = int(datetime.now().timestamp()) * 1000

    for external in externalEvents:
      if (external["status"] == "editing"):
        continue
      if (external["status"] == "accepted"):
        totalApprovedEvents += 1
      elif (external["status"] == "submitted"):
        pendingEvents += 1
      else:
        rejectedEvents += 1
      if (external["status"] == "accepted" and (external["durationEnd"] - currentTime) < 0):
        implementedEvent += 1

    for internal in internalEvents:
      if (internal["status"] == "editing"):
        continue
      if (internal["status"] == "accepted"):
        totalApprovedEvents += 1
      elif (internal["status"] == "submitted"):
        pendingEvents += 1
      else:
        rejectedEvents += 1
      if (internal["status"] == "accepted" and (internal["durationEnd"] - currentTime) < 0):
        implementedEvent += 1

    totalAllMembers = len(allMembers)
    for member in allMembers:
      accepted = member.get("accepted")
      active = member.get("active")
      if accepted == 1 or accepted == True:
        totalMembers += 1
        if active == 1 or active == True:
          totalActiveMembers += 1
      elif accepted is None or accepted == "":
        totalPendingMembers += 1

    return {
      "data": {
        "totalApprovedEvents": totalApprovedEvents,
        "pendingEvents": pendingEvents,
        "rejectedEvents": rejectedEvents,
        "implementedEvent": implementedEvent,
        "totalMembers": totalMembers,
        "totalPendingMembers": totalPendingMembers,
        "totalActiveMembers": totalActiveMembers,
        "totalAllMembers": totalAllMembers,
        "totalAccounts": totalAccounts
      },
      "message": "Successfully retrieved system summary"
    }

  return {
    "data": {
      "totalApprovedEvents": int(approved or 0),
      "pendingEvents": int(pending or 0),
      "rejectedEvents": int(rejected or 0),
      "implementedEvent": int(implemented or 0),
      "totalMembers": int(total_members or 0),
      "totalPendingMembers": int(total_pending_members or 0),
      "totalActiveMembers": int(total_active_members or 0),
      "totalAllMembers": int(total_all_members or 0),
      "totalAccounts": int(total_accounts or 0)
    },
    "message": "Successfully retrieved system summary"
  }

def getAnalytics():
  ageGroup = {}
  sexGroup = {}
  def _normalize_sex_label(raw_value):
    if raw_value is None:
      return None
    v = str(raw_value).strip().lower()
    if v in ("male", "m", "man", "boy"):
      return "Male"
    if v in ("female", "f", "woman", "girl"):
      return "Female"
    return None

  try:
    conn, cursor = cursorInstance()
    membership_table = table_name_for_query("membership")
    sex_expr = "LOWER(TRIM(sex))"

    age_query = f"""
      SELECT age, COUNT(*)
      FROM {membership_table}
      WHERE accepted = 1
        AND active = 1
        AND age IS NOT NULL
        AND CAST(age AS TEXT) != ''
      GROUP BY age
    """
    age_query = convert_boolean_condition(age_query)
    cursor.execute(age_query)
    for age_value, cnt in cursor.fetchall() or []:
      try:
        age_int = int(float(str(age_value).strip()))
        if age_int > 0:
          ageGroup[str(age_int)] = int(cnt or 0)
      except (TypeError, ValueError):
        continue

    sex_query = f"""
      SELECT {sex_expr} AS sex_norm, COUNT(*)
      FROM {membership_table}
      WHERE accepted = 1
        AND active = 1
        AND sex IS NOT NULL
        AND TRIM(sex) != ''
      GROUP BY {sex_expr}
    """
    sex_query = convert_boolean_condition(sex_query)
    cursor.execute(sex_query)
    for sex_norm, cnt in cursor.fetchall() or []:
      normalized = _normalize_sex_label(sex_norm)
      if normalized:
        sexGroup[normalized] = sexGroup.get(normalized, 0) + int(cnt or 0)
    conn.close()
  except Exception:
    # Fallback to previous model-based iteration
    allMemberships = MembershipModel().getAll()
    for membership in allMemberships:
      accepted = membership.get("accepted")
      active = membership.get("active")
      if accepted is None or accepted == False or accepted == 0:
        continue
      if accepted != 1 and accepted != True:
        continue
      if active is None or active == False or active == 0:
        continue
      if active != 1 and active != True:
        continue

      age_value = membership.get("age")
      if age_value is not None and age_value != "":
        try:
          age_int = int(float(str(age_value).strip()))
          if age_int > 0:
            age_key = str(age_int)
            if age_key not in ageGroup:
              ageGroup[age_key] = 0
            ageGroup[age_key] += 1
        except (ValueError, TypeError):
          pass

      sex_value = membership.get("sex")
      if sex_value is not None and sex_value != "":
        sex_normalized = _normalize_sex_label(sex_value)
        if sex_normalized in ["Male", "Female"]:
          if sex_normalized not in sexGroup:
            sexGroup[sex_normalized] = 0
          sexGroup[sex_normalized] += 1

  return {
    "message": "Successfully retrieved analytics",
    "data": {
      "ageGroup": ageGroup,
      "sexGroup": sexGroup
    },
  }

def getEventInformation(eventId: int, eventType: str):
  try:
    if (eventType == "external"):
      event = ExternalEventModel().get(eventId)
      if not event:
        return ({
          "message": "External event not found"
        }, 404)
    else:
      event = InternalEventModel().get(eventId)
      if not event:
        return ({
          "message": "Internal event not found"
        }, 404)

    conn, cursor = cursorInstance()
    requirements_table = table_name_for_query("requirements")
    evaluation_table = table_name_for_query("evaluation")
    event_id_col = '"eventId"' if IS_POSTGRESQL else "eventId"
    requirement_id_col = '"requirementId"' if IS_POSTGRESQL else "requirementId"

    aggregate_query = f"""
      SELECT
        COUNT(*) AS registered,
        COUNT(DISTINCT CASE
          WHEN e.finalized = 1
           AND COALESCE(TRIM(e.recommendations), '') != ''
          THEN r.id
          ELSE NULL
        END) AS attended
      FROM {requirements_table} r
      LEFT JOIN {evaluation_table} e ON e.{requirement_id_col} = r.id
      WHERE r.{event_id_col} = ?
        AND r.type = ?
        AND r.accepted = 1
    """
    aggregate_query = convert_boolean_condition(aggregate_query)
    aggregate_query = convert_placeholders(aggregate_query)
    cursor.execute(aggregate_query, (eventId, eventType))
    row = cursor.fetchone() or (0, 0)
    registered, answered = int(row[0] or 0), int(row[1] or 0)
    conn.close()

    return {
      "data": {
        "event": event,
        "registered": registered,
        "attended": answered
      },
      "message": "Successfully retrieved event details"
    }
  except Exception as e:
    print(f"Error in getEventInformation: {e}")
    import traceback
    traceback.print_exc()
    return ({
      "message": f"Error retrieving event information: {str(e)}"
    }, 500)

def getActiveMemberData():
  responseSummary = {}
  detailedMembers = []
  current_time_ms = int(datetime.now().timestamp()) * 1000
  ms_per_day = 1000 * 60 * 60 * 24

  try:
    conn, cursor = cursorInstance()
    membership_table = table_name_for_query("membership")
    requirements_table = table_name_for_query("requirements")
    evaluation_table = table_name_for_query("evaluation")
    external_events_table = table_name_for_query("externalEvents")
    internal_events_table = table_name_for_query("internalEvents")
    requirement_id_col = '"requirementId"' if IS_POSTGRESQL else "requirementId"
    event_id_col = '"eventId"' if IS_POSTGRESQL else "eventId"
    duration_end_col = '"durationEnd"' if IS_POSTGRESQL else "durationEnd"

    query = f"""
      SELECT
        m.fullname,
        COUNT(DISTINCT CASE
          WHEN e.finalized = 1
           AND COALESCE(TRIM(e.recommendations), '') != ''
          THEN r.id
          ELSE NULL
        END) AS participation_count,
        MAX(CASE
          WHEN r.type = 'external' THEN ee.{duration_end_col}
          WHEN r.type = 'internal' THEN ie.{duration_end_col}
          ELSE NULL
        END) AS last_event_ms
      FROM {membership_table} m
      INNER JOIN {requirements_table} r
        ON LOWER(TRIM(COALESCE(m.email, ''))) = LOWER(TRIM(COALESCE(r.email, '')))
       AND r.accepted = 1
      LEFT JOIN {evaluation_table} e
        ON e.{requirement_id_col} = r.id
      LEFT JOIN {external_events_table} ee
        ON r.type = 'external' AND ee.id = r.{event_id_col}
      LEFT JOIN {internal_events_table} ie
        ON r.type = 'internal' AND ie.id = r.{event_id_col}
      WHERE m.active = 1
        AND m.accepted = 1
      GROUP BY m.fullname
      HAVING COUNT(DISTINCT r.id) > 0
    """
    query = convert_boolean_condition(query)
    cursor.execute(query)
    rows = cursor.fetchall() or []
    conn.close()

    for fullname, participation_count, last_event_ms in rows:
      count = int(participation_count or 0)
      responseSummary[fullname] = count

      inactivity_days = None
      last_event_iso = None
      if last_event_ms and int(last_event_ms) > 0:
        inactivity_days = int((current_time_ms - int(last_event_ms)) / ms_per_day)
        last_event_iso = datetime.fromtimestamp(int(last_event_ms) / 1000).strftime("%Y-%m-%d")

      detailedMembers.append({
        "name": fullname,
        "participationCount": count,
        "lastEvent": last_event_iso,
        "inactivityDays": inactivity_days if inactivity_days is not None else None
      })
  except Exception:
    # Fallback to the old path if any DB compatibility issue appears.
    active_val = convert_boolean_value(1)
    accepted_val = convert_boolean_value(1)
    activeMembers = MembershipModel().getAndSearch(["active", "accepted"], [active_val, accepted_val])

    for activeMember in activeMembers:
      userEmailIndicator = activeMember["email"]
      userFullname = activeMember["fullname"]
      matchedRequirements = RequirementsModel().getAndSearch(["email", "accepted"], [userEmailIndicator, accepted_val])
      if len(matchedRequirements) == 0:
        continue

      participation_count = 0
      last_event_ms = 0
      for requirement in matchedRequirements:
        matchedEvaluation = EvaluationModel().getAndSearch(["requirementId", "finalized"], [requirement["id"], 1])
        if (len(matchedEvaluation) == 0):
          continue
        matchedEvaluation = matchedEvaluation[0]
        if (matchedEvaluation["recommendations"] != ""):
          participation_count += 1
          try:
            if (requirement["type"] == "external"):
              event = ExternalEventModel().get(requirement["eventId"])
            else:
              event = InternalEventModel().get(requirement["eventId"])
            if event and event.get("durationEnd"):
              last_event_ms = max(last_event_ms, int(event["durationEnd"]))
          except Exception:
            pass

      responseSummary[userFullname] = participation_count
      inactivity_days = None
      last_event_iso = None
      if last_event_ms and last_event_ms > 0:
        inactivity_days = int((current_time_ms - last_event_ms) / ms_per_day)
        last_event_iso = datetime.fromtimestamp(last_event_ms / 1000).strftime("%Y-%m-%d")

      detailedMembers.append({
        "name": userFullname,
        "participationCount": participation_count,
        "lastEvent": last_event_iso,
        "inactivityDays": inactivity_days if inactivity_days is not None else None
      })

  return {
    "data": {
      "summary": responseSummary,
      "members": detailedMembers
    },
    "message": "Successfully retrieved member details for event participation"
  }