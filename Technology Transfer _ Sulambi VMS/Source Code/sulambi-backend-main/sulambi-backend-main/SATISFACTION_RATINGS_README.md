# Predictive Satisfaction Ratings Database

## Overview
Database system that automatically collects volunteer and beneficiary satisfaction ratings (1-5 scale) with written comments from form submissions.

## How It Works

### Data Collection
When volunteers or beneficiaries submit evaluation forms:
1. Form data is saved to `evaluation` table (existing)
2. **Automatically** saved to `satisfactionSurveys` table (new)
3. Data includes:
   - 1-5 rating scores (overall, organization, communication, venue, materials, support)
   - Written comments and recommendations
   - Respondent type (Volunteer/Beneficiary)
   - Event information

### Database Table
**Table:** `satisfactionSurveys` (auto-created)

**Data Source:** 
- Volunteer Evaluation Forms → `satisfactionSurveys` (respondentType: "Volunteer")
- Beneficiary Evaluation Forms → `satisfactionSurveys` (respondentType: "Beneficiary")

## Excel Export

**Script:** `export_satisfaction_ratings_to_excel.py`

**Output:** `data/satisfaction-ratings.xlsx`

**Usage:**
```bash
python export_satisfaction_ratings_to_excel.py
```

**Excel Format:**
- Similar to Age and Sex Analytics Excel format
- Contains all ratings (1-5 scale)
- Includes comments and recommendations
- Shows volunteer vs beneficiary responses

## Automatic Data Collection

Data is **automatically collected** when:
- Volunteers submit evaluation forms via QR code
- Beneficiaries submit evaluation forms via QR code
- Forms are submitted through `/api/evaluation/<requirementId>` endpoint

**No manual data entry needed!**

## Current Status
✓ Database table created
✓ Automatic data collection enabled
✓ Excel export ready
✓ Sample data removed (only real form submissions)
