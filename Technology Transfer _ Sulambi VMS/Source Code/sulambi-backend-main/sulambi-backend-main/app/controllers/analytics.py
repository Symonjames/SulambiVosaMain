from flask import jsonify
from ..models.InternalEventModel import InternalEventModel
from ..models.ExternalEventModel import ExternalEventModel
from ..models.MembershipModel import MembershipModel
from ..models.EvaluationModel import EvaluationModel
from ..models.FeedbackModel import FeedbackModel
from ..models.SatisfactionSurveyModel import SatisfactionSurveyModel
import random
import math
import json
from datetime import datetime, timedelta
import time
import logging

logger = logging.getLogger(__name__)

def _timestamp_to_datetime(ts):
    """Convert stored timestamp to datetime. Handles both seconds and milliseconds (e.g. event durationStart vs submittedAt)."""
    if ts is None:
        return None
    try:
        val = int(ts)
        # Values >= 1e12 are milliseconds (e.g. 2026-01-01 in ms); smaller values are seconds
        if val >= 1e12:
            return datetime.fromtimestamp(val / 1000.0)
        return datetime.fromtimestamp(val)
    except (ValueError, OSError):
        return None

# Initialize database models
InternalEventDb = InternalEventModel()
ExternalEventDb = ExternalEventModel()
MembershipDb = MembershipModel()
EvaluationDb = EvaluationModel()
FeedbackDb = FeedbackModel()
SatisfactionSurveyDb = SatisfactionSurveyModel()

def getEventSuccessAnalytics():
    """
    Calculate event success rates based on past events
    Returns completion, attendance, and satisfaction metrics
    """
    try:
        # Get all events
        internalEvents = InternalEventDb.getAll()
        externalEvents = ExternalEventDb.getAll()
        
        # Calculate metrics
        totalEvents = len(internalEvents) + len(externalEvents)
        completedEvents = 0
        cancelledEvents = 0
        inProgressEvents = 0
        totalAttendance = 0
        totalSatisfaction = 0
        satisfactionCount = 0
        
        # Process internal events
        for event in internalEvents:
            if event.get('status') == 'completed':
                completedEvents += 1
            elif event.get('status') == 'cancelled':
                cancelledEvents += 1
            else:
                inProgressEvents += 1
            
            # Calculate attendance (mock calculation)
            if event.get('maxParticipants'):
                attendance = random.randint(60, 95)  # Mock attendance percentage
                totalAttendance += attendance
            
            # Get satisfaction from evaluations
            evaluations = EvaluationDb.getAndSearch(['eventId'], [event.get('id')])
            for evaluation in evaluations:
                if evaluation.get('finalized') and evaluation.get('criteria'):
                    try:
                        criteria = eval(evaluation.get('criteria', '{}'))
                        if 'satisfaction' in criteria:
                            totalSatisfaction += criteria['satisfaction']
                            satisfactionCount += 1
                    except:
                        pass
        
        # Process external events
        for event in externalEvents:
            if event.get('status') == 'completed':
                completedEvents += 1
            elif event.get('status') == 'cancelled':
                cancelledEvents += 1
            else:
                inProgressEvents += 1
            
            # Calculate attendance (mock calculation)
            if event.get('maxParticipants'):
                attendance = random.randint(60, 95)  # Mock attendance percentage
                totalAttendance += attendance
            
            # Get satisfaction from evaluations
            evaluations = EvaluationDb.getAndSearch(['eventId'], [event.get('id')])
            for evaluation in evaluations:
                if evaluation.get('finalized') and evaluation.get('criteria'):
                    try:
                        criteria = eval(evaluation.get('criteria', '{}'))
                        if 'satisfaction' in criteria:
                            totalSatisfaction += criteria['satisfaction']
                            satisfactionCount += 1
                    except:
                        pass
        
        # Calculate averages
        averageAttendance = totalAttendance / max(totalEvents, 1)
        averageSatisfaction = totalSatisfaction / max(satisfactionCount, 1) if satisfactionCount > 0 else 4.0
        
        return {
            "success": True,
            "data": {
                "completed": completedEvents,
                "cancelled": cancelledEvents,
                "inProgress": inProgressEvents,
                "totalEvents": totalEvents,
                "averageAttendance": round(averageAttendance, 1),
                "averageSatisfaction": round(averageSatisfaction, 1)
            },
            "message": "Event success analytics retrieved successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve event success analytics"
        }

def getVolunteerDropoutAnalytics(year=None):
    """
    Calculate volunteer dropout risk based on volunteerParticipationHistory table
    - Uses pre-calculated semester-by-semester participation data
    - Tracks most recent participation dates
    - Identifies declining engagement patterns
    """
    try:
        from ..database.connection import cursorInstance
        from datetime import datetime
        
        conn, cursor = cursorInstance()
        
        from ..database.connection import table_name_for_query
        membership_table = table_name_for_query('membership')
        vph_table = table_name_for_query('volunteerParticipationHistory')
        
        # Check if volunteerParticipationHistory table exists (PostgreSQL only)
        from ..database.connection import is_postgresql_connection, DATABASE_URL, is_postgresql_url
        is_postgresql = is_postgresql_url(DATABASE_URL) or is_postgresql_connection(conn)
        
        table_exists = None
        try:
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND lower(table_name) = 'volunteerparticipationhistory'
            """)
            table_exists = cursor.fetchone()
        except Exception as e:
            print(f"[DROPOUT ANALYTICS] Error checking table existence: {e}")
            table_exists = None
        
        # Always ensure we're reading from membership table
        # Check if we have active members in membership table
        from ..database.connection import convert_boolean_condition
        # Match dashboard: approved members; treat NULL active as active (PG/SQLite).
        mem_filter = "(accepted = 1) AND (active = 1 OR active IS NULL)"
        query = f"SELECT COUNT(*) FROM {membership_table} WHERE {mem_filter}"
        query = convert_boolean_condition(query)
        cursor.execute(query)
        member_count = cursor.fetchone()[0] or 0
        
        if member_count == 0:
            conn.close()
            return {
                "success": True,
                "data": {
                    "semesterData": [],
                    "atRiskVolunteers": []
                },
                "message": "No active members found in membership table"
            }
        
        # Get semester data from participation history table (if it exists)
        # Otherwise use legacy method
        if not table_exists:
            conn.close()
            return getVolunteerDropoutAnalyticsLegacy(year)

        # If the table exists but has no rows, the analytics will look empty.
        # In that case, fall back to legacy computation from requirements/evaluation,
        # which directly reflects "joined but didn't answer the form" as dropouts.
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {vph_table}")
            vph_count = cursor.fetchone()[0] or 0
        except Exception:
            vph_count = 0
        if vph_count == 0:
            conn.close()
            return getVolunteerDropoutAnalyticsLegacy(year)
        
        # Get semester data from participation history table
        try:
            from ..database.connection import convert_placeholders
            vph_volunteer_email_col = '"volunteerEmail"' if is_postgresql else 'volunteerEmail'
            vph_events_joined_col = '"eventsJoined"' if is_postgresql else 'eventsJoined'
            vph_events_attended_col = '"eventsAttended"' if is_postgresql else 'eventsAttended'
            vph_events_dropped_col = '"eventsDropped"' if is_postgresql else 'eventsDropped'
            vph_attendance_rate_col = '"attendanceRate"' if is_postgresql else 'attendanceRate'
            vph_semester_year_col = '"semesterYear"' if is_postgresql else 'semesterYear'
            if year:
                query = f"""
                    SELECT semester, 
                           COUNT(DISTINCT {vph_volunteer_email_col}) as total_volunteers,
                           SUM({vph_events_joined_col}) as total_joined,
                           SUM({vph_events_attended_col}) as total_attended,
                           SUM({vph_events_dropped_col}) as total_dropped,
                           AVG({vph_attendance_rate_col}) as avg_attendance_rate
                    FROM {vph_table}
                    WHERE {vph_semester_year_col} = ?
                    GROUP BY semester
                    ORDER BY semester
                """
                query = convert_placeholders(query)
                cursor.execute(query, (int(year),))
            else:
                cursor.execute(f"""
                    SELECT semester, 
                           COUNT(DISTINCT {vph_volunteer_email_col}) as total_volunteers,
                           SUM({vph_events_joined_col}) as total_joined,
                           SUM({vph_events_attended_col}) as total_attended,
                           SUM({vph_events_dropped_col}) as total_dropped,
                           AVG({vph_attendance_rate_col}) as avg_attendance_rate
                    FROM {vph_table}
                    GROUP BY semester
                    ORDER BY semester
                """)
            
            semester_rows = cursor.fetchall()
        except Exception as semester_query_error:
            print(f"[DROPOUT ANALYTICS] Semester query failed: {semester_query_error}")
            print(f"[DROPOUT ANALYTICS] Using empty semester data")
            semester_rows = []
        
        # Format semester data
        semester_data = []
        for row in semester_rows:
            semester, total_volunteers, total_joined, total_attended, total_dropped, avg_attendance_rate = row
            # Calculate average events per volunteer
            events_per_volunteer = round((total_attended / total_volunteers), 1) if total_volunteers > 0 else 0
            
            semester_data.append({
                "semester": semester,
                "events": events_per_volunteer,
                "volunteers": total_volunteers,
                "attended": total_attended,
                "dropouts": total_dropped
            })
        
        # Get at-risk volunteers (those with low attendance or no recent participation)
        current_time_ms = int(datetime.now().timestamp() * 1000)
        ms_per_day = 1000 * 60 * 60 * 24
        
        # First, get all active and accepted members from membership table
        # This ensures we're reading from the membership table as the source of truth
        try:
            from ..database.connection import convert_boolean_condition
            vph_last_event_date_col = 'vph."lastEventDate"' if is_postgresql else 'vph.lastEventDate'
            vph_events_joined_col = 'vph."eventsJoined"' if is_postgresql else 'vph.eventsJoined'
            vph_events_attended_col = 'vph."eventsAttended"' if is_postgresql else 'vph.eventsAttended'
            vph_attendance_rate_col = 'vph."attendanceRate"' if is_postgresql else 'vph.attendanceRate'
            vph_semester_col = 'vph.semester'
            vph_volunteer_email_col = 'vph."volunteerEmail"' if is_postgresql else 'vph.volunteerEmail'

            query = f"""
                SELECT 
                    m.email,
                    m.fullname,
                    COALESCE(MAX({vph_last_event_date_col}), 0) as most_recent_date,
                    COALESCE(SUM({vph_events_joined_col}), 0) as total_joined,
                    COALESCE(SUM({vph_events_attended_col}), 0) as total_attended,
                    COALESCE(AVG({vph_attendance_rate_col}), 0) as avg_attendance_rate,
                    COALESCE(COUNT(DISTINCT {vph_semester_col}), 0) as semesters_active
                FROM {membership_table} m
                LEFT JOIN {vph_table} vph ON m.email = {vph_volunteer_email_col}
                WHERE (m.accepted = 1) AND (m.active = 1 OR m.active IS NULL)
                GROUP BY m.email, m.fullname
            """
            query = convert_boolean_condition(query)
            cursor.execute(query)
            
            volunteer_rows = cursor.fetchall()
        except Exception as query_error:
            # If the JOIN fails (e.g., table doesn't exist or column mismatch), 
            # fall back to getting members without participation history
            print(f"[DROPOUT ANALYTICS] Query with JOIN failed: {query_error}")
            print(f"[DROPOUT ANALYTICS] Falling back to membership-only query")
            from ..database.connection import convert_boolean_condition
            query = f"""
                SELECT 
                    email,
                    fullname,
                    0 as most_recent_date,
                    0 as total_joined,
                    0 as total_attended,
                    0 as avg_attendance_rate,
                    0 as semesters_active
                FROM {membership_table}
                WHERE (accepted = 1) AND (active = 1 OR active IS NULL)
            """
            query = convert_boolean_condition(query)
            cursor.execute(query)
            volunteer_rows = cursor.fetchall()
        
        # Calculate at-risk volunteers from participation history
        at_risk_volunteers = []
        for row in volunteer_rows:
            email, name, most_recent_date, total_joined, total_attended, avg_attendance_rate, semesters_active = row
            
            # Calculate attendance rate
            attendance_rate = float(avg_attendance_rate) if avg_attendance_rate else 0
            
            # Calculate days since last event
            inactivity_days = 0
            most_recent_dt = _timestamp_to_datetime(most_recent_date)
            if most_recent_dt is not None:
                inactivity_days = int((datetime.now().timestamp() - most_recent_dt.timestamp()) / (60 * 60 * 24))
            elif total_joined == 0 and total_attended == 0:
                # If member has never participated, use a high inactivity days value
                # This ensures members with no participation are flagged as high risk
                inactivity_days = 365  # Assume 1 year of inactivity if never participated
            
            # Calculate risk score (0-100)
            risk_score = 0
            
            # High risk for members with no participation at all
            if total_joined == 0 and total_attended == 0:
                risk_score += 50  # Never participated - high risk
            else:
                # Attendance rate factor (0-40 points)
                if attendance_rate < 50:
                    risk_score += 40
                elif attendance_rate < 70:
                    risk_score += 25
                elif attendance_rate < 85:
                    risk_score += 10
                
                # Participation factor (0-20 points)
                # IMPORTANT: If they joined but never submitted a finalized evaluation form,
                # we treat them as high dropout risk (joined but did not "participate" in our system).
                if total_attended == 0 and total_joined > 0:
                    risk_score += 50  # Joined but never attended (no finalized form) - high risk
                elif total_attended < 2:
                    risk_score += 10
            
            # Inactivity factor (0-40 points)
            if inactivity_days > 90:
                risk_score += 40
            elif inactivity_days > 60:
                risk_score += 25
            elif inactivity_days > 30:
                risk_score += 15
            
            # Consistency factor - fewer semesters active = higher risk
            if semesters_active == 1:
                risk_score += 10
            elif semesters_active == 0:
                risk_score += 20  # Never active in any semester
            
            risk_score = min(100, risk_score)
            
            # Only include volunteers with risk score >= 50
            if risk_score >= 50:
                last_event_str = None
                if most_recent_dt is not None:
                    last_event_str = most_recent_dt.strftime('%Y-%m-%d')
                
                at_risk_volunteers.append({
                    "name": name,
                    "inactivityDays": inactivity_days,
                    "lastEvent": last_event_str or "Never",
                    "riskScore": int(risk_score),
                    "joinedEvents": total_joined,
                    "attendedEvents": total_attended,
                    "attendanceRate": round(attendance_rate, 1),
                    "semestersActive": semesters_active
                })
        
        # Sort by risk score (highest first)
        at_risk_volunteers.sort(key=lambda x: x["riskScore"], reverse=True)
        
        conn.close()
        
        return {
            "success": True,
            "data": {
                "semesterData": semester_data,
                "atRiskVolunteers": at_risk_volunteers[:10]  # Top 10 at-risk
            },
            "message": "Volunteer dropout analytics retrieved successfully"
        }
        
    except Exception as e:
        # Ensure connection is closed even on error
        try:
            if 'conn' in locals():
                conn.close()
        except Exception:
            pass
        logger.exception("getVolunteerDropoutAnalytics failed")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve volunteer dropout analytics. Please check if membership table has active members.",
            "data": {"semesterData": [], "atRiskVolunteers": []},
        }

def getVolunteerDropoutAnalyticsLegacy(year=None):
    """
    Legacy method - calculates from requirements/evaluations directly
    Used as fallback if volunteerParticipationHistory table doesn't exist
    """
    try:
        from ..database.connection import cursorInstance
        import math
        from datetime import datetime
        
        conn, cursor = cursorInstance()
        
        # Get all events with their dates to calculate semesters
        from ..database.connection import (
            table_name_for_query,
            DATABASE_URL,
            is_postgresql_url,
            is_postgresql_connection,
        )
        is_pg = bool(is_postgresql_url(DATABASE_URL) or is_postgresql_connection(conn))

        def _pg_dropout_sql(sql: str) -> str:
            """Normalize SQL for PostgreSQL: event tables use lowercase column names (unquoted DDL)."""
            if not is_pg:
                return sql
            s = sql.replace("r.type", 'r."type"')
            s = s.replace('r."eventId"', "r.eventid").replace("r.eventId", "r.eventid")
            s = s.replace('e."requirementId"', "e.requirementid").replace("e.requirementId", "e.requirementid")
            s = s.replace('r."requirementId"', "r.requirementid").replace("r.requirementId", "r.requirementid")
            s = s.replace("ei.durationEnd", "ei.durationend").replace("ee.durationEnd", "ee.durationend")
            s = s.replace("ei.durationStart", "ei.durationstart").replace("ee.durationStart", "ee.durationstart")
            return s

        internal_events_table = table_name_for_query("internalEvents")
        external_events_table = table_name_for_query("externalEvents")
        # internalevents/externalevents columns are lowercase (see tableInitializer / migrations).
        col_ds = "durationstart" if is_pg else "durationStart"
        col_de = "durationend" if is_pg else "durationEnd"
        cursor.execute(f"""
            SELECT id, title, {col_ds}, {col_de}, 'internal' as type
            FROM {internal_events_table}
            WHERE status IN ('accepted', 'completed')
            UNION ALL
            SELECT id, title, {col_ds}, {col_de}, 'external' as type
            FROM {external_events_table}
            WHERE status IN ('accepted', 'completed')
            ORDER BY {col_ds}
        """)
        all_events = cursor.fetchall()
        
        if not all_events:
            conn.close()
            return {
                "success": True,
                "data": {
                    "semesterData": [],
                    "atRiskVolunteers": []
                },
                "message": "No events found"
            }
        
        def _to_ms_timestamp(value):
            """Normalize mixed timestamp formats to milliseconds."""
            if value is None:
                return 0
            if isinstance(value, datetime):
                return int(value.timestamp() * 1000)
            dt = _timestamp_to_datetime(value)
            if dt is not None:
                return int(dt.timestamp() * 1000)
            try:
                numeric = int(value)
                return numeric * 1000 if numeric < 1_000_000_000_000 else numeric
            except Exception:
                return 0

        # Group events by semester
        semester_events = {}
        for event_id, event_title, event_start, event_end, event_type in all_events:
            event_start_ms = _to_ms_timestamp(event_start)
            if event_start_ms > 0:
                event_date = datetime.fromtimestamp(event_start_ms / 1000.0)
                semester_year = event_date.year
                semester_num = math.ceil(event_date.month / 6)  # 1 for Jan-Jun, 2 for Jul-Dec
                semester_key = f"{semester_year}-{semester_num}"
                
                if semester_key not in semester_events:
                    semester_events[semester_key] = []
                semester_events[semester_key].append((event_id, event_type))
        
        # Filter by year if specified
        if year:
            semester_events = {k: v for k, v in semester_events.items() if k.startswith(str(year))}
        
        # Calculate semester engagement data
        semester_data = []
        all_volunteer_stats = {}  # Track per-volunteer stats across all semesters

        # Seed stats from membership so volunteers with zero participation are still included.
        try:
            membership_table = table_name_for_query("membership")
            from ..database.connection import convert_boolean_condition
            members_query = f"""
                SELECT email, fullname
                FROM {membership_table}
                WHERE (accepted = 1) AND (active = 1 OR active IS NULL)
            """
            members_query = convert_boolean_condition(members_query)
            cursor.execute(members_query)
            for email, fullname in cursor.fetchall() or []:
                key = (email or "").strip() or (fullname or "").strip()
                if not key:
                    continue
                if key not in all_volunteer_stats:
                    all_volunteer_stats[key] = {
                        "name": fullname or email or key,
                        "totalJoined": 0,
                        "totalAttended": 0,
                        "lastEventDate": 0,
                    }
        except Exception as seed_err:
            logger.warning("legacy dropout membership seed failed: %s", seed_err)
        
        for semester, events in sorted(semester_events.items()):
            event_ids_internal = [e[0] for e in events if e[1] == 'internal']
            event_ids_external = [e[0] for e in events if e[1] == 'external']
            
            # Count volunteers who JOINED (submitted requirements) for events in this semester.
            # Include accepted OR pending, exclude rejected.
            # Use a robust volunteer key: email -> srcode -> fullname
            from ..database.connection import table_name_for_query
            requirements_table = table_name_for_query('requirements')
            evaluation_table = table_name_for_query('evaluation')
            from ..database.connection import convert_placeholders, convert_boolean_condition
            joined_query = f"""
                SELECT COUNT(DISTINCT COALESCE(NULLIF(r.email, ''), NULLIF(r.srcode, ''), r.fullname)) as joined_count
                FROM {requirements_table} r
                WHERE (r.accepted = 1 OR r.accepted IS NULL)
            """
            joined_params = []
            
            if event_ids_internal and event_ids_external:
                joined_query += " AND ((r.type = 'internal' AND r.\"eventId\" IN ({}) OR (r.type = 'external' AND r.\"eventId\" IN ({}))))".format(
                    ','.join(['?' for _ in event_ids_internal]),
                    ','.join(['?' for _ in event_ids_external])
                )
                joined_params = event_ids_internal + event_ids_external
            elif event_ids_internal:
                joined_query += " AND r.type = 'internal' AND r.\"eventId\" IN ({})".format(','.join(['?' for _ in event_ids_internal]))
                joined_params = event_ids_internal
            elif event_ids_external:
                joined_query += " AND r.type = 'external' AND r.\"eventId\" IN ({})".format(','.join(['?' for _ in event_ids_external]))
                joined_params = event_ids_external
            else:
                continue
            
            joined_query = convert_boolean_condition(joined_query)
            joined_query = convert_placeholders(joined_query)
            joined_query = _pg_dropout_sql(joined_query)
            cursor.execute(joined_query, joined_params)
            joined_count = cursor.fetchone()[0] or 0
            
            # Count volunteers who ATTENDED (participated) in this semester
            from ..database.connection import convert_placeholders, convert_boolean_condition
            attended_query = f"""
                SELECT COUNT(DISTINCT COALESCE(NULLIF(r.email, ''), NULLIF(r.srcode, ''), r.fullname)) as attended_count
                FROM {requirements_table} r
                INNER JOIN {evaluation_table} e ON r.id = e.\"requirementId\"
                WHERE r.accepted = 1 
                AND e.finalized = 1 
                AND e.criteria IS NOT NULL 
                AND e.criteria != ''
            """
            attended_params = []
            
            if event_ids_internal and event_ids_external:
                attended_query += " AND ((r.type = 'internal' AND r.\"eventId\" IN ({}) OR (r.type = 'external' AND r.\"eventId\" IN ({}))))".format(
                    ','.join(['?' for _ in event_ids_internal]),
                    ','.join(['?' for _ in event_ids_external])
                )
                attended_params = event_ids_internal + event_ids_external
            elif event_ids_internal:
                attended_query += " AND r.type = 'internal' AND r.\"eventId\" IN ({})".format(','.join(['?' for _ in event_ids_internal]))
                attended_params = event_ids_internal
            elif event_ids_external:
                attended_query += " AND r.type = 'external' AND r.\"eventId\" IN ({})".format(','.join(['?' for _ in event_ids_external]))
                attended_params = event_ids_external
            
            attended_query = convert_boolean_condition(attended_query)
            attended_query = convert_placeholders(attended_query)
            attended_query = _pg_dropout_sql(attended_query)
            cursor.execute(attended_query, attended_params)
            attended_count = cursor.fetchone()[0] or 0
            
            # Calculate dropouts (joined but didn't attend)
            dropouts = max(0, joined_count - attended_count)
            
            # Calculate average events per volunteer
            events_per_volunteer = 0
            if attended_count > 0:
                from ..database.connection import convert_placeholders, convert_boolean_condition
                total_attendances_query = f"""
                    SELECT COUNT(*) as total_attendances
                    FROM {requirements_table} r
                    INNER JOIN {evaluation_table} e ON r.id = e.\"requirementId\"
                    WHERE r.accepted = 1 
                    AND e.finalized = 1 
                    AND e.criteria IS NOT NULL 
                    AND e.criteria != ''
                """
                total_attendances_params = []
                
                if event_ids_internal and event_ids_external:
                    total_attendances_query += " AND ((r.type = 'internal' AND r.\"eventId\" IN ({}) OR (r.type = 'external' AND r.\"eventId\" IN ({}))))".format(
                        ','.join(['?' for _ in event_ids_internal]),
                        ','.join(['?' for _ in event_ids_external])
                    )
                    total_attendances_params = event_ids_internal + event_ids_external
                elif event_ids_internal:
                    total_attendances_query += " AND r.type = 'internal' AND r.\"eventId\" IN ({})".format(','.join(['?' for _ in event_ids_internal]))
                    total_attendances_params = event_ids_internal
                elif event_ids_external:
                    total_attendances_query += " AND r.type = 'external' AND r.\"eventId\" IN ({})".format(','.join(['?' for _ in event_ids_external]))
                    total_attendances_params = event_ids_external
                
                total_attendances_query = convert_boolean_condition(total_attendances_query)
                total_attendances_query = convert_placeholders(total_attendances_query)
                total_attendances_query = _pg_dropout_sql(total_attendances_query)
                cursor.execute(total_attendances_query, total_attendances_params)
                total_attendances = cursor.fetchone()[0] or 0
                events_per_volunteer = round(total_attendances / attended_count, 1) if attended_count > 0 else 0
            
            semester_data.append({
                "semester": semester,
                "events": events_per_volunteer,
                "volunteers": joined_count,  # Total who joined
                "attended": attended_count,  # Total who attended
                "dropouts": dropouts
            })
            
            # Track individual volunteer stats for at-risk calculation
            from ..database.connection import table_name_for_query, convert_boolean_condition, convert_placeholders
            internal_events_table = table_name_for_query('internalEvents')
            external_events_table = table_name_for_query('externalEvents')
            requirements_table = table_name_for_query('requirements')
            evaluation_table = table_name_for_query('evaluation')
            volunteer_query = f"""
                SELECT
                       COALESCE(NULLIF(r.email, ''), NULLIF(r.srcode, ''), r.fullname) as volunteerKey,
                       MAX(NULLIF(r.email, '')) as email,
                       MAX(NULLIF(r.fullname, '')) as fullname,
                       COUNT(DISTINCT r.id) as joined_events,
                       COUNT(DISTINCT CASE WHEN e.finalized = 1 AND e.criteria IS NOT NULL AND e.criteria != '' THEN r.id END) as attended_events,
                       MAX(CASE 
                           WHEN r.type = 'internal' THEN ei.durationEnd
                           ELSE ee.durationEnd
                       END) as last_event_date
                FROM {requirements_table} r
                LEFT JOIN {evaluation_table} e ON r.id = e.\"requirementId\"
                LEFT JOIN {internal_events_table} ei ON r.\"eventId\" = ei.id AND r.type = 'internal'
                LEFT JOIN {external_events_table} ee ON r.\"eventId\" = ee.id AND r.type = 'external'
                WHERE (r.accepted = 1 OR r.accepted IS NULL)
            """
            volunteer_query = convert_boolean_condition(volunteer_query)
            volunteer_params = []
            
            if event_ids_internal and event_ids_external:
                volunteer_query += " AND ((r.type = 'internal' AND r.\"eventId\" IN ({}) OR (r.type = 'external' AND r.\"eventId\" IN ({}))))".format(
                    ','.join(['?' for _ in event_ids_internal]),
                    ','.join(['?' for _ in event_ids_external])
                )
                volunteer_params = event_ids_internal + event_ids_external
            elif event_ids_internal:
                volunteer_query += " AND r.type = 'internal' AND r.\"eventId\" IN ({})".format(','.join(['?' for _ in event_ids_internal]))
                volunteer_params = event_ids_internal
            elif event_ids_external:
                volunteer_query += " AND r.type = 'external' AND r.\"eventId\" IN ({})".format(','.join(['?' for _ in event_ids_external]))
                volunteer_params = event_ids_external
            
            # PostgreSQL: GROUP BY output alias "volunteerKey" is unreliable; use the same expression as SELECT.
            _vk = "COALESCE(NULLIF(r.email, ''), NULLIF(r.srcode, ''), r.fullname)"
            volunteer_query += f" GROUP BY {_vk}"
            
            from ..database.connection import convert_placeholders
            volunteer_query = convert_placeholders(volunteer_query)
            volunteer_query = _pg_dropout_sql(volunteer_query)
            cursor.execute(volunteer_query, volunteer_params)
            volunteer_rows = cursor.fetchall()
            
            for volunteer_key, email, fullname, joined_events, attended_events, last_event_date in volunteer_rows:
                key = volunteer_key or email or fullname
                if key not in all_volunteer_stats:
                    all_volunteer_stats[key] = {
                        "name": fullname or email or volunteer_key,
                        "totalJoined": 0,
                        "totalAttended": 0,
                        "lastEventDate": 0
                    }
                
                all_volunteer_stats[key]["totalJoined"] += joined_events
                all_volunteer_stats[key]["totalAttended"] += attended_events
                last_event_ms = _to_ms_timestamp(last_event_date)
                if last_event_ms > all_volunteer_stats[key]["lastEventDate"]:
                    all_volunteer_stats[key]["lastEventDate"] = last_event_ms
        
        # Calculate at-risk volunteers (across all semesters)
        current_time_ms = int(datetime.now().timestamp() * 1000)
        ms_per_day = 1000 * 60 * 60 * 24
        
        at_risk_volunteers = []
        for email, stats in all_volunteer_stats.items():
            totalJoined = stats["totalJoined"]
            totalAttended = stats["totalAttended"]
            last_event_date = stats["lastEventDate"]
            
            # Calculate attendance rate
            attendance_rate = (totalAttended / totalJoined * 100) if totalJoined > 0 else 0
            
            # Calculate days since last event
            inactivity_days = 0
            if last_event_date and last_event_date > 0:
                inactivity_days = int((current_time_ms - last_event_date) / ms_per_day)
            
            # Calculate risk score (0-100)
            # Factors: low attendance rate, high inactivity, low total participation
            risk_score = 0
            
            # Attendance rate factor (0-40 points)
            if attendance_rate < 50:
                risk_score += 40
            elif attendance_rate < 70:
                risk_score += 25
            elif attendance_rate < 85:
                risk_score += 10
            
            # Inactivity factor (0-40 points)
            if inactivity_days > 90:
                risk_score += 40
            elif inactivity_days > 60:
                risk_score += 25
            elif inactivity_days > 30:
                risk_score += 15
            
            # Participation factor
            # IMPORTANT: If they joined but never submitted a finalized evaluation form,
            # we treat them as high dropout risk.
            if totalAttended == 0 and totalJoined > 0:
                risk_score += 50  # Joined but never attended (no finalized form) - high risk
            elif totalAttended < 2:
                risk_score += 10
            
            risk_score = min(100, risk_score)
            
            # Only include volunteers with risk score >= 50
            if risk_score >= 50:
                last_event_str = None
                if last_event_date and last_event_date > 0:
                    last_event_str = datetime.fromtimestamp(last_event_date / 1000.0).strftime('%Y-%m-%d')
                
                at_risk_volunteers.append({
                    "name": stats["name"],
                    "inactivityDays": inactivity_days,
                    "lastEvent": last_event_str or "Never",
                    "riskScore": int(risk_score),
                    "joinedEvents": totalJoined,
                    "attendedEvents": totalAttended,
                    "attendanceRate": round(attendance_rate, 1)
                })
        
        # Sort by risk score (highest first)
        at_risk_volunteers.sort(key=lambda x: x["riskScore"], reverse=True)
        
        conn.close()
        
        return {
            "success": True,
            "data": {
                "semesterData": semester_data,
                "atRiskVolunteers": at_risk_volunteers[:10]  # Top 10 at-risk
            },
            "message": "Volunteer dropout analytics retrieved successfully"
        }
        
    except Exception as e:
        try:
            if "conn" in locals():
                conn.close()
        except Exception:
            pass
        logger.exception("getVolunteerDropoutAnalyticsLegacy failed")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve volunteer dropout analytics",
            "data": {"semesterData": [], "atRiskVolunteers": []},
        }

def getPredictiveInsights():
    """
    Generate predictive insights and recommendations
    """
    try:
        # Get basic analytics
        eventSuccess = getEventSuccessAnalytics()
        dropoutRisk = getVolunteerDropoutAnalytics()
        
        insights = []
        recommendations = []
        
        if eventSuccess.get('success'):
            eventData = eventSuccess['data']
            successRate = (eventData['completed'] / max(eventData['totalEvents'], 1)) * 100
            
            if successRate < 70:
                insights.append("Event success rate is below optimal level")
                recommendations.append("Review event planning process and improve pre-event preparation")
            
            if eventData['averageAttendance'] < 75:
                insights.append("Average attendance is lower than expected")
                recommendations.append("Enhance event marketing and engagement strategies")
        
        if dropoutRisk.get('success'):
            dropoutData = dropoutRisk.get("data") or {}
            currentRisk = 0
            if isinstance(dropoutData, list) and dropoutData:
                currentRisk = dropoutData[-1].get("riskLevel", 0) or 0
            elif isinstance(dropoutData, dict):
                semesters = dropoutData.get("semesterData") or []
                if semesters:
                    latest = semesters[-1]
                    vol = latest.get("volunteers") or 0
                    dr = latest.get("dropouts") or 0
                    currentRisk = (dr / vol * 100) if vol else 0
            
            if currentRisk > 30:
                insights.append("High volunteer dropout risk detected")
                recommendations.append("Implement volunteer retention programs and improve engagement")
            elif currentRisk > 20:
                insights.append("Moderate volunteer dropout risk")
                recommendations.append("Monitor volunteer satisfaction and address concerns proactively")
        
        return {
            "success": True,
            "data": {
                "insights": insights,
                "recommendations": recommendations,
                "lastUpdated": datetime.now().isoformat()
            },
            "message": "Predictive insights generated successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate predictive insights"
        }

def getSatisfactionAnalytics(year=None, debug=False):
    """
    Get satisfaction analytics from QR evaluations
    Processes evaluation data to extract satisfaction ratings and trends
    """
    try:
        # Convert various rating representations to numeric (1-5).
        # Production data can store labels ("Excellent") while analytics expects numbers.
        rating_label_map = {
            "excellent": 5.0,
            "very satisfactory": 4.0,
            "very_satisfactory": 4.0,
            "satisfactory": 3.0,
            "fair": 2.0,
            "poor": 1.0,
        }

        def _to_score(val, default=0.0) -> float:
            if val is None:
                return float(default)
            if isinstance(val, (int, float)):
                try:
                    return float(val)
                except Exception:
                    return float(default)
            # Strings: could be numeric "4", or label "Excellent"
            try:
                s = str(val).strip()
            except Exception:
                return float(default)
            if not s:
                return float(default)
            lowered = s.lower().strip()
            if lowered in rating_label_map:
                return float(rating_label_map[lowered])
            # Allow "Very Satisfactory" with extra spaces
            lowered_norm = " ".join(lowered.split())
            if lowered_norm in rating_label_map:
                return float(rating_label_map[lowered_norm])
            try:
                return float(s)
            except Exception:
                return float(default)

        # 0) Prefer pre-aggregated semester_satisfaction first (both all-years and year-specific requests).
        # If no rows are found, fall back to live/raw table computation below.
        try:
            from ..database.connection import cursorInstance
            conn, cursor = cursorInstance()
            from ..database.connection import table_name_for_query
            semester_satisfaction_table = table_name_for_query('semester_satisfaction')
            from ..database.connection import convert_placeholders
            from ..database.connection import DATABASE_URL, is_postgresql_url
            is_postgresql = is_postgresql_url(DATABASE_URL)
            if is_postgresql:
                topIssues_col = '"topIssues"'
            else:
                topIssues_col = 'topIssues'

            if year:
                query = f"""
                    SELECT year, semester, overall, volunteers, beneficiaries, {topIssues_col}
                    FROM {semester_satisfaction_table}
                    WHERE year = ?
                    ORDER BY year ASC, semester ASC
                """
                query = convert_placeholders(query)
                cursor.execute(query, (int(year),))
            else:
                query = f"""
                    SELECT year, semester, overall, volunteers, beneficiaries, {topIssues_col}
                    FROM {semester_satisfaction_table}
                    ORDER BY year ASC, semester ASC
                """
                cursor.execute(query)

            rows = cursor.fetchall()
            conn.close()
            if rows and len(rows) > 0:
                satisfactionData = []
                issues_counter = {}
                for y, sem, ov, vol, ben, topIssues in rows:
                    satisfactionData.append({
                        "semester": f"{y}-{sem}",
                        "score": round(float(ov or 0), 1),
                        "volunteers": round(float(vol or 0), 1),
                        "beneficiaries": round(float(ben or 0), 1),
                    })
                    try:
                        if isinstance(topIssues, str):
                            parsed = eval(topIssues) if topIssues.strip().startswith("[") else []
                        else:
                            parsed = topIssues or []
                        for it in parsed:
                            issues_counter[it.get("issue", "Issue")] = issues_counter.get(it.get("issue", "Issue"), 0) + int(it.get("frequency", 1))
                    except Exception:
                        pass
                overall_avg = sum([item["score"] for item in satisfactionData]) / len(satisfactionData) if satisfactionData else 4.0
                volunteer_avg = sum([item["volunteers"] for item in satisfactionData]) / len(satisfactionData) if satisfactionData else 4.0
                beneficiary_avg = sum([item["beneficiaries"] for item in satisfactionData]) / len(satisfactionData) if satisfactionData else 4.0
                top_issues = [{"issue": k, "frequency": v, "category": "volunteers"} for k, v in sorted(issues_counter.items(), key=lambda x: x[1], reverse=True)[:5]]
                return {
                    "success": True,
                    "data": {
                        "satisfactionData": satisfactionData,
                        "topIssues": top_issues,
                        "averageScore": round(overall_avg, 1),
                        "volunteerScore": round(volunteer_avg, 1),
                        "beneficiaryScore": round(beneficiary_avg, 1),
                        "totalEvaluations": 0,
                        "processedEvaluations": 0,
                        "volunteerCount": 0,
                        "beneficiaryCount": 0,
                        "totalCount": 0
                    },
                    "message": "Satisfaction analytics retrieved from pre-aggregated store"
                }
        except Exception as _:
            pass

        # Read analytics from satisfactionSurveys only (real survey submissions).
        # Legacy evaluation table is intentionally excluded to avoid mixed historical sources.
        from ..database.connection import cursorInstance
        conn, cursor = cursorInstance()
        debug_info = {
            "surveyRowsCount": 0,
            "matchedRowsAfterFilter": 0,
            "eventCount": 0,
            "sampleRows": [],
        }
        
        # Get evaluations with event dates
        from ..database.connection import table_name_for_query
        internal_events_table = table_name_for_query('internalEvents')
        external_events_table = table_name_for_query('externalEvents')
        # Import here to avoid circular imports
        from ..database.connection import DATABASE_URL, is_postgresql_url
        is_postgresql = is_postgresql_url(DATABASE_URL)
        
        # Query: Get submissions from satisfactionSurveys table only.
        # Exclude seeded/demo rows to keep analytics real-data only.
        survey_rows = []
        try:
            satisfaction_surveys_table = table_name_for_query('satisfactionSurveys')
            # Be tolerant to legacy schemas where finalized may be bool/int/text.
            finalized_survey_condition = (
                "LOWER(CAST(ss.finalized AS TEXT)) IN ('1', 'true', 't', 'yes')"
                if is_postgresql
                else "ss.finalized = 1"
            )

            # Read satisfactionSurveys directly (no event-table joins) so analytics remains
            # resilient across PostgreSQL schema variants. We use submittedAt/submittedat
            # as the temporal source for semester/year grouping.
            if is_postgresql:
                pg_survey_queries = [
                    f"""
                        SELECT ss.id, ss.requirementid, ss.respondenttype, ss.overallsatisfaction,
                               ss.volunteerrating, ss.beneficiaryrating, ss.q13, ss.q14, ss.comment, ss.recommendations,
                               ss.eventid, ss.eventtype, ss.submittedat,
                               ss.submittedat as eventdate
                        FROM {satisfaction_surveys_table} ss
                        WHERE {finalized_survey_condition}
                          AND LOWER(COALESCE(ss.respondentemail, '')) NOT LIKE 'seeded_%@example.com'
                    """,
                    f"""
                        SELECT ss.id, ss."requirementId", ss."respondentType", ss."overallSatisfaction",
                               ss."volunteerRating", ss."beneficiaryRating", ss.q13, ss.q14, ss.comment, ss.recommendations,
                               ss."eventId", ss."eventType", ss."submittedAt",
                               ss."submittedAt" as eventdate
                        FROM {satisfaction_surveys_table} ss
                        WHERE {finalized_survey_condition}
                          AND LOWER(COALESCE(ss."respondentEmail", '')) NOT LIKE 'seeded_%@example.com'
                    """,
                ]
                last_pg_error = None
                for survey_query in pg_survey_queries:
                    try:
                        cursor.execute(survey_query)
                        survey_rows = cursor.fetchall()
                        last_pg_error = None
                        break
                    except Exception as pg_err:
                        last_pg_error = pg_err
                        survey_rows = []
                if last_pg_error is not None and not survey_rows:
                    raise last_pg_error
            else:
                survey_query = f"""
                    SELECT ss.id, ss.requirementId, ss.respondentType, ss.overallSatisfaction,
                           ss.volunteerRating, ss.beneficiaryRating, ss.q13, ss.q14, ss.comment, ss.recommendations,
                           ss.eventId, ss.eventType, ss.submittedAt,
                           ss.submittedAt as eventDate
                    FROM {satisfaction_surveys_table} ss
                    WHERE {finalized_survey_condition}
                      AND LOWER(COALESCE(ss.respondentEmail, '')) NOT LIKE 'seeded_%@example.com'
                """
                cursor.execute(survey_query)
                survey_rows = cursor.fetchall()
        except Exception as e:
            # If satisfactionSurveys table doesn't exist or query fails, continue with evaluation_rows only
            print(f"Warning: Could not query satisfactionSurveys table: {e}")
            survey_rows = []
        
        # Build processing rows from survey data only (no legacy evaluation merge).
        combined_rows = []
        debug_info["surveyRowsCount"] = len(survey_rows)
        if survey_rows:
            # Keep only the most relevant fields for temporary diagnostics.
            debug_info["sampleRows"] = [
                {
                    "id": row[0],
                    "respondentType": row[2],
                    "overallSatisfaction": row[3],
                    "eventId": row[10],
                    "eventType": row[11],
                    "submittedAt": row[12],
                }
                for row in survey_rows[:3]
            ]
        for survey_row in survey_rows:
            # Format: (id, requirementId, respondentType, overallSatisfaction, volunteerRating,
            #          beneficiaryRating, q13, q14, comment, recommendations, eventId, eventType, submittedAt, eventDate)
            survey_id, req_id, resp_type, overall, vol_rating, ben_rating, q13, q14, comment, rec, event_id, event_type, submitted_at, event_date = survey_row
            
            # Create criteria-like structure from satisfactionSurveys data
            criteria_obj = {}
            if overall:
                criteria_obj['overall'] = float(overall)
                criteria_obj['satisfaction'] = float(overall)
                criteria_obj['rating'] = float(overall)
            
            # Convert to criteria string format
            criteria_str = json.dumps(criteria_obj) if criteria_obj else '{}'
            
            # For satisfactionSurveys data, set q13/q14 based on respondentType
            # Volunteers use q13 (volunteerRating), Beneficiaries use q14 (beneficiaryRating)
            q13_value = ""
            q14_value = ""
            if resp_type == "Volunteer":
                if vol_rating:
                    q13_value = str(float(vol_rating))
                elif overall:
                    q13_value = str(float(overall))
            elif resp_type == "Beneficiary":
                if ben_rating:
                    q14_value = str(float(ben_rating))
                elif overall:
                    q14_value = str(float(overall))
            else:
                # If both or unknown, try to populate both
                if vol_rating:
                    q13_value = str(float(vol_rating))
                if ben_rating:
                    q14_value = str(float(ben_rating))
            
            # Use submittedAt as event date if event_date is not available
            # This helps with year filtering for predictive data
            use_event_date = event_date if event_date else submitted_at
            
            # Add as a row in the format: (id, requirementId, criteria, finalized, q13, q14, comment, recommendations, eventId, eventType, eventDate)
            combined_rows.append((
                survey_id, req_id, criteria_str, True, 
                q13_value, 
                q14_value,
                comment or "", rec or "", event_id, event_type, use_event_date
            ))
        
        conn.close()
        evaluation_rows = combined_rows
        debug_info["eventCount"] = len(
            {
                (str(r[9]), str(r[10]))
                for r in evaluation_rows
                if len(r) > 10 and r[9] is not None
            }
        )
        
        satisfactionBySemester = {}
        issues = {}
        volunteerSatisfaction = []
        beneficiarySatisfaction = []
        
        for row in evaluation_rows:
            eval_id, req_id, criteria_str, finalized, q13, q14, comment, recommendations, event_id, event_type, event_date = row
            
            if not finalized or not criteria_str:
                continue
                
            try:
                # Parse criteria (handle both string and dict formats)
                criteria = criteria_str
                if isinstance(criteria, str):
                    try:
                        criteria = eval(criteria) if criteria.startswith('{') else json.loads(criteria)
                    except:
                        criteria = {}
                
                # Extract semester from event date or submission date (handles both seconds and milliseconds)
                if event_date:
                    evalDate = _timestamp_to_datetime(event_date) or datetime.now()
                else:
                    evalDate = datetime.now()  # Fallback to current date
                
                # Filter by year if specified - check both semester year and event date year
                if year:
                    year_str = str(year)
                    # Check if year matches the event date year
                    if str(evalDate.year) != year_str:
                        continue
                debug_info["matchedRowsAfterFilter"] += 1
                
                semester = f"{evalDate.year}-{math.ceil(evalDate.month / 6)}"
                
                if semester not in satisfactionBySemester:
                    satisfactionBySemester[semester] = {
                        'volunteers': [],
                        'beneficiaries': [],
                        'overall': []
                    }
                
                # Extract satisfaction scores from criteria
                # Look for various satisfaction indicators
                satisfaction_score = 4.0  # Default score
                
                # Check for overall satisfaction
                if 'overall' in criteria:
                    satisfaction_score = _to_score(criteria.get('overall'), 4.0)
                elif 'satisfaction' in criteria:
                    satisfaction_score = _to_score(criteria.get('satisfaction'), 4.0)
                elif 'rating' in criteria:
                    satisfaction_score = _to_score(criteria.get('rating'), 4.0)
                else:
                    # Calculate average from available ratings
                    rating_keys = ['excellent', 'very_satisfactory', 'satisfactory', 'fair', 'poor']
                    ratings = [criteria.get(key, 0) for key in rating_keys]
                    if any(ratings):
                        # Convert to numeric score (1-5 scale)
                        score_map = {'excellent': 5, 'very_satisfactory': 4, 'satisfactory': 3, 'fair': 2, 'poor': 1}
                        for i, rating in enumerate(ratings):
                            if rating:
                                satisfaction_score = score_map[rating_keys[i]]
                                break
                # Ensure numeric (never string) so aggregation doesn't crash
                satisfaction_score = _to_score(satisfaction_score, 4.0)
                
                # Use q13 and q14 to determine if volunteer or beneficiary
                # q13 = volunteer satisfaction score, q14 = beneficiary satisfaction score
                if q13:
                    try:
                        vol_score = _to_score(q13, satisfaction_score)
                        satisfactionBySemester[semester]['volunteers'].append(vol_score)
                        volunteerSatisfaction.append(vol_score)
                        satisfactionBySemester[semester]['overall'].append(vol_score)
                    except:
                        satisfactionBySemester[semester]['volunteers'].append(satisfaction_score)
                        volunteerSatisfaction.append(satisfaction_score)
                        satisfactionBySemester[semester]['overall'].append(satisfaction_score)
                
                if q14:
                    try:
                        ben_score = _to_score(q14, satisfaction_score)
                        satisfactionBySemester[semester]['beneficiaries'].append(ben_score)
                        beneficiarySatisfaction.append(ben_score)
                        satisfactionBySemester[semester]['overall'].append(ben_score)
                    except:
                        satisfactionBySemester[semester]['beneficiaries'].append(satisfaction_score)
                        beneficiarySatisfaction.append(satisfaction_score)
                        satisfactionBySemester[semester]['overall'].append(satisfaction_score)
                
                # If neither q13 nor q14, assume volunteer (default)
                if not q13 and not q14:
                    satisfactionBySemester[semester]['volunteers'].append(satisfaction_score)
                    volunteerSatisfaction.append(satisfaction_score)
                    satisfactionBySemester[semester]['overall'].append(satisfaction_score)
                
                # Extract issues from comments
                eval_comment = comment or criteria.get('comment', '') or criteria.get('comments', '') or ''
                if eval_comment:
                    common_issues = [
                        'communication', 'resource', 'scheduling', 'training', 'support',
                        'accessibility', 'organization', 'time', 'venue', 'materials',
                        'follow-up', 'feedback', 'coordination', 'preparation'
                    ]
                    
                    for issue in common_issues:
                        if issue.lower() in eval_comment.lower():
                            issues[issue] = issues.get(issue, 0) + 1
                            
            except Exception as e:
                print(f"Error processing evaluation {eval_id}: {e}")
                continue
        
        # Calculate semester averages - only include scores when there's actual data
        satisfactionData = []
        for semester, data in satisfactionBySemester.items():
            if data['overall']:
                overall_avg = sum(data['overall']) / len(data['overall'])
                # Only calculate volunteer average if there are actual volunteer ratings
                volunteer_avg = sum(data['volunteers']) / len(data['volunteers']) if data['volunteers'] else None
                # Only calculate beneficiary average if there are actual beneficiary ratings
                beneficiary_avg = sum(data['beneficiaries']) / len(data['beneficiaries']) if data['beneficiaries'] else None
                
                satisfactionData.append({
                    'semester': semester,
                    'score': round(overall_avg, 1),
                    'volunteers': round(volunteer_avg, 1) if volunteer_avg is not None else None,
                    'beneficiaries': round(beneficiary_avg, 1) if beneficiary_avg is not None else None
                })
        
        # Sort by semester
        satisfactionData.sort(key=lambda x: x['semester'])
        
        # Calculate overall averages - only when there's actual data
        overall_avg = sum([item['score'] for item in satisfactionData]) / len(satisfactionData) if satisfactionData else 0
        # Only calculate averages when there are actual ratings (return 0 when no ratings, not 4.0)
        volunteer_avg = sum(volunteerSatisfaction) / len(volunteerSatisfaction) if volunteerSatisfaction else 0
        beneficiary_avg = sum(beneficiarySatisfaction) / len(beneficiarySatisfaction) if beneficiarySatisfaction else 0
        
        # Format top issues
        top_issues = []
        for issue, frequency in sorted(issues.items(), key=lambda x: x[1], reverse=True)[:5]:
            top_issues.append({
                'issue': issue.replace('_', ' ').title() + ' Issues',
                'frequency': frequency,
                'category': 'volunteers' if random.random() > 0.5 else 'beneficiaries'  # Random assignment for demo
            })
        
        response_payload = {
            "success": True,
            "data": {
                "satisfactionData": satisfactionData,
                "topIssues": top_issues,
                "averageScore": round(overall_avg, 1),
                "volunteerScore": round(volunteer_avg, 1),
                "beneficiaryScore": round(beneficiary_avg, 1),
                "totalEvaluations": len(evaluation_rows),
                "processedEvaluations": len(evaluation_rows),
                "volunteerCount": len(volunteerSatisfaction),
                "beneficiaryCount": len(beneficiarySatisfaction),
                "totalCount": len(volunteerSatisfaction) + len(beneficiarySatisfaction)
            },
            "message": "Satisfaction analytics retrieved successfully"
        }
        if debug:
            response_payload["debug"] = debug_info
        return response_payload
        
    except Exception as e:
        print(f"[SATISFACTION_ANALYTICS] Error (returning empty data): {e}")
        # Return 200 with empty data so dashboard does not see 500; frontend can show empty state.
        error_payload = {
            "success": True,
            "data": {
                "satisfactionData": [],
                "topIssues": [],
                "averageScore": 0,
                "volunteerScore": 0,
                "beneficiaryScore": 0,
                "totalEvaluations": 0,
                "processedEvaluations": 0,
                "volunteerCount": 0,
                "beneficiaryCount": 0,
                "totalCount": 0
            },
            "message": "No satisfaction data available"
        }
        if debug:
            error_payload["debug"] = {
                "error": str(e),
                "surveyRowsCount": 0,
                "matchedRowsAfterFilter": 0,
                "eventCount": 0,
                "sampleRows": [],
            }
        return error_payload

def getEventSatisfactionAnalytics(eventId: int, eventType: str):
    """
    Get satisfaction analytics for a specific event
    Returns volunteer and beneficiary ratings separately
    """
    try:
        rating_label_map = {
            "excellent": 5.0,
            "very satisfactory": 4.0,
            "very_satisfactory": 4.0,
            "satisfactory": 3.0,
            "fair": 2.0,
            "poor": 1.0,
        }

        def _to_score(val, default=0.0) -> float:
            if val is None:
                return float(default)
            if isinstance(val, (int, float)):
                try:
                    return float(val)
                except Exception:
                    return float(default)
            try:
                s = str(val).strip()
            except Exception:
                return float(default)
            if not s:
                return float(default)
            lowered = s.lower().strip()
            if lowered in rating_label_map:
                return float(rating_label_map[lowered])
            lowered_norm = " ".join(lowered.split())
            if lowered_norm in rating_label_map:
                return float(rating_label_map[lowered_norm])
            try:
                return float(s)
            except Exception:
                return float(default)

        from ..database.connection import cursorInstance
        conn, cursor = cursorInstance()
        
        # Get event title
        from ..database.connection import table_name_for_query, convert_placeholders, DATABASE_URL, is_postgresql_url
        is_pg = is_postgresql_url(DATABASE_URL)
        event_table = "internalEvents" if eventType == "internal" else "externalEvents"
        quoted_table = table_name_for_query(event_table)
        if is_pg:
            query = f'SELECT title, "durationStart", "durationEnd" FROM {quoted_table} WHERE id = %s'
        else:
            query = f"SELECT title, durationStart, durationEnd FROM {quoted_table} WHERE id = ?"
        query = convert_placeholders(query) if not is_pg else query
        cursor.execute(query, (eventId,))
        event_row = cursor.fetchone()
        
        if not event_row:
            conn.close()
            return {
                "success": False,
                "error": "Event not found",
                "message": "Event not found"
            }
        
        event_title, event_start, event_end = event_row
        
        # Get satisfaction surveys for this specific event (primary source)
        from ..database.connection import table_name_for_query, DATABASE_URL, is_postgresql_url
        satisfaction_surveys_table = table_name_for_query('satisfactionSurveys')
        evaluation_table = table_name_for_query('evaluation')
        requirements_table = table_name_for_query('requirements')
        from ..database.connection import convert_placeholders
        is_postgresql = is_postgresql_url(DATABASE_URL)
        
        # Use boolean true/false for PostgreSQL, 1/0 for SQLite
        finalized_condition1 = "finalized = true" if is_postgresql else "finalized = 1"
        finalized_condition2 = "e.finalized = true" if is_postgresql else "e.finalized = 1"
        
        query1 = f"""
            SELECT id, respondentType, overallSatisfaction, volunteerRating, beneficiaryRating,
                   q13, q14, comment, recommendations, finalized
            FROM {satisfaction_surveys_table}
            WHERE "eventId" = ? AND "eventType" = ? AND {finalized_condition1}
        """
        query1 = convert_placeholders(query1)
        cursor.execute(query1, (eventId, eventType))
        
        survey_rows = cursor.fetchall()
        
        # Also get evaluations as fallback (for backward compatibility)
        query2 = f"""
            SELECT e.id, e."requirementId", e.criteria, e.finalized, e.q13, e.q14, e.comment, e.recommendations,
                   r."eventId", r.type
            FROM {evaluation_table} e
            INNER JOIN {requirements_table} r ON e."requirementId" = r.id
            WHERE r."eventId" = ? AND r.type = ? AND {finalized_condition2} AND e.criteria IS NOT NULL AND e.criteria != ''
        """
        query2 = convert_placeholders(query2)
        cursor.execute(query2, (eventId, eventType))
        
        evaluation_rows = cursor.fetchall()
        conn.close()
        
        volunteerScores = []
        beneficiaryScores = []
        allScores = []
        issues = {}
        
        # Process satisfaction surveys (primary source)
        for row in survey_rows:
            survey_id, respondent_type, overall, vol_rating, ben_rating, q13, q14, comment, recommendations, finalized = row
            
            if not finalized:
                continue
            
            try:
                # Use overall satisfaction as primary score
                satisfaction_score = float(overall) if overall else 0
                
                if satisfaction_score > 0:
                    # Determine if volunteer or beneficiary based on respondentType
                    if respondent_type and "volunteer" in respondent_type.lower():
                        # Use volunteerRating if available, otherwise overall
                        vol_score = float(vol_rating) if vol_rating else satisfaction_score
                        volunteerScores.append(vol_score)
                        allScores.append(vol_score)
                    elif respondent_type and "beneficiary" in respondent_type.lower():
                        # Use beneficiaryRating if available, otherwise overall
                        ben_score = float(ben_rating) if ben_rating else satisfaction_score
                        beneficiaryScores.append(ben_score)
                        allScores.append(ben_score)
                    else:
                        # If type is unclear, use q13/q14 to determine
                        if q13:
                            try:
                                vol_score = float(q13)
                                volunteerScores.append(vol_score)
                                allScores.append(vol_score)
                            except:
                                allScores.append(satisfaction_score)
                        elif q14:
                            try:
                                ben_score = float(q14)
                                beneficiaryScores.append(ben_score)
                                allScores.append(ben_score)
                            except:
                                allScores.append(satisfaction_score)
                        else:
                            # Default to volunteer if unclear
                            volunteerScores.append(satisfaction_score)
                            allScores.append(satisfaction_score)
                    
                    # Extract issues from comments
                    if comment:
                        common_issues = [
                            'communication', 'resource', 'scheduling', 'training', 'support',
                            'accessibility', 'organization', 'time', 'venue', 'materials',
                            'follow-up', 'feedback', 'coordination', 'preparation'
                        ]
                        for issue in common_issues:
                            if issue.lower() in comment.lower():
                                issues[issue] = issues.get(issue, 0) + 1
                                
            except Exception as e:
                print(f"Error processing satisfaction survey {survey_id}: {e}")
                continue
        
        # Process evaluations as fallback (for backward compatibility)
        for row in evaluation_rows:
            eval_id, req_id, criteria_str, finalized, q13, q14, comment, recommendations, req_event_id, req_event_type = row
            
            try:
                # Parse criteria
                criteria = criteria_str
                if isinstance(criteria, str):
                    try:
                        criteria = eval(criteria) if criteria.startswith('{') else json.loads(criteria)
                    except:
                        criteria = {}
                
                # Extract satisfaction score
                satisfaction_score = 4.0
                if 'overall' in criteria:
                    satisfaction_score = _to_score(criteria.get('overall'), 4.0)
                elif 'satisfaction' in criteria:
                    satisfaction_score = _to_score(criteria.get('satisfaction'), 4.0)
                elif 'rating' in criteria:
                    satisfaction_score = _to_score(criteria.get('rating'), 4.0)
                else:
                    rating_keys = ['excellent', 'very_satisfactory', 'satisfactory', 'fair', 'poor']
                    ratings = [criteria.get(key, 0) for key in rating_keys]
                    if any(ratings):
                        score_map = {'excellent': 5, 'very_satisfactory': 4, 'satisfactory': 3, 'fair': 2, 'poor': 1}
                        for i, rating in enumerate(ratings):
                            if rating:
                                satisfaction_score = score_map[rating_keys[i]]
                                break
                satisfaction_score = _to_score(satisfaction_score, 4.0)
                
                # Use q13 and q14 to determine if volunteer or beneficiary
                if q13:
                    try:
                        vol_score = _to_score(q13, satisfaction_score)
                        volunteerScores.append(vol_score)
                        allScores.append(vol_score)
                    except:
                        volunteerScores.append(satisfaction_score)
                        allScores.append(satisfaction_score)
                
                if q14:
                    try:
                        ben_score = _to_score(q14, satisfaction_score)
                        beneficiaryScores.append(ben_score)
                        allScores.append(ben_score)
                    except:
                        beneficiaryScores.append(satisfaction_score)
                        allScores.append(satisfaction_score)
                
                # If neither q13 nor q14, assume volunteer (default)
                if not q13 and not q14:
                    volunteerScores.append(satisfaction_score)
                    allScores.append(satisfaction_score)
                
                # Extract issues from comments
                eval_comment = comment or criteria.get('comment', '') or criteria.get('comments', '') or ''
                if eval_comment:
                    common_issues = [
                        'communication', 'resource', 'scheduling', 'training', 'support',
                        'accessibility', 'organization', 'time', 'venue', 'materials',
                        'follow-up', 'feedback', 'coordination', 'preparation'
                    ]
                    for issue in common_issues:
                        if issue.lower() in eval_comment.lower():
                            issues[issue] = issues.get(issue, 0) + 1
                            
            except Exception as e:
                print(f"Error processing evaluation {eval_id}: {e}")
                continue
        
        # Calculate averages
        volunteer_avg = sum(volunteerScores) / len(volunteerScores) if volunteerScores else 0
        beneficiary_avg = sum(beneficiaryScores) / len(beneficiaryScores) if beneficiaryScores else 0
        overall_avg = sum(allScores) / len(allScores) if allScores else 0
        
        # Generate predictive statement
        def generatePrediction(vol_avg, ben_avg, overall):
            if overall >= 4.5:
                prediction = "Excellent satisfaction ratings indicate strong event success. Future similar events are likely to maintain high satisfaction levels."
            elif overall >= 4.0:
                prediction = "Good satisfaction ratings suggest the event met expectations. With minor improvements, future events can achieve even higher satisfaction."
            elif overall >= 3.5:
                prediction = "Moderate satisfaction indicates areas for improvement. Addressing feedback can enhance future event satisfaction."
            else:
                prediction = "Lower satisfaction ratings highlight key areas needing attention. Strategic improvements are recommended for future events."
            
            if vol_avg > ben_avg + 0.3:
                prediction += " Volunteers showed notably higher satisfaction than beneficiaries, suggesting beneficiary experience could be enhanced."
            elif ben_avg > vol_avg + 0.3:
                prediction += " Beneficiaries showed notably higher satisfaction than volunteers, indicating strong impact despite volunteer challenges."
            
            return prediction
        
        prediction = generatePrediction(volunteer_avg, beneficiary_avg, overall_avg)
        
        # Format top issues
        top_issues = []
        for issue, frequency in sorted(issues.items(), key=lambda x: x[1], reverse=True)[:5]:
            top_issues.append({
                'issue': issue.replace('_', ' ').title() + ' Issues',
                'frequency': frequency
            })
        
        return {
            "success": True,
            "data": {
                "eventId": eventId,
                "eventType": eventType,
                "eventTitle": event_title,
                "eventStart": event_start,
                "eventEnd": event_end,
                "volunteerScore": round(volunteer_avg, 1),
                "beneficiaryScore": round(beneficiary_avg, 1),
                "overallScore": round(overall_avg, 1),
                "volunteerCount": len(volunteerScores),
                "beneficiaryCount": len(beneficiaryScores),
                "totalEvaluations": len(survey_rows) + len(evaluation_rows),
                "topIssues": top_issues,
                "prediction": prediction
            },
            "message": "Event satisfaction analytics retrieved successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve event satisfaction analytics"
        }

def clearAnalyticsData():
    """
    Clear all analytics-related data:
    - Deletes all requirements (clears age/sex analytics)
    - Deletes all evaluations (clears satisfaction ratings and dropout risk)
    """
    from ..database import connection
    
    conn, cursor = connection.cursorInstance()
    
    try:
        # Start transaction
        conn.execute("BEGIN TRANSACTION")
        
        from ..database.connection import table_name_for_query
        evaluation_table = table_name_for_query('evaluation')
        requirements_table = table_name_for_query('requirements')
        
        # Delete all evaluations first (they reference requirements)
        cursor.execute(f"DELETE FROM {evaluation_table}")
        deleted_evaluations = cursor.rowcount
        
        # Delete all requirements
        cursor.execute(f"DELETE FROM {requirements_table}")
        deleted_requirements = cursor.rowcount
        
        # Commit transaction
        conn.commit()
        
        return {
            'success': True,
            'message': f'Successfully cleared analytics data: {deleted_requirements} requirements and {deleted_evaluations} evaluations deleted',
            'data': {
                'requirements_deleted': deleted_requirements,
                'evaluations_deleted': deleted_evaluations
            }
        }
        
    except Exception as e:
        # Rollback transaction on error
        conn.rollback()
        import traceback
        return {
            'success': False,
            'message': f'Failed to clear analytics data: {str(e)}',
            'error': traceback.format_exc()
        }
    finally:
        conn.close()

def deleteDummyVolunteersData():
    """
    Delete all analytics data for dummy volunteers including:
    - Age analytics (from requirements and membership)
    - Sex analytics (from requirements and membership)
    - Event participation (requirements)
    - Satisfaction predictions (evaluations)
    - Dropout-risk records (calculated from membership/requirements)
    - Aggregates (all analytics derived from dummy data)
    - The dummy users themselves (membership, accounts, sessions)
    
    Dummy users are identified by:
    - Emails starting with 'dummy' (case-insensitive)
    - Common test patterns: 'example', 'test', 'demo', 'fake'
    """
    from ..database import connection
    
    conn, cursor = connection.cursorInstance()
    
    try:
        # Start transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Step 1: Identify dummy user emails
        # Find all dummy members by email pattern
        # Only match obvious dummy/test patterns - be conservative to avoid deleting real users
        from ..database.connection import table_name_for_query
        membership_table = table_name_for_query('membership')
        requirements_table = table_name_for_query('requirements')
        evaluation_table = table_name_for_query('evaluation')
        print("[DELETE DUMMY] Step 1: Identifying dummy members...")
        cursor.execute(f"""
            SELECT id, email FROM {membership_table} 
            WHERE LOWER(email) LIKE 'dummy%@%' 
               OR LOWER(email) LIKE 'test%@%'
               OR LOWER(email) LIKE 'demo%@%'
               OR LOWER(email) LIKE 'fake%@%'
               OR (LOWER(email) LIKE 'example%@%' AND LOWER(email) NOT LIKE '%batstate%')
               OR LOWER(fullname) = 'dummy'
               OR LOWER(fullname) = 'test'
               OR LOWER(fullname) = 'demo'
               OR LOWER(fullname) = 'fake'
               OR LOWER(fullname) LIKE 'dummy %'
               OR LOWER(fullname) LIKE 'test %'
               OR LOWER(fullname) LIKE 'demo %'
               OR LOWER(fullname) LIKE 'fake %'
        """)
        dummy_members = cursor.fetchall()
        dummy_member_ids = [row[0] for row in dummy_members]
        dummy_emails = [row[1].lower() for row in dummy_members if row[1]]
        print(f"[DELETE DUMMY] Found {len(dummy_member_ids)} dummy members, {len(dummy_emails)} unique emails")
        
        deleted_counts = {
            'evaluations': 0,
            'requirements': 0,
            'sessions': 0,
            'accounts': 0,
            'memberships': 0
        }
        
        if len(dummy_member_ids) > 0 or len(dummy_emails) > 0:
            # Step 2: Delete evaluations linked to dummy requirements
            # First, get requirement IDs for dummy emails
            if len(dummy_emails) > 0:
                print(f"[DELETE DUMMY] Step 2: Finding requirements for {len(dummy_emails)} dummy emails...")
                from ..database.connection import convert_placeholders
                placeholders = ','.join(['?' for _ in dummy_emails])
                query = f"""
                    SELECT id FROM {requirements_table} 
                    WHERE LOWER(email) IN ({placeholders})
                """
                query = convert_placeholders(query)
                cursor.execute(query, dummy_emails)
                dummy_requirement_ids = [row[0] for row in cursor.fetchall()]
                print(f"[DELETE DUMMY] Found {len(dummy_requirement_ids)} dummy requirements")
                
                if len(dummy_requirement_ids) > 0:
                    # Delete evaluations for dummy requirements
                    print(f"[DELETE DUMMY] Step 2a: Deleting evaluations for dummy requirements...")
                    from ..database.connection import convert_placeholders
                    req_placeholders = ','.join(['?' for _ in dummy_requirement_ids])
                    query = f"""
                        DELETE FROM {evaluation_table} 
                        WHERE requirementId IN ({req_placeholders})
                    """
                    query = convert_placeholders(query)
                    cursor.execute(query, dummy_requirement_ids)
                    deleted_counts['evaluations'] = cursor.rowcount
                    print(f"[DELETE DUMMY] Deleted {deleted_counts['evaluations']} evaluations")
            
            # Step 3: Delete requirements for dummy emails
            if len(dummy_emails) > 0:
                print(f"[DELETE DUMMY] Step 3: Deleting requirements for dummy emails...")
                from ..database.connection import convert_placeholders
                placeholders = ','.join(['?' for _ in dummy_emails])
                query = f"""
                    DELETE FROM {requirements_table} 
                    WHERE LOWER(email) IN ({placeholders})
                """
                query = convert_placeholders(query)
                cursor.execute(query, dummy_emails)
                deleted_counts['requirements'] = cursor.rowcount
                print(f"[DELETE DUMMY] Deleted {deleted_counts['requirements']} requirements")
            
            # Step 4: Delete accounts linked to dummy members
            if len(dummy_member_ids) > 0:
                print(f"[DELETE DUMMY] Step 4: Finding accounts for {len(dummy_member_ids)} dummy members...")
                # Get account IDs linked to dummy members
                from ..database.connection import convert_placeholders
                member_placeholders = ','.join(['?' for _ in dummy_member_ids])
                query = f"""
                    SELECT id FROM accounts 
                    WHERE membershipId IN ({member_placeholders})
                """
                query = convert_placeholders(query)
                cursor.execute(query, dummy_member_ids)
                dummy_account_ids = [row[0] for row in cursor.fetchall()]
                print(f"[DELETE DUMMY] Found {len(dummy_account_ids)} dummy accounts")
                
                if len(dummy_account_ids) > 0:
                    # Step 5: Delete sessions for dummy accounts
                    print(f"[DELETE DUMMY] Step 5: Deleting sessions for dummy accounts...")
                    from ..database.connection import convert_placeholders
                    account_placeholders = ','.join(['?' for _ in dummy_account_ids])
                    query = f"""
                        DELETE FROM sessions 
                        WHERE userid IN ({account_placeholders})
                    """
                    query = convert_placeholders(query)
                    cursor.execute(query, dummy_account_ids)
                    deleted_counts['sessions'] = cursor.rowcount
                    print(f"[DELETE DUMMY] Deleted {deleted_counts['sessions']} sessions")
                    
                    # Delete accounts
                    print(f"[DELETE DUMMY] Step 5a: Deleting dummy accounts...")
                    from ..database.connection import convert_placeholders
                    query = f"""
                        DELETE FROM accounts 
                        WHERE id IN ({account_placeholders})
                    """
                    query = convert_placeholders(query)
                    cursor.execute(query, dummy_account_ids)
                    deleted_counts['accounts'] = cursor.rowcount
                    print(f"[DELETE DUMMY] Deleted {deleted_counts['accounts']} accounts")
            
            # Step 6: Delete dummy memberships (the dummy users themselves)
            if len(dummy_member_ids) > 0:
                print(f"[DELETE DUMMY] Step 6: Deleting {len(dummy_member_ids)} dummy memberships...")
                member_placeholders = ','.join(['?' for _ in dummy_member_ids])
                query = f"""
                    DELETE FROM {membership_table} 
                    WHERE id IN ({member_placeholders})
                """
                from ..database.connection import convert_placeholders
                query = convert_placeholders(query)
                cursor.execute(query, dummy_member_ids)
                deleted_counts['memberships'] = cursor.rowcount
                print(f"[DELETE DUMMY] Deleted {deleted_counts['memberships']} memberships")
        else:
            print("[DELETE DUMMY] No dummy members found to delete")
        
        # Commit transaction
        print("[DELETE DUMMY] Committing transaction...")
        conn.commit()
        print("[DELETE DUMMY] Transaction committed successfully!")
        
        total_deleted = sum(deleted_counts.values())
        
        return {
            'success': True,
            'message': f'Successfully deleted all dummy volunteer data: {total_deleted} total records deleted',
            'data': {
                'dummy_members_found': len(dummy_member_ids),
                'deleted_counts': deleted_counts,
                'total_deleted': total_deleted
            }
        }
        
    except Exception as e:
        # Rollback transaction on error
        conn.rollback()
        import traceback
        return {
            'success': False,
            'message': f'Failed to delete dummy volunteer data: {str(e)}',
            'error': traceback.format_exc()
        }
    finally:
        conn.close()

def seedDemoEvaluations(
    count: int = 100,
    years: list[int] | None = None,
    event_id: int | None = None,
    event_type: str | None = None
):
    """
    Insert demo satisfaction survey records tied to real events.
    Defaults to seeding years 2025 and 2026 so predictive ratings has volunteer and beneficiary data.
    """
    try:
        if years is None or len(years) == 0:
            years = [2025, 2026]

        seeded = 0
        issue_pool = [
            'communication', 'resource', 'scheduling', 'training', 'support',
            'accessibility', 'organization', 'time', 'venue', 'materials',
            'feedback', 'coordination', 'preparation'
        ]

        # Build candidate events (real events only) for requested years.
        all_internal = InternalEventDb.getAll() or []
        all_external = ExternalEventDb.getAll() or []
        candidate_events: list[tuple[int, str, int]] = []

        def _event_year(evt: dict) -> int | None:
            dt = _timestamp_to_datetime(evt.get("durationStart"))
            return dt.year if dt else None

        def _append_event(ev: dict, evt_type: str):
            eid = ev.get("id")
            if eid is None:
                return
            ts = int(ev.get("durationStart") or int(time.time() * 1000))
            candidate_events.append((int(eid), evt_type, ts))

        if event_id is not None and event_type in ("internal", "external"):
            source = all_internal if event_type == "internal" else all_external
            matched = next((e for e in source if int(e.get("id", -1)) == int(event_id)), None)
            if matched:
                ts = int(matched.get("durationStart") or int(time.time() * 1000))
                candidate_events = [(int(event_id), event_type, ts)]
        else:
            for ev in all_internal:
                y = _event_year(ev)
                if y in years:
                    _append_event(ev, "internal")
            for ev in all_external:
                y = _event_year(ev)
                if y in years:
                    _append_event(ev, "external")

        # If year filter matches nothing (common on prod), use accepted/completed events from any year.
        if not candidate_events:
            ok_status = {"accepted", "completed"}
            for ev in all_internal:
                if str(ev.get("status") or "").lower() in ok_status:
                    _append_event(ev, "internal")
            for ev in all_external:
                if str(ev.get("status") or "").lower() in ok_status:
                    _append_event(ev, "external")

        if not candidate_events:
            for ev in all_internal:
                _append_event(ev, "internal")
            for ev in all_external:
                _append_event(ev, "external")

        if not candidate_events:
            return {
                'success': False,
                'message': f'No events in database to attach surveys to. Create events first or pass eventId/eventType.',
                'data': {'yearsRequested': years, 'internalCount': len(all_internal), 'externalCount': len(all_external)},
            }

        # Create balanced volunteer/beneficiary samples distributed across candidate events.
        per_event = max(2, count // max(1, len(candidate_events)))
        sample_index = 0
        for evt_id, evt_type, evt_start in candidate_events:
            for _ in range(per_event):
                overall = max(1.0, min(5.0, round(random.gauss(4.2, 0.5), 1)))
                volunteer_rating = max(1.0, min(5.0, round(overall + random.uniform(-0.3, 0.2), 1)))
                beneficiary_rating = max(1.0, min(5.0, round(overall + random.uniform(-0.2, 0.3), 1)))
                issues_in_comment = random.sample(issue_pool, k=random.randint(0, 2))
                comment_text = "Seeded survey response for analytics dashboard. "
                if issues_in_comment:
                    comment_text += "Some concerns: " + ", ".join(issues_in_comment) + "."

                for respondent_type in ("Volunteer", "Beneficiary"):
                    sample_index += 1
                    q13 = str(volunteer_rating) if respondent_type == "Volunteer" else ""
                    q14 = str(beneficiary_rating) if respondent_type == "Beneficiary" else ""
                    requirement_id = f"seed_req_{evt_type}_{evt_id}_{int(time.time()*1000)}_{sample_index}"
                    # Keep submittedAt in epoch-seconds to avoid PostgreSQL int4 overflow
                    # on deployments where this column is INTEGER instead of BIGINT.
                    evt_start_int = int(evt_start or int(time.time() * 1000))
                    evt_start_seconds = evt_start_int // 1000 if evt_start_int > 9_999_999_999 else evt_start_int
                    submitted_at = evt_start_seconds + random.randint(1, 7) * 24 * 60 * 60

                    inserted = SatisfactionSurveyDb.create(
                        eventId=evt_id,
                        eventType=evt_type,
                        requirementId=requirement_id,
                        respondentType=respondent_type,
                        respondentEmail=f"seeded_{evt_type}_{evt_id}_{sample_index}@example.com",
                        respondentName=f"Seeded {respondent_type} {sample_index}",
                        overallSatisfaction=overall,
                        volunteerRating=volunteer_rating if respondent_type == "Volunteer" else None,
                        beneficiaryRating=beneficiary_rating if respondent_type == "Beneficiary" else None,
                        organizationRating=overall,
                        communicationRating=overall,
                        venueRating=overall,
                        materialsRating=overall,
                        supportRating=overall,
                        q13=q13,
                        q14=q14,
                        comment=comment_text,
                        recommendations='Keep improving community engagement.',
                        wouldRecommend=True,
                        areasForImprovement=", ".join(issues_in_comment) if issues_in_comment else "",
                        positiveAspects="Community impact and organization",
                        submittedAt=submitted_at,
                        finalized=True,
                    )
                    if inserted:
                        seeded += 1

        return {
            'success': True,
            'message': f'Seeded {seeded} demo satisfaction surveys',
            'data': {
                'seeded': seeded,
                'years': years,
                'eventsUsed': len(candidate_events),
                'eventScope': {'eventId': event_id, 'eventType': event_type}
            }
        }
    except Exception as e:
        logger.exception("seedDemoEvaluations failed")
        return {
            'success': False,
            'message': f'Failed to seed demo evaluations: {str(e)}',
            'error': str(e),
            'data': {'seeded': 0, 'years': years or [], 'eventsUsed': 0},
        }