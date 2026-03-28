#!/usr/bin/env python3
"""
Scan the database for legacy file paths (not https Cloudinary URLs).
Writes legacy_upload_manifest.txt — copy those files into uploads/ then run
migrate_uploads_to_cloudinary.py or run_full_cloudinary_migration.py.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import (  # noqa: E402
    cursorInstance,
    quote_identifier,
    DATABASE_URL,
    is_postgresql_url,
    table_name_for_query,
)

MANIFEST = Path(__file__).resolve().parent / "legacy_upload_manifest.txt"

FILE_PATH_TABLES = {
    "requirements": ["medCert", "waiver", "curriculum", "destination", "firstAid", "fees"],
    "internalReport": ["photos"],
    "externalReport": ["photos"],
}


def _is_legacy_path(text: str) -> bool:
    if not text or not str(text).strip():
        return False
    s = str(text).strip()
    if "res.cloudinary.com" in s:
        return False
    if s.startswith("http://") or s.startswith("https://"):
        return False
    if "uploads/" in s or "uploads\\" in s:
        return True
    # Bare filename saved by old backend (uuid + name)
    if re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", s, re.I):
        return True
    return False


def _extract_filenames(value: str) -> list[str]:
    out: list[str] = []
    if not value:
        return out
    s = str(value).strip()
    parts: list[str]
    if s.startswith("["):
        try:
            import json

            parsed = json.loads(s)
            parts = [str(x) for x in parsed] if isinstance(parsed, list) else [s]
        except Exception:
            parts = [p.strip() for p in s.split(",") if p.strip()]
    else:
        parts = [p.strip() for p in s.split(",") if p.strip()]
    for part in parts:
        p = part.strip().strip('"').strip("'")
        if not _is_legacy_path(p):
            continue
        p = p.replace("\\", "/")
        if p.startswith("uploads/"):
            p = p[len("uploads/") :]
        elif p.lower().startswith("uploads/"):
            p = p.split("/", 1)[-1]
        out.append(p)
    return out


def export_legacy_paths_to_manifest() -> int:
    is_pg = is_postgresql_url(DATABASE_URL)
    try:
        conn, cursor = cursorInstance()
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return 1

    seen: set[str] = set()

    try:
        for table_name, columns in FILE_PATH_TABLES.items():
            from_clause = table_name_for_query(table_name)
            existing_columns: list[str] = []
            try:
                if is_pg:
                    cursor.execute(
                        """
                        SELECT column_name FROM information_schema.columns
                        WHERE LOWER(table_name) = LOWER(%s)
                        ORDER BY column_name
                        """,
                        (table_name,),
                    )
                    existing_columns = [r[0] for r in cursor.fetchall()]
                else:
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    existing_columns = [col[1] for col in cursor.fetchall()]
            except Exception as e:
                print(f"[WARN] Skip table {table_name}: {e}")
                continue

            for column in columns:
                actual = None
                if is_pg:
                    for col in existing_columns:
                        if col.lower() == column.lower():
                            actual = col
                            break
                else:
                    if column in existing_columns:
                        actual = column
                if not actual:
                    continue

                qc = quote_identifier(actual) if is_pg else actual
                try:
                    if is_pg:
                        q = f'SELECT {qc} FROM {from_clause} WHERE {qc} IS NOT NULL AND CAST({qc} AS TEXT) != %s'
                        cursor.execute(q, ("",))
                    else:
                        q = f"SELECT {qc} FROM {from_clause} WHERE {qc} IS NOT NULL AND {qc} != ''"
                        cursor.execute(q)
                    for (cell,) in cursor.fetchall():
                        if not cell:
                            continue
                        for fn in _extract_filenames(cell):
                            if fn and fn not in seen:
                                seen.add(fn)
                except Exception as e:
                    print(f"[WARN] {table_name}.{actual}: {e}")
                    if is_pg:
                        try:
                            conn.rollback()
                        except Exception:
                            pass

        conn.close()
    except Exception as e:
        print(f"[ERROR] {e}")
        return 1

    lines = sorted(seen)
    MANIFEST.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    print(f"[OK] Wrote {len(lines)} unique path(s) to {MANIFEST}")
    print("     Copy these files into uploads/ (same filenames), then run migration.")
    return 0 if lines else 2


def main() -> int:
    print("=" * 60)
    print("EXPORT LEGACY UPLOAD PATHS (from database)")
    print("=" * 60)
    return export_legacy_paths_to_manifest()


if __name__ == "__main__":
    raise SystemExit(main())
