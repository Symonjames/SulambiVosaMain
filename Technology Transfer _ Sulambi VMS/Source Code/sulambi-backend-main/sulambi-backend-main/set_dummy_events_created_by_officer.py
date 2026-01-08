"""
Set dummy/seeded events' createdBy to an Officer account so the UI shows "Officer Username: Officer"
instead of "Admin" in the Event Approval table.

Safe defaults:
- Only updates events where status='accepted' AND title contains '(202' (seeded naming convention)
- Only updates rows currently createdBy an admin account

Run:
  py .\\set_dummy_events_created_by_officer.py
"""

from app.database import connection


def _fetchone(cur, sql, params=()):
    cur.execute(sql, params)
    return cur.fetchone()


def _ensure_officer_account(cur, conn):
    row = _fetchone(
        cur,
        """
        SELECT id, username, accountType
        FROM accounts
        WHERE LOWER(username) = 'officer'
        LIMIT 1
        """,
    )
    if row:
        return int(row[0]), str(row[1])

    # create a lightweight officer account used for seeded content attribution
    cur.execute(
        """
        INSERT INTO accounts (username, password, accountType, membershipId, active)
        VALUES (?, ?, ?, NULL, TRUE)
        """,
        ("Officer", "seeded-officer-password", "officer"),
    )
    conn.commit()
    officer_id = cur.lastrowid
    return int(officer_id), "Officer"


def _find_admin_id(cur):
    # Prefer explicit admin accountType
    row = _fetchone(
        cur,
        """
        SELECT id, username
        FROM accounts
        WHERE accountType = 'admin'
        ORDER BY id ASC
        LIMIT 1
        """,
    )
    if row:
        return int(row[0]), str(row[1])

    # Fallback: username match
    row = _fetchone(
        cur,
        """
        SELECT id, username
        FROM accounts
        WHERE LOWER(username) = 'admin'
        ORDER BY id ASC
        LIMIT 1
        """,
    )
    if row:
        return int(row[0]), str(row[1])

    return None, None


def main():
    conn, cur = connection.cursorInstance()
    try:
        admin_id, admin_username = _find_admin_id(cur)
        if not admin_id:
            print("[WARN] No admin account found. Nothing to update.")
            return

        officer_id, officer_username = _ensure_officer_account(cur, conn)

        # Update only seeded-style accepted events with (202 in title
        for table in ("internalEvents", "externalEvents"):
            cur.execute(
                f"""
                UPDATE {table}
                SET createdBy = ?
                WHERE createdBy = ?
                  AND status = 'accepted'
                  AND title LIKE '%(202%'
                """,
                (officer_id, admin_id),
            )
            print(f"[OK] Updated {table}: {cur.rowcount} row(s) now createdBy={officer_username}")

        conn.commit()
        print("[OK] Done")
        print(f"      Admin: {admin_username} (id={admin_id}) -> Officer: {officer_username} (id={officer_id})")
    finally:
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()


