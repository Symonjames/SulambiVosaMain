from flask import Blueprint, request
from ..controllers.analytics import (
    getEventSuccessAnalytics,
    getVolunteerDropoutAnalytics,
    getPredictiveInsights,
    getSatisfactionAnalytics,
    getEventSatisfactionAnalytics,
    seedDemoEvaluations,
    clearAnalyticsData,
    deleteDummyVolunteersData
)
from ..tools.rebuild_semester_satisfaction import rebuild as rebuild_semester_satisfaction
from ..controllers.participation import (
    getVolunteerParticipationHistory,
    getSemesterParticipationSummary
)

AnalyticsBlueprint = Blueprint("analytics", __name__)

@AnalyticsBlueprint.route("/analytics/event-success", methods=["GET"])
def eventSuccessRoute():
    """Get event success analytics"""
    result = getEventSuccessAnalytics()
    return result, 200 if result.get("success") else 500

@AnalyticsBlueprint.route("/analytics/volunteer-dropout", methods=["GET"])
def volunteerDropoutRoute():
    """Get volunteer dropout risk analytics"""
    from flask import jsonify
    year = request.args.get('year', None)
    result = getVolunteerDropoutAnalytics(year)
    print(f"[DROPOUT ROUTE] Returning result: success={result.get('success')}, has_data={bool(result.get('data'))}")
    if result.get('data'):
        print(f"[DROPOUT ROUTE] semesterData length: {len(result.get('data', {}).get('semesterData', []))}")
        print(f"[DROPOUT ROUTE] atRiskVolunteers length: {len(result.get('data', {}).get('atRiskVolunteers', []))}")
    return jsonify(result), 200 if result.get("success") else 500

@AnalyticsBlueprint.route("/analytics/insights", methods=["GET"])
def insightsRoute():
    """Get predictive insights and recommendations"""
    result = getPredictiveInsights()
    return result, 200 if result.get("success") else 500

@AnalyticsBlueprint.route("/analytics/satisfaction/rebuild", methods=["POST", "OPTIONS"])
def rebuildSatisfactionRoute():
    """Admin: rebuild semester_satisfaction from evaluations"""
    # Handle CORS preflight quickly
    if request.method == "OPTIONS":
        from flask import jsonify
        origin = request.headers.get('Origin', '*')
        response = jsonify({"status": "ok"})
        response.status_code = 200
        response.headers.add("Access-Control-Allow-Origin", origin)
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response
    try:
        year = request.args.get('year', None)
        rebuild_semester_satisfaction(year)
        return {"success": True, "message": "semester_satisfaction rebuilt"}, 200
    except Exception as e:
        return {"success": False, "error": str(e), "message": "Failed to rebuild semester satisfaction"}, 500

@AnalyticsBlueprint.route("/analytics/satisfaction", methods=["GET"])
def satisfactionAnalyticsRoute():
    """Get satisfaction analytics from QR evaluations"""
    year = request.args.get('year', None)
    result = getSatisfactionAnalytics(year)
    return result, 200 if result.get("success") else 500

@AnalyticsBlueprint.route("/analytics/satisfaction/event", methods=["GET"])
def eventSatisfactionAnalyticsRoute():
    """Get satisfaction analytics for a specific event"""
    event_id = request.args.get('eventId', None)
    event_type = request.args.get('eventType', None)
    
    if not event_id or not event_type:
        return {
            "success": False,
            "error": "Missing eventId or eventType parameter",
            "message": "Both eventId and eventType are required"
        }, 400
    
    try:
        event_id_int = int(event_id)
    except:
        return {
            "success": False,
            "error": "Invalid eventId",
            "message": "eventId must be a valid integer"
        }, 400
    
    result = getEventSatisfactionAnalytics(event_id_int, event_type)
    return result, 200 if result.get("success") else 500

@AnalyticsBlueprint.route("/analytics/participation-history", methods=["GET"])
def participationHistoryRoute():
    """Get detailed volunteer participation history"""
    from flask import jsonify
    volunteer_email = request.args.get('volunteerEmail', None)
    semester = request.args.get('semester', None)
    year = request.args.get('year', None)
    result = getVolunteerParticipationHistory(volunteer_email, semester, year)
    return jsonify(result), 200 if result.get("success") else 500

@AnalyticsBlueprint.route("/analytics/participation-summary", methods=["GET"])
def participationSummaryRoute():
    """Get semester-by-semester participation summary for bar graphs"""
    from flask import jsonify
    semester = request.args.get('semester', None)
    year = request.args.get('year', None)
    result = getSemesterParticipationSummary(semester, year)
    return jsonify(result), 200 if result.get("success") else 500

@AnalyticsBlueprint.route("/analytics/all", methods=["GET"])
def allAnalyticsRoute():
    """Get all analytics data in one request"""
    try:
        eventSuccess = getEventSuccessAnalytics()
        dropoutRisk = getVolunteerDropoutAnalytics()
        insights = getPredictiveInsights()
        satisfaction = getSatisfactionAnalytics()
        
        return {
            "success": True,
            "data": {
                "eventSuccess": eventSuccess,
                "dropoutRisk": dropoutRisk,
                "insights": insights,
                "satisfaction": satisfaction
            },
            "message": "All analytics data retrieved successfully"
        }, 200
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve analytics data"
        }, 500

@AnalyticsBlueprint.route("/analytics/dev/seed", methods=["GET"])
def seedEvaluationsRoute():
    """Seed demo evaluation records for testing analytics"""
    count_param = request.args.get('count', default='100')
    try:
        count = int(count_param)
    except:
        count = 100
    result = seedDemoEvaluations(count)
    return result, 200 if result.get("success") else 500

@AnalyticsBlueprint.route("/analytics/dev/clear", methods=["POST", "OPTIONS"])
def clearAnalyticsDataRoute():
    """Clear all analytics data (requirements and evaluations)"""
    # Handle OPTIONS explicitly at route level for CORS
    if request.method == "OPTIONS":
        from flask import jsonify
        origin = request.headers.get('Origin', '*')
        response = jsonify({"status": "ok"})
        response.status_code = 200
        response.headers.add("Access-Control-Allow-Origin", origin)
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response
    
    try:
        result = clearAnalyticsData()
        status_code = 200 if result.get("success") else 500
        from flask import jsonify, make_response
        origin = request.headers.get('Origin', '*')
        resp = make_response(jsonify(result), status_code)
        resp.headers.add("Access-Control-Allow-Origin", origin)
        resp.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        resp.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        resp.headers.add("Access-Control-Allow-Credentials", "true")
        return resp
    except Exception as e:
        from flask import jsonify, make_response
        origin = request.headers.get('Origin', '*')
        error_resp = make_response(jsonify({
            "success": False,
            "error": str(e),
            "message": f"Error clearing analytics data: {str(e)}"
        }), 500)
        error_resp.headers.add("Access-Control-Allow-Origin", origin)
        error_resp.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        error_resp.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        error_resp.headers.add("Access-Control-Allow-Credentials", "true")
        return error_resp

@AnalyticsBlueprint.route("/analytics/dev/delete-dummy-volunteers", methods=["POST", "OPTIONS"])
def deleteDummyVolunteersRoute():
    """Delete all dummy volunteer data including analytics, participation, and user records"""
    # Handle OPTIONS explicitly at route level for CORS
    if request.method == "OPTIONS":
        from flask import jsonify
        origin = request.headers.get('Origin', '*')
        response = jsonify({"status": "ok"})
        response.status_code = 200
        response.headers.add("Access-Control-Allow-Origin", origin)
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response
    
    try:
        result = deleteDummyVolunteersData()
        status_code = 200 if result.get("success") else 500
        from flask import jsonify, make_response
        origin = request.headers.get('Origin', '*')
        resp = make_response(jsonify(result), status_code)
        resp.headers.add("Access-Control-Allow-Origin", origin)
        resp.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        resp.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        resp.headers.add("Access-Control-Allow-Credentials", "true")
        return resp
    except Exception as e:
        from flask import jsonify, make_response
        origin = request.headers.get('Origin', '*')
        error_resp = make_response(jsonify({
            "success": False,
            "error": str(e),
            "message": f"Error deleting dummy volunteer data: {str(e)}"
        }), 500)
        error_resp.headers.add("Access-Control-Allow-Origin", origin)
        error_resp.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        error_resp.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        error_resp.headers.add("Access-Control-Allow-Credentials", "true")
        return error_resp