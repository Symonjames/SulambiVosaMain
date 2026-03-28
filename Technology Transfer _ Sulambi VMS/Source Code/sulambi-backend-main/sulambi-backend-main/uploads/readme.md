# Uploads folder (legacy migration)

**Production uploads go to Cloudinary** — this folder is only for **one-time migration**.

1. Export paths from the database:
   ```bash
   python export_legacy_upload_paths.py
   ```
   This creates `legacy_upload_manifest.txt` in the backend root.

2. Restore the **actual files** from backup (old server, laptop, etc.) into this folder using the **exact filenames** listed in the manifest (or drop the whole old `uploads/` tree here).

3. Run the full pipeline (from backend root, with `.env` containing `DATABASE_URL` / `DB_PATH` and `CLOUDINARY_*`):
   ```bash
   python run_full_cloudinary_migration.py
   ```

Files in this directory are ignored by git (`uploads/*`) except this README.
