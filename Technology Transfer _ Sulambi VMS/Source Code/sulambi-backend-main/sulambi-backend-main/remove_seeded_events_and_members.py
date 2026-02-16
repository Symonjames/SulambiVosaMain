"""
Remove some seeded events and seeded members to reduce database size and improve load times.

- Seeded events: external/internal events whose title contains '(202' (seeded naming convention).
- Seeded members: keep only the most recent K members (default 80); delete older ones.

Run from backend root:
  python remove_seeded_events_and_members.py
  python remove_seeded_events_and_members.py --keep-members 50   # keep 50 members
  python remove_seeded_events_and_members.py --dry-run            # print counts only, no delete

Uses app.database.connection (supports SQLite and PostgreSQL).
"""

import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
is_postgresql = DATABASE_URL and DATABASE_URL.startswith("postgresql://")


def q(s):
    """Quote identifier for PostgreSQL."""
    return f'"{s}"' if is_postgresql else s


def ph(n):
    """Placeholders: ? for SQLite, %s for PostgreSQL."""
    return ", ".join(["%s" if is_postgresql else "?" for _ in range(n)])


def run(cursor, sql, params=None):
    if params is None:
        params = ()
    if is_postgresql:
        sql = sql.replace("?", "%s")
    cursor.execute(sql, params)


def fetchone(cursor, sql, params=()):
    run(cursor, sql, params)
    return cursor.fetchone()


def fetchall(cursor, sql, params=()):
    run(cursor, sql, params)
    return cursor.fetchall()


def remove_seeded_events(conn, cursor):
    """Delete events where title contains '(202' (seeded convention). Clean dependencies first."""
    title_pattern = "%(202%"
    out = {"external": 0, "internal": 0}

    for event_type, table, report_table in [
        ("external", "externalEvents", "externalReport"),
        ("internal", "internalEvents", "internalReport"),
    ]:
        t, rt = q(table), q(report_table)
        # Get event IDs to delete
        run(
            cursor,
            f"SELECT id FROM {t} WHERE title LIKE ?",
            (title_pattern,),
        )
        event_ids = [row[0] for row in cursor.fetchall()]
        if not event_ids:
            continue

        placeholders = ph(len(event_ids))
        id_list_sql = f"({placeholders})"

        # 1. Evaluations for requirements that belong to these events
        req_table = q("requirements")
        run(
            cursor,
            f"""
            DELETE FROM {q('evaluation')}
            WHERE requirementId IN (
                SELECT id FROM {req_table}
                WHERE eventId IN {id_list_sql} AND type = ?
            )
            """,
            tuple(list(event_ids) + [event_type]),
        )
        conn.commit()

        # 2. Requirements for these events
        run(
            cursor,
            f"DELETE FROM {req_table} WHERE eventId IN {id_list_sql} AND type = ?",
            tuple(list(event_ids) + [event_type]),
        )
        conn.commit()

        # 3. Reports for these events
        run(
            cursor,
            f"DELETE FROM {rt} WHERE eventId IN {id_list_sql}",
            tuple(event_ids),
        )
        conn.commit()

        # 4. Satisfaction surveys for these events
        run(
            cursor,
            f"DELETE FROM {q('satisfactionSurveys')} WHERE eventId IN {id_list_sql} AND eventType = ?",
            tuple(list(event_ids) + [event_type]),
        )
        conn.commit()

        # 5. Activity month assignments (internal only)
        if event_type == "internal":
            run(
                cursor,
                f"DELETE FROM {q('activity_month_assignments')} WHERE eventId IN {id_list_sql}",
                tuple(event_ids),
            )
            conn.commit()

        # 6. Delete events
        run(
            cursor,
            f"DELETE FROM {t} WHERE id IN {id_list_sql}",
            tuple(event_ids),
        )
        out[event_type] = cursor.rowcount
        conn.commit()

    return out


def remove_excess_members(conn, cursor, keep_count=80):
    """Keep only the most recent `keep_count` members (by id); delete the rest."""
    m = q("membership")
    run(
        cursor,
        f"SELECT id FROM {m} ORDER BY id DESC LIMIT {int(keep_count)}",
    )
    keep_ids = [row[0] for row in cursor.fetchall()]
    if not keep_ids:
        return 0

    run(cursor, f"SELECT id FROM {m}")
    all_ids = [row[0] for row in cursor.fetchall()]
    delete_ids = [i for i in all_ids if i not in keep_ids]
    if not delete_ids:
        return 0

    placeholders = ph(len(delete_ids))
    id_list_sql = f"({placeholders})"

    # Get emails for requirements/evaluation cleanup
    run(
        cursor,
        f"SELECT email FROM {m} WHERE id IN {id_list_sql}",
        tuple(delete_ids),
    )
    emails = [row[0] for row in cursor.fetchall()]
    if not emails:
        return 0

    # 1. Evaluations for requirements with these emails
    run(
        cursor,
        f"DELETE FROM {q('evaluation')} WHERE requirementId IN (SELECT id FROM {q('requirements')} WHERE email IN ({ph(len(emails))}))",
        tuple(emails),
    )
    conn.commit()

    # 2. Requirements with these emails
    run(
        cursor,
        f"DELETE FROM {q('requirements')} WHERE email IN ({ph(len(emails))})",
        tuple(emails),
    )
    conn.commit()

    # 2b. Dropout risk and participation history for these members
    run(
        cursor,
        f"DELETE FROM {q('dropoutRiskAssessment')} WHERE membershipId IN {id_list_sql}",
        tuple(delete_ids),
    )
    conn.commit()
    run(
        cursor,
        f"DELETE FROM {q('volunteerParticipationHistory')} WHERE membershipId IN {id_list_sql}",
        tuple(delete_ids),
    )
    conn.commit()
    run(
        cursor,
        f"DELETE FROM {q('volunteerParticipationHistory')} WHERE volunteerEmail IN ({ph(len(emails))})",
        tuple(emails),
    )
    conn.commit()

    # 3. Get account ids for these membership ids, then delete sessions for those accounts
    run(
        cursor,
        f"SELECT id FROM {q('accounts')} WHERE membershipId IN {id_list_sql}",
        tuple(delete_ids),
    )
    account_ids = [row[0] for row in cursor.fetchall()]
    if account_ids:
        acc_ph = ph(len(account_ids))
        run(
            cursor,
            f"DELETE FROM {q('sessions')} WHERE userid IN ({acc_ph})",
            tuple(account_ids),
        )
        conn.commit()

    # 4. Accounts that reference these membership ids
    run(
        cursor,
        f"DELETE FROM {q('accounts')} WHERE membershipId IN {id_list_sql}",
        tuple(delete_ids),
    )
    conn.commit()

    # 5. Delete membership rows
    run(
        cursor,
        f"DELETE FROM {m} WHERE id IN {id_list_sql}",
        tuple(delete_ids),
    )
    removed = cursor.rowcount
    conn.commit()
    return removed


def main():
    import sys
    from app.database import connection

    keep_members = 80
    dry_run = False
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--dry-run":
            dry_run = True
        elif arg == "--keep-members":
            if i + 1 < len(args):
                try:
                    keep_members = int(args[i + 1])
                except ValueError:
                    pass
                i += 1  # skip next so we don't treat number as a flag
        i += 1

    conn, cursor = connection.cursorInstance()
    try:
        print("=" * 60)
        print("REMOVING SEEDED EVENTS AND EXCESS MEMBERS")
        if dry_run:
            print("(DRY RUN - no changes will be made)")
        print("=" * 60)

        # 1. Seeded events
        print("\n1. Seeded events (title contains '(202')...")
        if dry_run:
            for event_type, table in [("external", "externalEvents"), ("internal", "internalEvents")]:
                run(cursor, f"SELECT COUNT(*) FROM {q(table)} WHERE title LIKE ?", ("%(202%",))
                c = cursor.fetchone()[0]
                print(f"   Would remove {c} {event_type} events")
        else:
            counts = remove_seeded_events(conn, cursor)
            total_events = counts["external"] + counts["internal"]
            print(f"   Removed {counts['external']} external, {counts['internal']} internal events ({total_events} total)")

        # 2. Excess members
        print(f"\n2. Members (keeping most recent {keep_members})...")
        run(cursor, f"SELECT COUNT(*) FROM {q('membership')}")
        total_m = cursor.fetchone()[0]
        to_remove = max(0, total_m - keep_members)
        if dry_run:
            print(f"   Would remove {to_remove} members (current total: {total_m})")
        else:
            removed_members = remove_excess_members(conn, cursor, keep_count=keep_members)
            print(f"   Removed {removed_members} members")

        print("\n" + "=" * 60)
        print("Done.")
        print("=" * 60)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
