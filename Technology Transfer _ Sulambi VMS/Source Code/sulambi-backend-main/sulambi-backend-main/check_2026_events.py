import os
from datetime import datetime

from dotenv import load_dotenv
import psycopg2


def to_iso(ms: int | float | None) -> str:
    """Convert milliseconds-since-epoch to human-readable string."""
    if ms is None:
        return "None"
    try:
        return datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return f"invalid({ms})"


def main() -> None:
    # Load .env from backend folder so DATABASE_URL from your backend env is available
    load_dotenv()

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL is not set. Are you running this in Render/backend env?")
        return

    print(f"Using DATABASE_URL={database_url.split('@')[-1]}")

    conn = psycopg2.connect(database_url)
    cur = conn.cursor()

    tables = ["internalEvents", "externalEvents"]

    for table in tables:
        print(f"\n=== {table} events with durationStart in 2026 ===")
        # durationStart is stored as milliseconds since epoch
        query = f"""
            SELECT id, title, durationstart, durationend
            FROM "{table}"
            WHERE to_timestamp(durationstart / 1000) >= '2026-01-01'
              AND to_timestamp(durationstart / 1000) <  '2027-01-01'
            ORDER BY durationstart;
        """
        cur.execute(query)
        rows = cur.fetchall()
        if not rows:
            print("  (none)")
        for rid, title, ds, de in rows:
            print(
                f"  ID={rid}, title={repr(title)}, "
                f"start={to_iso(ds)}, end={to_iso(de)}"
            )

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()


