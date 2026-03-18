# Render Deployment Guide for Sulambi VMS

This guide will help you deploy the Sulambi VMS application to Render.

## Prerequisites

1. A Render account (sign up at https://render.com)
2. Your code pushed to a Git repository (GitHub, GitLab, or Bitbucket)
3. Basic understanding of environment variables

## Project Structure

```
Technology Transfer _ Sulambi VMS/
├── Source Code/
│   ├── render.yaml                    # Render configuration file
│   ├── sulambi-backend-main/
│   │   └── sulambi-backend-main/
│   │       ├── server.py
│   │       ├── requirements.txt
│   │       ├── start.sh              # Startup script
│   │       └── ...
│   └── sulambi-frontend-main/
│       └── sulambi-frontend-main/
│           ├── package.json
│           ├── vite.config.ts
│           └── ...
```

## Deployment Steps

### Step 1: Connect Your Repository

1. Log in to Render dashboard
2. Click "New +" and select "Blueprint"
3. Connect your Git repository: `https://github.com/Symonjames/SULAMBI`
4. **Important**: Set the Root Directory to: `Technology Transfer _ Sulambi VMS/Source Code`
   - This is where the `render.yaml` file is located
5. Render will automatically detect the `render.yaml` file and create the services

### Step 2: Configure Environment Variables

**⚠️ IMPORTANT**: Configure environment variables **BEFORE** the first build, especially for the frontend service.

After the services are created, you'll need to set up environment variables:

#### Backend Service (`sulambi-backend`)

Go to your backend service → Environment tab and configure:

- `AUTOMAILER_EMAIL`: Your email for automated mailings
- `AUTOMAILER_PASSW`: Password for the email account
- `DEBUG`: Set to `"False"` for production

The following are automatically set by Render:
- `DATABASE_URL`: Automatically connected from the database service
- `PORT`: Automatically set by Render
- `HOST`: Set to `0.0.0.0`

#### Frontend Service (`sulambi-frontend`)

**⚠️ CRITICAL**: Set this **BEFORE** the first build, as Vite embeds environment variables at build time.

Go to your frontend service → Environment tab and set:

- `VITE_API_URI`: Set this to your backend URL + `/api`
  - Example: `https://sulambi-backend.onrender.com/api`
  - **Important**: 
    - Replace `sulambi-backend` with your actual backend service name
    - Set this **before** triggering the first build
    - If you change this later, you'll need to rebuild the frontend

### Step 3: Database Initialization

The backend will automatically initialize the database on first startup using the `start.sh` script.

**Important Note**: The current `tableInitializer.py` uses SQLite-specific syntax. For PostgreSQL (which Render uses), you may need to update the table creation statements. The main differences are:

- SQLite: `INTEGER PRIMARY KEY AUTOINCREMENT`
- PostgreSQL: `SERIAL PRIMARY KEY` or `BIGSERIAL PRIMARY KEY`

If you encounter database initialization errors, you may need to:
1. Update `app/database/tableInitializer.py` to use PostgreSQL-compatible syntax
2. Or use SQLite by setting `DB_PATH` and not using `DATABASE_URL`

### Step 4: Verify Deployment

1. **Backend**: Check that the backend service is running
   - Visit: `https://your-backend-name.onrender.com`
   - You should see a response or CORS error (which is normal for API)

2. **Frontend**: Visit your frontend URL
   - Should load the React application
   - Check browser console for API connection errors

3. **Database**: The database should be automatically created and initialized

## Service URLs

After deployment, you'll have:

- **Backend API**: `https://sulambi-backend.onrender.com`
- **Frontend**: `https://sulambi-frontend.onrender.com`
- **Database**: Internal connection (not publicly accessible)

## Default Accounts

After database initialization, the following accounts are created:

- **Admin**: 
  - Username: `Admin`
  - Password: `sulambi@2024`

- **Officer**:
  - Username: `Sulambi-Officer`
  - Password: `password@2024`

**⚠️ IMPORTANT**: Change these passwords immediately after first login!

## Troubleshooting

### Backend Issues

1. **Database Connection Errors**
   - Verify `DATABASE_URL` is set correctly
   - Check database service is running
   - Review backend logs for connection errors

2. **Import Errors**
   - Ensure all dependencies are in `requirements.txt`
   - Check Python version matches (3.11.0)

3. **Port Issues**
   - Render automatically sets `PORT` environment variable
   - Ensure your app uses `$PORT` or `os.getenv("PORT")`

### Frontend Issues

1. **API Connection Errors**
   - Verify `VITE_API_URI` is set correctly
   - Check CORS settings in backend
   - Ensure backend URL includes `/api` suffix

2. **Build Errors**
   - Check Node.js version compatibility
   - Review build logs for specific errors
   - Ensure all dependencies are in `package.json`

### Database Issues

1. **Table Creation Errors**
   - Check if `tableInitializer.py` uses PostgreSQL-compatible syntax
   - Review database logs
   - May need to manually run initialization

2. **Connection String Issues**
   - Verify `DATABASE_URL` format
   - Check database credentials

## Manual Database Initialization

If automatic initialization fails, you can manually initialize:

1. SSH into your backend service (if available)
2. Or use Render's shell feature
3. Run: `python server.py --init`

## Updating the Application

1. Push changes to your Git repository
2. Render will automatically detect and deploy changes
3. Monitor the deployment logs for any issues

## Cost Considerations

- **Free Tier**: 
  - Services spin down after 15 minutes of inactivity
  - First request after spin-down may be slow
  - Database has limited storage

- **Paid Plans**: 
  - Services stay running 24/7
  - Better performance
  - More database storage

## Security Recommendations

1. **Change Default Passwords**: Immediately change default admin/officer passwords
2. **Environment Variables**: Never commit sensitive data to Git
3. **CORS**: Update CORS settings to only allow your frontend domain
4. **HTTPS**: Render provides HTTPS by default
5. **Database**: Use strong database passwords (auto-generated by Render)

## Additional Configuration

### Custom Domain

1. Go to your service settings
2. Add custom domain
3. Update DNS records as instructed
4. Update `VITE_API_URI` if backend domain changes

### Environment-Specific Settings

You can create separate services for staging/production:
- Use different `render.yaml` files or
- Manually create services with different configurations

## Support

- Render Documentation: https://render.com/docs
- Render Community: https://community.render.com
- Check service logs in Render dashboard for detailed error messages

## Important Notes

### File Storage Limitation

**⚠️ CRITICAL**: Render's filesystem is **ephemeral**, meaning:
- Files uploaded to the `uploads/` directory will be **lost** when the service restarts
- This includes images, documents, and any other uploaded files
- Services on the free tier spin down after 15 minutes of inactivity, causing data loss

**Recommended Solutions**:
1. **Use Cloud Storage** (Recommended for production):
   - AWS S3
   - Google Cloud Storage
   - Cloudinary (for images)
   - Update `app/utils/multipartFileWriter.py` to upload to cloud storage instead of local filesystem

2. **Use Render Disk** (Paid feature):
   - Provides persistent storage
   - Files survive service restarts
   - Requires a paid plan

3. **Store file references only**:
   - Store files in external storage
   - Store only URLs/paths in database
   - Serve files from external storage

### Other Notes

- The `render.yaml` file uses the free tier by default
- Services may take a few minutes to build and deploy initially
- Database initialization happens on first startup
- Make sure to set `VITE_API_URI` correctly for frontend-backend communication
- Default passwords should be changed immediately after deployment

