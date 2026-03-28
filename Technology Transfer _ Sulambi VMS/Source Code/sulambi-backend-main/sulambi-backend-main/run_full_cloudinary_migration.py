#!/usr/bin/env python3
"""
End-to-end legacy media migration:
  1) Optional: export DB manifest if uploads/ is empty
  2) migrate_uploads_to_cloudinary.py (upload + rewrite DB)
  3) update_frontend_image_refs.py (hardcoded uploads/ in src)

Requires .env (or environment) with:
  CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET
  DATABASE_URL (PostgreSQL) or DB_PATH (SQLite)

Usage:
  python run_full_cloudinary_migration.py
  python run_full_cloudinary_migration.py --skip-frontend
  python run_full_cloudinary_migration.py --export-only
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent


def _uploads_data_files() -> list[Path]:
    d = BACKEND_ROOT / "uploads"
    if not d.is_dir():
        return []
    skip = {"readme.md", ".gitkeep", ".ds_store"}
    out = []
    for p in d.rglob("*"):
        if p.is_file() and p.name.lower() not in skip:
            out.append(p)
    return out


def main() -> int:
    os.chdir(BACKEND_ROOT)
    sys.path.insert(0, str(BACKEND_ROOT))

    parser = argparse.ArgumentParser(description="Full Cloudinary migration runner")
    parser.add_argument("--skip-frontend", action="store_true", help="Do not run frontend path replacer")
    parser.add_argument("--export-only", action="store_true", help="Only write legacy_upload_manifest.txt")
    args = parser.parse_args()

    from dotenv import load_dotenv

    load_dotenv(BACKEND_ROOT / ".env")

    if args.export_only:
        from export_legacy_upload_paths import main as export_main

        return export_main()

    data_files = _uploads_data_files()
    if not data_files:
        print("[INFO] No files under uploads/ — exporting paths still referenced in the database…")
        from export_legacy_upload_paths import export_legacy_paths_to_manifest

        code = export_legacy_paths_to_manifest()
        if code == 2:
            print(
                "\n[STOP] No legacy paths found in DB (or DB empty). "
                "Nothing to migrate, or connect DATABASE_URL / DB_PATH."
            )
            return 2
        if code != 0:
            return code
        print(
            f"\n[NEXT] Copy the listed files into: {BACKEND_ROOT / 'uploads'}\n"
            "       Then run: python run_full_cloudinary_migration.py"
        )
        return 3

    from migrate_uploads_to_cloudinary import migrate_uploads_to_cloudinary

    mig_rc = migrate_uploads_to_cloudinary()
    if mig_rc not in (0, None):
        return int(mig_rc)

    mapping = BACKEND_ROOT / "cloudinary_migration_mapping.json"
    if args.skip_frontend:
        print("[INFO] Skipped frontend update (--skip-frontend).")
        return 0

    if not mapping.exists() or mapping.stat().st_size == 0:
        print("[WARN] No mapping file produced; skipping frontend update.")
        return 0

    # Source Code / sulambi-frontend-main / sulambi-frontend-main / script.py
    fe_script = BACKEND_ROOT.parent.parent / "sulambi-frontend-main" / "sulambi-frontend-main" / "update_frontend_image_refs.py"
    if not fe_script.is_file():
        print(f"[WARN] Frontend script missing: {fe_script}")
        return 0

    print("\n[INFO] Running frontend image ref update…")
    r = subprocess.run([sys.executable, str(fe_script)], cwd=str(fe_script.parent))
    if r.returncode != 0:
        print(f"[WARN] Frontend script exited {r.returncode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
