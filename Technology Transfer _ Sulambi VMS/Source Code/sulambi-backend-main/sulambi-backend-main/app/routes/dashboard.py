from flask import Blueprint, request
from ..controllers import dashboard

DashboardBlueprint = Blueprint('dashboard', __name__, url_prefix="/dashboard")

@DashboardBlueprint.get('/')
def dashboardGetRoute():
  return dashboard.getSummary()

@DashboardBlueprint.get('/analytics')
def dashboardGetAnalyticsRoute():
  return dashboard.getAnalytics()

@DashboardBlueprint.get('/active-member')
def dashboardGetActiveMemberDetailsRoute():
  return dashboard.getActiveMemberData()

@DashboardBlueprint.get('/event/external/<id>')
def dashboardGetExternalEventDetails(id):
  return dashboard.getEventInformation(id, "external")

@DashboardBlueprint.get('/event/internal/<id>')
def dashboardGetInternalEventDetails(id):
  return dashboard.getEventInformation(id, "internal")
