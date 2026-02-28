#!/usr/bin/env python3
"""
Diagnostic script for evaluation email scheduling/sending.

Usage examples:
  python test_evaluation_email_automation.py
  python test_evaluation_email_automation.py --send-requirement <requirement_uuid>
  python test_evaluation_email_automation.py --send-due --limit 5
"""

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv


def _to_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value == 1
    if isinstance(value, str):
        v = value.strip().lower()
        return v in ("1", "true", "t", "yes", "y")
    return False


def _safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _event_for_requirement(requirement, internal_db, external_db):
    event_type = (requirement.get("type") or "").strip().lower()
    event_id = requirement.get("eventId")
    if event_id is None:
        return None
    if event_type == "internal":
        return internal_db.get(event_id)
    return external_db.get(event_id)


def _fmt_ms(ms):
    if not ms:
        return "0 (immediate)"
    dt = datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
    return f"{ms} ({dt.isoformat()})"


def _fmt_remaining_ms(target_ms, now_ms):
    if target_ms <= 0:
        return "immediate"
    delta = target_ms - now_ms
    if delta <= 0:
        return "due now"
    total_sec = int(delta / 1000)
    hours = total_sec // 3600
    mins = (total_sec % 3600) // 60
    sec = total_sec % 60
    return f"in {hours}h {mins}m {sec}s"


def _is_eval_finalized(requirement_id, evaluation_db):
    rows = evaluation_db.getAndSearch(["requirementId"], [requirement_id]) or []
    if not rows:
        return False
    row = rows[0]
    return _to_bool(row.get("finalized"))


def main():
    backend_root = Path(__file__).resolve().parent
    os.chdir(backend_root)
    load_dotenv(backend_root / ".env")

    parser = argparse.ArgumentParser(description="Test evaluation email automation.")
    parser.add_argument("--send-requirement", dest="send_requirement", default=None,
                        help="Requirement UUID to send evaluation email now.")
    parser.add_argument("--send-due", action="store_true",
                        help="Send evaluation emails for due requirements now.")
    parser.add_argument("--set-email", dest="set_email_requirement", default=None,
                        help="Requirement UUID to update email for.")
    parser.add_argument("--email", dest="email_value", default=None,
                        help="Email value used with --set-email.")
    parser.add_argument("--to-email", dest="to_email_override", default=None,
                        help="Override recipient email when sending (does not update DB).")
    parser.add_argument("--show-all", action="store_true",
                        help="Print all requirements (not only accepted/due).")
    parser.add_argument("--limit", type=int, default=10,
                        help="Max number of due entries to print/send (default: 10).")
    args = parser.parse_args()

    sys.path.insert(0, str(backend_root))

    from app.models.RequirementsModel import RequirementsModel
    from app.models.InternalEventModel import InternalEventModel
    from app.models.ExternalEventModel import ExternalEventModel
    from app.models.EvaluationModel import EvaluationModel
    from app.modules.Mailer import validateEmailConfig, htmlMailer

    requirements_db = RequirementsModel()
    internal_db = InternalEventModel()
    external_db = ExternalEventModel()
    evaluation_db = EvaluationModel()

    print("\n=== Evaluation Email Automation Diagnostic ===")
    print(f"Backend root: {backend_root}")

    email_status = validateEmailConfig()
    print(f"Email provider: {email_status.get('provider', 'Unknown')}")
    print(f"Email configured: {email_status.get('configured', False)}")
    print(f"Email check: {email_status.get('message', '')}")

    all_requirements = requirements_db.getAll() or []
    accepted_reqs = [r for r in all_requirements if _to_bool(r.get("accepted"))]
    print(f"Total requirements: {len(all_requirements)}")
    print(f"Accepted requirements: {len(accepted_reqs)}")

    if args.show_all:
        print("\nAll requirements snapshot:")
        for req in all_requirements[:max(1, args.limit)]:
            req_id = req.get("id")
            req_name = (req.get("fullname") or "").strip()
            req_email = (req.get("email") or "").strip()
            req_type = req.get("type") or "external"
            req_event_id = req.get("eventId")
            req_event = _event_for_requirement(req, internal_db, external_db) or {}
            req_event_title = req_event.get("title") or "Event Not Found"
            req_eval_send_ms = _safe_int(req_event.get("evaluationSendTime"), 0)
            accepted_raw = req.get("accepted")
            if _to_bool(accepted_raw):
                accepted_label = "accepted"
            elif accepted_raw in (0, "0", False, "false", "False"):
                accepted_label = "rejected"
            else:
                accepted_label = "pending"
            print(
                f"- req={req_id} name={req_name or '(blank)'} email={req_email or '(blank)'} "
                f"type={req_type} eventId={req_event_id} event='{req_event_title}' "
                f"evaluationSendTime={_fmt_ms(req_eval_send_ms)} "
                f"status={accepted_label}"
            )

    now_ms = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
    due_rows = []
    accepted_rows = []
    skipped_no_email = []
    skipped_no_event = []

    for req in accepted_reqs:
        req_id = req.get("id")
        email = (req.get("email") or "").strip()
        if not req_id:
            continue
        if not email:
            skipped_no_email.append(req_id)
            continue

        event = _event_for_requirement(req, internal_db, external_db)
        if not event:
            skipped_no_event.append(req_id)
            continue

        send_ms = _safe_int(event.get("evaluationSendTime"), 0)
        finalized = _is_eval_finalized(req_id, evaluation_db)
        row = {
            "requirement": req,
            "event": event,
            "send_ms": send_ms,
            "finalized": finalized,
        }
        accepted_rows.append(row)
        is_due = (send_ms <= 0) or (send_ms <= now_ms)
        if not is_due:
            continue

        due_rows.append(row)

    print(f"Due-for-send entries (now): {len(due_rows)}")
    if accepted_rows:
        print("\nAccepted requirement schedule snapshot:")
        for row in accepted_rows[:max(1, args.limit)]:
            req = row["requirement"]
            event = row["event"]
            print(
                f"- req={req.get('id')} email={req.get('email')} "
                f"type={req.get('type')} eventId={req.get('eventId')} "
                f"event='{event.get('title', 'Untitled')}' "
                f"evaluationSendTime={_fmt_ms(row['send_ms'])} "
                f"status={_fmt_remaining_ms(row['send_ms'], now_ms)} "
                f"finalized={row['finalized']}"
            )
    if skipped_no_email:
        print("\nSkipped (missing requirement email):")
        for req_id in skipped_no_email[:max(1, args.limit)]:
            print(f"- req={req_id}")
    if skipped_no_event:
        print("\nSkipped (missing linked event record):")
        for req_id in skipped_no_event[:max(1, args.limit)]:
            print(f"- req={req_id}")
    if due_rows:
        print("\nTop due entries:")
        for row in due_rows[:max(1, args.limit)]:
            req = row["requirement"]
            event = row["event"]
            print(
                f"- req={req.get('id')} email={req.get('email')} "
                f"type={req.get('type')} eventId={req.get('eventId')} "
                f"event='{event.get('title', 'Untitled')}' "
                f"evaluationSendTime={_fmt_ms(row['send_ms'])} "
                f"finalized={row['finalized']}"
            )

    def _send_eval_email_now(requirement_details, event_details, recipient_override=None):
        template_path = backend_root / "templates" / "evaluation-mail-template.html"
        template_html = template_path.read_text(encoding="utf-8")
        token = str(requirement_details.get("id") or "")
        base_url = os.getenv("FRONTEND_APP_URL") or ""
        link = (base_url.rstrip("/") + "/evaluation/" + token) if base_url else ("/evaluation/" + token)
        event_pin = (event_details.get("beneficiaryEvaluationPin") or "").strip()
        mail_to = (recipient_override or requirement_details.get("email") or "").strip()
        if not mail_to:
            print(f"[SEND SKIP] Missing recipient email for req={token}")
            return False

        template_html = template_html.replace("[name]", requirement_details.get("fullname") or "")
        template_html = template_html.replace("[token]", token)
        template_html = template_html.replace("[event-title]", event_details.get("title") or "")
        template_html = template_html.replace("[link]", link)
        template_html = template_html.replace("[event-pin]", event_pin if event_pin else "Not set (beneficiary survey open without PIN)")
        return bool(htmlMailer(
            mailTo=mail_to,
            htmlRendered=template_html,
            subject="Evaluation Attendance",
        ))

    if args.set_email_requirement:
        requirement_id = str(args.set_email_requirement).strip()
        new_email = (args.email_value or "").strip()
        if not new_email or "@" not in new_email:
            print("ERROR: Provide a valid --email when using --set-email")
            raise SystemExit(1)
        target_req = requirements_db.get(requirement_id)
        if not target_req:
            print(f"ERROR: Requirement not found: {requirement_id}")
            raise SystemExit(1)
        requirements_db.updateSpecific(requirement_id, ["email"], (new_email,))
        updated = requirements_db.get(requirement_id) or {}
        print(f"\nUpdated requirement email: req={requirement_id} email={updated.get('email')}")
        return

    if args.send_requirement:
        target = requirements_db.get(str(args.send_requirement).strip())
        if not target:
            print(f"\nERROR: Requirement not found: {args.send_requirement}")
            raise SystemExit(1)
        target_event = _event_for_requirement(target, internal_db, external_db)
        if not target_event:
            print(f"\nERROR: Event not found for requirement: {args.send_requirement}")
            raise SystemExit(1)

        print(f"\nSending evaluation email NOW for requirement: {args.send_requirement}")
        ok = _send_eval_email_now(target, target_event, args.to_email_override)
        print("Send result:", "SUCCESS" if ok else "FAILED")
        return

    if args.send_due:
        if not due_rows:
            print("\nNo due entries to send.")
            return
        to_send = due_rows[:max(1, args.limit)]
        print(f"\nSending {len(to_send)} due email(s) now...")
        success = 0
        fail = 0
        for row in to_send:
            req = row["requirement"]
            event = row["event"]
            ok = _send_eval_email_now(req, event, args.to_email_override)
            if ok:
                success += 1
            else:
                fail += 1
            print(f"  req={req.get('id')} -> {'SUCCESS' if ok else 'FAILED'}")
        print(f"\nDone. Success={success} Failed={fail}")
        return

    print("\nDry-run complete. No emails sent.")
    print("Use one of these to send:")
    print("  --send-requirement <requirement_uuid>")
    print("  --send-due --limit 5")


if __name__ == "__main__":
    main()

