# Migrate Local Uploads to Cloudinary

This guide explains how to migrate all files from the local `uploads` folder to Cloudinary while ensuring they continue to appear in their respective places in the application.

## Prerequisites

1. **Cloudinary Account**: Sign up at [cloudinary.com](https://cloudinary.com) (free tier available)
2. **Cloudinary Credentials**: Get from your Cloudinary dashboard:
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`

## Setup

1. **Set Environment Variables** (create/update `.env` file):
   ```env
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret
   ```

   For production (Render), set these in your Render dashboard:
   - Go to your backend service → Environment
   - Add the three Cloudinary variables

2. **Install Cloudinary Package** (if not already installed):
   ```bash
   pip install cloudinary
   ```

## Running the Migration

### Step 1: Test the Script (Optional)

Review what will be migrated:
- The script will process all files in the `uploads/` folder
- It will find all database references to these files
- It will upload each file to Cloudinary
- It will update database references from local paths to Cloudinary URLs

### Step 2: Run the Migration

```bash
cd "Technology Transfer _ Sulambi VMS/Source Code/sulambi-backend-main/sulambi-backend-main"
python migrate_uploads_to_cloudinary.py
```

### Step 3: Update Frontend References (Automated)

After migration, automatically update hardcoded image paths in the frontend:

```bash
cd "Technology Transfer _ Sulambi VMS/Source Code/sulambi-frontend-main/sulambi-frontend-main"
python update_frontend_image_refs.py
```

This script will:
1. Read the `cloudinary_migration_mapping.json` file
2. Search all frontend code files (`.tsx`, `.ts`, `.jsx`, `.js`, `.json`)
3. Find hardcoded image paths like `uploads/logo.png` or `"uploads/image.jpg"`
4. Replace them with Cloudinary URLs automatically
5. Show a summary of all changes made

**Note**: The script only updates files in the `src` directory, excluding `node_modules` and build folders.

### Step 4: Verify the Results

The migration process:
1. ✅ Upload each file to Cloudinary
2. ✅ Update database references automatically
3. ✅ Create a mapping file (`cloudinary_migration_mapping.json`) for rollback
4. ✅ Update frontend hardcoded image references (via Step 3)

## Important Notes About File Types

**UI-Only Images**: Some images in the `uploads` folder may be for UI purposes only (e.g., logos, icons, static assets) and may not have database references. This is normal and expected. The script will still upload these files to Cloudinary so they remain available for your application.

**Frontend Compatibility**: The frontend has been updated to automatically detect and use Cloudinary URLs (URLs starting with `http://` or `https://`). This means:
- **Database-referenced files**: Will work automatically after migration (database will have Cloudinary URLs)
- **UI-only files**: Can be automatically updated using the `update_frontend_image_refs.py` script, which replaces hardcoded paths with Cloudinary URLs

**Database-Referenced Files**: Files that are referenced in the database (requirements, reports, etc.) will have their database paths automatically updated to Cloudinary URLs.

## What Gets Updated

The script updates file paths in these database tables:

1. **requirements table**:
   - `medCert` - Medical certificate paths
   - `waiver` - Waiver document paths
   - `curriculum` - Curriculum paths
   - `destination` - Destination paths
   - `firstAid` - First aid certificate paths
   - `fees` - Fee document paths

2. **internalReport table**:
   - `photos` - Photo arrays (JSON format)

3. **externalReport table**:
   - `photos` - Photo arrays (JSON format)

## Example Migration

**Before:**
```json
{
  "waiver": "uploads/0da36ec4-7b72-46b4-8764-213cb9481cdd1.PNG"
}
```

**After:**
```json
{
  "waiver": "https://res.cloudinary.com/your-cloud/image/upload/v1234567890/uploads/0da36ec4-7b72-46b4-8764-213cb9481cdd1.PNG"
}
```

## Frontend Compatibility

The frontend already handles both local and Cloudinary URLs:
- If URL starts with `http://` or `https://` → Uses as-is (Cloudinary URL)
- If URL starts with `uploads/` → Constructs local URL (for local development)

**No frontend changes needed!** ✅

## Rollback (If Needed)

If something goes wrong, the mapping file contains all changes:

1. Open `cloudinary_migration_mapping.json`
2. For each entry, manually restore the `old_value` in the database
3. Or contact support for automated rollback script

## Important Notes

1. **Backup First**: The script modifies your database. Make a backup before running:
   ```bash
   # For SQLite
   cp app/database/database.db app/database/database.db.backup
   
   # For PostgreSQL (from Render dashboard, use backup feature)
   ```

2. **Test Locally**: Test the migration on a local copy first before running on production

3. **Verify Images**: After migration, test the application to ensure all images appear correctly:
   - Check requirement documents
   - Check report photos
   - Verify all image displays

4. **Local Files**: After verifying everything works, you can delete local files from `uploads/` folder (they're now on Cloudinary)

5. **Future Uploads**: New uploads will automatically go to Cloudinary (already configured in the system)

## Troubleshooting

**Error: "Cloudinary configuration missing"**
- Set the three Cloudinary environment variables in `.env` file

**Error: "Database not found"**
- Check your `DB_PATH` environment variable
- Or ensure you're running from the correct directory

**Images still not appearing after migration:**
- Check browser console for 404 errors
- Verify Cloudinary URLs are accessible
- Check if frontend is using correct `VITE_API_URI`

**Some files have no database references:**
- Files already using Cloudinary URLs will be skipped (this is normal)
- UI-only files (logos, icons, static assets) may not have database references - this is expected
- Files with no database references will still be uploaded to Cloudinary but won't have their paths updated in the database
- **UI-only files**: After migration, run the `update_frontend_image_refs.py` script (Step 3) to automatically update hardcoded image references in your frontend code. The script will replace paths like `uploads/logo.png` with Cloudinary URLs automatically.
- If you know a file should have a database reference but it's not found, check the filename matching (database might use a different path format)

## Support

If you encounter issues:
1. Check the mapping file for what was changed
2. Review the console output for specific errors
3. Verify Cloudinary credentials are correct
4. Ensure database connection is working

---

**Last Updated:** 2024
**Script Version:** 1.0
