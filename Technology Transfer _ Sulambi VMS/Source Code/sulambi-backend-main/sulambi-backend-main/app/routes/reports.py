from flask import Blueprint, request
from ..controllers import reports
from ..middlewares.requiredParams import reportsParams

ReportsBlueprint = Blueprint('reports', __name__, url_prefix="/reports")

@ReportsBlueprint.get("/")
def getAllReportDetails():
  return reports.getAllReports()

@ReportsBlueprint.get("/analytics/external/<eventId>")
def getExternalReportDetails(eventId):
  return reports.getReportCalculations(eventId, "external")

@ReportsBlueprint.get("/analytics/internal/<eventId>")
def getInternalReportDetails(eventId):
  return reports.getReportCalculations(eventId, "internal")

@ReportsBlueprint.post("/external/<eventId>")
def createExternalReportRoute(eventId):
  return reports.createReport(eventId, "external")

@ReportsBlueprint.post("/internal/<eventId>")
def createInternalReportRoute(eventId):
  return reports.createReport(eventId, "internal")

@ReportsBlueprint.delete("/external/<reportId>")
def deleteExternalReportRoute(reportId):
  return reports.deleteReport(int(reportId), "external")

@ReportsBlueprint.delete("/internal/<reportId>")
def deleteInternalReportRoute(reportId):
  return reports.deleteReport(int(reportId), "internal")

@ReportsBlueprint.before_request
def reportsMiddleware():
  if (request.method != "OPTIONS"):
    if (request.method not in ["GET", "DELETE", "PATCH"]):
      missingParams = None

      # external report creation
      if (("/api/reports/external" in request.path) and request.method == "POST" and request.view_args.get("eventId") != None):
        missingParams = reportsParams.createExternalReportParamCheck()

      # internal report creation
      elif (("/api/reports/internal" in request.path) and request.method == "POST" and request.view_args.get("eventId") != None):
        missingParams = reportsParams.createInternalReportParamCheck()

      if (missingParams != None):
        return missingParams