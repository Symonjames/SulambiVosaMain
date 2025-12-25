# API Setup Instructions

## Issue Fixed
The "Recent Photo Submissions" section was showing "Image not found" errors because the frontend couldn't properly construct URLs for loading images from the backend.

## Root Cause
1. Missing `VITE_API_URI` environment variable
2. Incorrect URL construction for static file serving

## Solution Applied
1. **Added fallback API URL**: Updated all components to use `http://localhost:8000/api` as fallback when `VITE_API_URI` is not defined
2. **Fixed URL construction**: Updated image URL construction to properly point to the backend's static file serving endpoint

## Files Modified
- `src/api/init.ts` - Added fallback for API base URL
- `src/components/TemplateForms/AdminPhotoDisplay.tsx` - Fixed image URL construction
- `src/components/Carousel/PhotoThumbnailCarousel.tsx` - Fixed image URL construction  
- `src/components/Forms/FormGeneratorTemplate.tsx` - Fixed file URL construction

## How to Run
1. **Start the backend server** (from sulambi-backend-main directory):
   ```bash
   python server.py
   ```
   The backend will run on `http://localhost:8000`

2. **Start the frontend** (from sulambi-frontend-main directory):
   ```bash
   npm run dev
   ```

3. **Optional: Set environment variable** (create `.env` file):
   ```
   VITE_API_URI=http://localhost:8000/api
   ```

## Backend Static File Serving
The backend serves uploaded images via the `/uploads/<filename>` route, which is properly configured in `server.py`:
```python
@Server.route("/uploads/<path:path>")
def staticFileHost(path):
    return send_from_directory("uploads", path)
```

## Image URL Construction
Images are now properly constructed as:
- Base URL: `http://localhost:8000` (removed `/api` suffix)
- Full URL: `http://localhost:8000/uploads/{filename}?t={timestamp}`

The timestamp parameter ensures fresh loading and prevents caching issues.






