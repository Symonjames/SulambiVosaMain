"""
WARNING: Make sure to execute this code after creation of new column signatoriesId.
This script initializes all the values of signatories id from NULL to created new one

Kindly import this file to --test argument to execute (see server.py)
"""

from app.models.InternalEventModel import InternalEventModel
from app.models.ExternalEventModel import ExternalEventModel
from app.models.SignatoriesModel import SignatoriesModel
from app.models.ExternalReportModel import ExternalReportModel
from app.models.InternalReportModel import InternalReportModel

InternalEvents: list[dict] = InternalEventModel().getAll()
ExternalEvents: list[dict] = ExternalEventModel().getAll()
InternalReports: list[dict] = InternalReportModel().getAll()
ExternalReports: list[dict] = ExternalReportModel().getAll()

for event in InternalEvents:
  if (event.get("signatoriesId") != None):
    continue

  eventId = event["id"]
  createdSignatories = SignatoriesModel().create(
    approvedBy="NAME",
    preparedBy="NAME",
    recommendingApproval1="NAME",
    recommendingApproval2="NAME",
    reviewedBy="NAME"
  )
  InternalEventModel().updateSpecific(eventId, ["signatoriesId"], (createdSignatories["id"],))
  print("[+] Updated Signatories for Internal event: ", event["title"])

for event in ExternalEvents:
  if (event.get("signatoriesId") != None):
    continue

  eventId = event["id"]
  createdSignatories = SignatoriesModel().create(
    approvedBy="NAME",
    preparedBy="NAME",
    recommendingApproval1="NAME",
    recommendingApproval2="NAME",
    reviewedBy="NAME"
  )
  ExternalEventModel().updateSpecific(eventId, ["signatoriesId"], (createdSignatories["id"],))
  print("[+] Updated Signatories for External event: ", event["title"])

for report in InternalReports:
  if (report.get("signatoriesId") != None):
    continue

  createdSignatories = SignatoriesModel().create(
    approvedBy="NAME",
    preparedBy="NAME",
    recommendingApproval1="NAME",
    recommendingApproval2="NAME",
    reviewedBy="NAME"
  )

  InternalReportModel().updateSpecific(report.get("id"), ["signatoriesId"], (createdSignatories.get("id"),))

for report in InternalReports:
  if (report.get("signatoriesId") != None):
    continue

  createdSignatories = SignatoriesModel().create(
    approvedBy="NAME",
    preparedBy="NAME",
    recommendingApproval1="NAME",
    recommendingApproval2="NAME",
    reviewedBy="NAME"
  )

  ExternalReportModel().updateSpecific(report.get("id"), ["signatoriesId"], (createdSignatories.get("id"),))
