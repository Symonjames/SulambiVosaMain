"""
Controller for volunteer participation history
Provides detailed semester-by-semester participation data for analytics
"""

def getVolunteerParticipationHistory(volunteerEmail=None, semester=None, year=None):
    """
    Get detailed volunteer participation history
    - If volunteerEmail provided: returns that volunteer's history across all semesters
    - If semester provided: returns all volunteers' participation for that semester
    - If year provided: returns all participation for that year
    - If none provided: returns all participation history
    """
    try:
        from ..database.connection import cursorInstance
        
        conn, cursor = cursorInstance()
        
        # Build query based on filters
        query = """
            SELECT 
                volunteerEmail,
                volunteerName,
                membershipId,
                semester,
                semesterYear,
                semesterNumber,
                eventsJoined,
                eventsAttended,
                eventsDropped,
                attendanceRate,
                firstEventDate,
                lastEventDate,
                daysActiveInSemester,
                participationConsistency,
                engagementLevel,
                calculatedAt,
                lastUpdated
            FROM volunteerParticipationHistory
            WHERE 1=1
        """
        params = []
        
        if volunteerEmail:
            query += " AND volunteerEmail = ?"
            params.append(volunteerEmail)
        
        if semester:
            query += " AND semester = ?"
            params.append(semester)
        
        if year:
            query += " AND semesterYear = ?"
            params.append(int(year))
        
        query += " ORDER BY semesterYear DESC, semesterNumber DESC, volunteerName"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Format results
        participation_data = []
        for row in rows:
            participation_data.append({
                "volunteerEmail": row[0],
                "volunteerName": row[1],
                "membershipId": row[2],
                "semester": row[3],
                "semesterYear": row[4],
                "semesterNumber": row[5],
                "eventsJoined": row[6],
                "eventsAttended": row[7],
                "eventsDropped": row[8],
                "attendanceRate": row[9],
                "firstEventDate": row[10],
                "lastEventDate": row[11],
                "daysActiveInSemester": row[12],
                "participationConsistency": row[13],
                "engagementLevel": row[14],
                "calculatedAt": row[15],
                "lastUpdated": row[16]
            })
        
        conn.close()
        
        return {
            "success": True,
            "data": participation_data,
            "count": len(participation_data),
            "message": "Volunteer participation history retrieved successfully"
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve volunteer participation history",
            "traceback": traceback.format_exc()
        }

def getSemesterParticipationSummary(semester=None, year=None):
    """
    Get semester-by-semester participation summary for bar graphs
    Returns aggregated data showing active vs low/irregular participation
    """
    try:
        from ..database.connection import cursorInstance
        
        conn, cursor = cursorInstance()
        
        # Build query
        query = """
            SELECT 
                semester,
                COUNT(DISTINCT volunteerEmail) as total_volunteers,
                SUM(eventsJoined) as total_joined,
                SUM(eventsAttended) as total_attended,
                SUM(eventsDropped) as total_dropped,
                AVG(attendanceRate) as avg_attendance_rate,
                COUNT(DISTINCT CASE WHEN engagementLevel = 'Active' THEN volunteerEmail END) as active_volunteers,
                COUNT(DISTINCT CASE WHEN engagementLevel = 'At Risk' THEN volunteerEmail END) as at_risk_volunteers,
                COUNT(DISTINCT CASE WHEN engagementLevel = 'Inactive' THEN volunteerEmail END) as inactive_volunteers,
                COUNT(DISTINCT CASE WHEN participationConsistency = 'Regular' THEN volunteerEmail END) as regular_volunteers,
                COUNT(DISTINCT CASE WHEN participationConsistency = 'Irregular' THEN volunteerEmail END) as irregular_volunteers,
                COUNT(DISTINCT CASE WHEN participationConsistency = 'Low' THEN volunteerEmail END) as low_volunteers
            FROM volunteerParticipationHistory
            WHERE 1=1
        """
        params = []
        
        if semester:
            query += " AND semester = ?"
            params.append(semester)
        
        if year:
            query += " AND semesterYear = ?"
            params.append(int(year))
        
        query += " GROUP BY semester ORDER BY semester"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Format results for bar graphs
        semester_summary = []
        for row in rows:
            semester_summary.append({
                "semester": row[0],
                "totalVolunteers": row[1],
                "totalJoined": row[2],
                "totalAttended": row[3],
                "totalDropped": row[4],
                "avgAttendanceRate": round(row[5] or 0, 2),
                "activeVolunteers": row[6],
                "atRiskVolunteers": row[7],
                "inactiveVolunteers": row[8],
                "regularVolunteers": row[9],
                "irregularVolunteers": row[10],
                "lowVolunteers": row[11]
            })
        
        conn.close()
        
        return {
            "success": True,
            "data": semester_summary,
            "message": "Semester participation summary retrieved successfully"
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve semester participation summary",
            "traceback": traceback.format_exc()
        }

















