"""
Bootstrap membership records from member-app.xlsx when database is empty.

This is intended for fresh deployments (e.g., new Render PostgreSQL database)
so volunteer-related dashboards do not start with zero members.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from ..models.MembershipModel import MembershipModel

load_dotenv()
DEBUG = os.getenv("DEBUG") == "True"


def _candidate_excel_paths() -> list[Path]:
    base_dir = Path(__file__).resolve().parents[2]  # .../sulambi-backend-main
    data_dir = base_dir / "data"
    return [
        data_dir / "member-app.xlsx",
        data_dir / "member app.xlsx",
        data_dir / "member- app.xlsx",
        data_dir / "members-app.xlsx",
        data_dir / "member_app.xlsx",
        data_dir / "members_app.xlsx",
    ]


def _find_excel_file() -> Path | None:
    env_path = (os.getenv("MEMBER_EXCEL_PATH") or "").strip()
    if env_path:
        p = Path(env_path)
        if p.is_file():
            return p
    for p in _candidate_excel_paths():
        if p.exists():
            return p
    return None


def _normalize_sex_for_membership(raw) -> str:
    """Store canonical labels so dashboard SQL + analytics grouping match."""
    v = _to_str(raw).lower()
    if v in ("female", "f", "woman", "girl", "gal", "babae", "babaye", "f.", "fem", "fem."):
        return "Female"
    if v in ("male", "m", "man", "boy", "guy", "lalaki", "male.", "m."):
        return "Male"
    if "female" in v or "woman" in v or "girl" in v:
        return "Female"
    if "male" in v and "female" not in v:
        return "Male"
    return "N/A"


def _normalize_age_for_membership(raw) -> int:
    n = _to_int(raw, 0)
    return max(0, n)


def _to_str(value) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return "" if text.lower() == "nan" else text


def _to_bool_from_yes(value) -> bool:
    return _to_str(value).lower() in ("yes", "true", "1")


def _to_int(value, default: int = 0) -> int:
    try:
        if value is None:
            return default
        text = str(value).strip()
        if text == "" or text.lower() == "nan":
            return default
        return int(float(text))
    except Exception:
        return default


def ensure_members_seeded_from_excel() -> dict:
    """
    Seed members from Excel only when membership table is empty.
    Returns a small status payload for startup logging.
    """
    model = MembershipModel()
    existing_members = model.getAll() or []
    if existing_members:
        return {"seeded": 0, "reason": "membership_not_empty", "current": len(existing_members)}

    excel_path = _find_excel_file()
    if not excel_path:
        return {"seeded": 0, "reason": "excel_not_found"}

    try:
        import pandas as pd
    except Exception as e:
        return {"seeded": 0, "reason": f"pandas_unavailable: {e}"}

    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        return {"seeded": 0, "reason": f"excel_read_failed: {e}"}

    inserted = 0
    skipped = 0

    for index, row in df.iterrows():
        # Keep behavior aligned with existing importer that skips row 0.
        if index == 0:
            continue

        fullname = _to_str(row.get("Name (Last Name, First Name, Middle Initial)", ""))
        email = _to_str(row.get("Email Address", ""))
        gsuite_email = _to_str(row.get("Gsuite Email", ""))
        final_email = gsuite_email or email

        if not fullname or not final_email:
            skipped += 1
            continue

        if model.getOrSearch(["email"], [final_email]):
            skipped += 1
            continue

        applying_as = _to_str(row.get("I'm applying as", "Volunteer"))
        volunteer_exp = _to_bool_from_yes(row.get("Do you have any prior volunteerism experience?", ""))
        weekdays = _to_str(row.get("How much time can you devote for volunteering activities on weekdays?", ""))
        weekends = _to_str(row.get("How much time can you devote for volunteering activities on weekends?", ""))
        interests = _to_str(
            row.get("What areas or interests do you want to volunteer in? Check the area(s) that interest you. ", "")
        )
        srcode = _to_str(row.get("Sr-Code", ""))
        age = _normalize_age_for_membership(row.get("Age", 0))
        birthday = _to_str(row.get("Birthday", ""))
        sex = _normalize_sex_for_membership(row.get("Sex", ""))
        campus = _to_str(row.get("Campus", ""))
        college_dept = _to_str(row.get("College/Department", ""))
        yrlevel_program = _to_str(row.get("Year Level & Program", ""))
        address = _to_str(row.get("Address", ""))
        contact_num = _to_str(row.get("Contact Number", ""))
        fblink = _to_str(row.get("Facebook Link", ""))
        blood_type = _to_str(row.get("Blood Type", ""))
        blood_donation = _to_str(row.get("Blood Donation", ""))
        medical_condition = _to_str(
            row.get("Do you have any existing medical condition/s? If yes, please specify. If none, type N/A.", "N/A")
        ) or "N/A"
        payment_option = _to_str(row.get("Payment Options", ""))
        volunteer_exp_q1 = _to_str(
            row.get("1. What volunteering activities of Sulambi VOSA last Academic Year did you join?", "")
        )
        volunteer_exp_q2 = _to_str(
            row.get("2. What volunteering activities did you join outside Sulambi VOSA and/or the University?", "")
        )
        volunteer_exp_proof = _to_str(
            row.get("2.1 Upload proof for the volunteering activities you joined outside(e.g. Pictures, Certificate)", "")
        )
        reason_q1 = _to_str(row.get("Why do you want to become a member?", ""))
        reason_q2 = _to_str(row.get("What can you contribute to the organization?", ""))

        username_base = fullname.split(" ")[0].replace(" ", "").replace(",", "")
        username = f"{username_base}{index}"

        try:
            model.create(
                applyingAs=applying_as or "Volunteer",
                volunterismExperience=volunteer_exp,
                weekdaysTimeDevotion=weekdays,
                weekendsTimeDevotion=weekends,
                areasOfInterest=interests,
                fullname=fullname,
                email=final_email,
                affiliation="Batangas State University",
                srcode=srcode,
                age=age,
                birthday=birthday,
                sex=sex,
                campus=campus,
                collegeDept=college_dept,
                yrlevelprogram=yrlevel_program,
                address=address,
                contactNum=contact_num,
                fblink=fblink,
                bloodType=blood_type,
                bloodDonation=blood_donation,
                medicalCondition=medical_condition,
                paymentOption=payment_option,
                username=username,
                password="password",
                active=True,
                accepted=True,
                volunteerExpQ1=volunteer_exp_q1,
                volunteerExpQ2=volunteer_exp_q2,
                volunteerExpProof=volunteer_exp_proof,
                reasonQ1=reason_q1,
                reasonQ2=reason_q2,
            )
            inserted += 1
        except Exception as e:
            skipped += 1
            if DEBUG:
                print(f"[startup] seed member skipped: {final_email} ({e})")

    return {
        "seeded": inserted,
        "skipped": skipped,
        "excel": str(excel_path),
    }


def seed_members_from_excel() -> dict:
    """
    Insert rows from member-app.xlsx into ``membership`` (same table as dashboard
    summary/analytics). Safe to call repeatedly: skips existing emails.

    Production note: startup ``ensure_members_seeded_from_excel`` only runs when
    the membership table is completely empty, so a non-empty DB never auto-imports.
    This function does not have that restriction.

    Optional env: MEMBER_EXCEL_PATH=absolute path to an .xlsx when the file is not
    under sulambi-backend-main/data/.
    """
    model = MembershipModel()
    excel_path = _find_excel_file()
    if not excel_path:
        return {
            "success": False,
            "inserted": 0,
            "skipped_duplicates": 0,
            "skipped_invalid": 0,
            "message": "Excel file not found. Place member-app.xlsx under data/ or set MEMBER_EXCEL_PATH.",
        }

    try:
        import pandas as pd
    except Exception as e:
        return {
            "success": False,
            "inserted": 0,
            "skipped_duplicates": 0,
            "skipped_invalid": 0,
            "message": f"pandas not available: {e}",
        }

    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        return {
            "success": False,
            "inserted": 0,
            "skipped_duplicates": 0,
            "skipped_invalid": 0,
            "message": f"Failed to read Excel: {e}",
        }

    inserted = 0
    skipped_duplicates = 0
    skipped_invalid = 0
    errors: list[str] = []

    for index, row in df.iterrows():
        if index == 0:
            continue

        fullname = _to_str(row.get("Name (Last Name, First Name, Middle Initial)", ""))
        email = _to_str(row.get("Email Address", ""))
        gsuite_email = _to_str(row.get("Gsuite Email", ""))
        final_email = gsuite_email or email

        if not fullname or not final_email:
            skipped_invalid += 1
            continue

        if model.getOrSearch(["email"], [final_email]):
            skipped_duplicates += 1
            continue

        applying_as = _to_str(row.get("I'm applying as", "Volunteer"))
        volunteer_exp = _to_bool_from_yes(row.get("Do you have any prior volunteerism experience?", ""))
        weekdays = _to_str(row.get("How much time can you devote for volunteering activities on weekdays?", ""))
        weekends = _to_str(row.get("How much time can you devote for volunteering activities on weekends?", ""))
        interests = _to_str(
            row.get("What areas or interests do you want to volunteer in? Check the area(s) that interest you. ", "")
        )
        srcode = _to_str(row.get("Sr-Code", ""))
        age = _normalize_age_for_membership(row.get("Age", 0))
        birthday = _to_str(row.get("Birthday", ""))
        sex = _normalize_sex_for_membership(row.get("Sex", ""))
        campus = _to_str(row.get("Campus", ""))
        college_dept = _to_str(row.get("College/Department", ""))
        yrlevel_program = _to_str(row.get("Year Level & Program", ""))
        address = _to_str(row.get("Address", ""))
        contact_num = _to_str(row.get("Contact Number", ""))
        fblink = _to_str(row.get("Facebook Link", ""))
        blood_type = _to_str(row.get("Blood Type", ""))
        blood_donation = _to_str(row.get("Blood Donation", ""))
        medical_condition = _to_str(
            row.get("Do you have any existing medical condition/s? If yes, please specify. If none, type N/A.", "N/A")
        ) or "N/A"
        payment_option = _to_str(row.get("Payment Options", ""))
        volunteer_exp_q1 = _to_str(
            row.get("1. What volunteering activities of Sulambi VOSA last Academic Year did you join?", "")
        )
        volunteer_exp_q2 = _to_str(
            row.get("2. What volunteering activities did you join outside Sulambi VOSA and/or the University?", "")
        )
        volunteer_exp_proof = _to_str(
            row.get("2.1 Upload proof for the volunteering activities you joined outside(e.g. Pictures, Certificate)", "")
        )
        reason_q1 = _to_str(row.get("Why do you want to become a member?", ""))
        reason_q2 = _to_str(row.get("What can you contribute to the organization?", ""))

        username_base = fullname.split(" ")[0].replace(" ", "").replace(",", "")
        username = f"{username_base}{index}"

        try:
            model.create(
                applyingAs=applying_as or "Volunteer",
                volunterismExperience=volunteer_exp,
                weekdaysTimeDevotion=weekdays,
                weekendsTimeDevotion=weekends,
                areasOfInterest=interests,
                fullname=fullname,
                email=final_email,
                affiliation="Batangas State University",
                srcode=srcode,
                age=age,
                birthday=birthday,
                sex=sex,
                campus=campus,
                collegeDept=college_dept,
                yrlevelprogram=yrlevel_program,
                address=address,
                contactNum=contact_num,
                fblink=fblink,
                bloodType=blood_type,
                bloodDonation=blood_donation,
                medicalCondition=medical_condition,
                paymentOption=payment_option,
                username=username,
                password="password",
                active=True,
                accepted=True,
                volunteerExpQ1=volunteer_exp_q1,
                volunteerExpQ2=volunteer_exp_q2,
                volunteerExpProof=volunteer_exp_proof,
                reasonQ1=reason_q1,
                reasonQ2=reason_q2,
            )
            inserted += 1
        except Exception as e:
            skipped_invalid += 1
            if len(errors) < 10:
                errors.append(f"{final_email}: {e}")
            if DEBUG:
                print(f"[seed_members_from_excel] skip {final_email}: {e}")

    return {
        "success": True,
        "inserted": inserted,
        "skipped_duplicates": skipped_duplicates,
        "skipped_invalid": skipped_invalid,
        "excel": str(excel_path),
        "message": f"Inserted {inserted} membership row(s); skipped {skipped_duplicates} duplicate email(s), {skipped_invalid} invalid/failed row(s).",
        "errors": errors,
    }

