"""Test the dropout analytics function"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.controllers.analytics import getVolunteerDropoutAnalytics

result = getVolunteerDropoutAnalytics()

if result.get('success'):
    print('✓ Function executed successfully!')
    data = result.get('data', {})
    semester_data = data.get('semesterData', [])
    at_risk = data.get('atRiskVolunteers', [])
    
    print(f'\nSemester Data: {len(semester_data)} semesters')
    for sem in semester_data:
        print(f"  {sem['semester']}: {sem['volunteers']} joined, {sem['attended']} attended, {sem['dropouts']} dropouts, {sem['events']} events/volunteer")
    
    print(f'\nAt-Risk Volunteers: {len(at_risk)} volunteers')
    for vol in at_risk[:5]:  # Show first 5
        print(f"  {vol['name']}: {vol['riskScore']}% risk, {vol['inactivityDays']} days inactive, {vol['attendedEvents']}/{vol['joinedEvents']} attended")
else:
    print(f'✗ Error: {result.get("error")}')
    if 'traceback' in result:
        print(f'\nTraceback:\n{result["traceback"]}')

















