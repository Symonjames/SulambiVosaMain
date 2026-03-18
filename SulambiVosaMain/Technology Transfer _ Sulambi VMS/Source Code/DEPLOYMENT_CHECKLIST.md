# Render Deployment Quick Checklist

Use this checklist to ensure a smooth deployment to Render.

## Pre-Deployment

- [ ] Code is pushed to Git repository (GitHub/GitLab/Bitbucket)
- [ ] All dependencies are listed in `requirements.txt` (backend) and `package.json` (frontend)
- [ ] Tested locally to ensure everything works

## Deployment Steps

### 1. Connect Repository to Render
- [ ] Create Render account
- [ ] Create new Blueprint from repository
- [ ] Render detects `render.yaml` automatically

### 2. Configure Backend Service
- [ ] Service name: `sulambi-backend` (or your preferred name)
- [ ] Set `AUTOMAILER_EMAIL` environment variable
- [ ] Set `AUTOMAILER_PASSW` environment variable
- [ ] Verify `DATABASE_URL` is automatically connected
- [ ] Verify `PORT` is automatically set

### 3. Configure Frontend Service
- [ ] Service name: `sulambi-frontend` (or your preferred name)
- [ ] **BEFORE FIRST BUILD**: Set `VITE_API_URI` to `https://your-backend-name.onrender.com/api`
- [ ] Replace `your-backend-name` with actual backend service name

### 4. Database Service
- [ ] Database name: `sulambi-database` (or your preferred name)
- [ ] Verify database is created and connected to backend

### 5. First Deployment
- [ ] Monitor build logs for errors
- [ ] Wait for services to finish building
- [ ] Check backend is running (may take 1-2 minutes on first deploy)
- [ ] Check frontend is accessible

### 6. Post-Deployment Verification
- [ ] Backend API is accessible
- [ ] Frontend loads correctly
- [ ] Frontend can connect to backend API
- [ ] Test login with default credentials:
  - Admin: `Admin` / `sulambi@2024`
  - Officer: `Sulambi-Officer` / `password@2024`
- [ ] **CHANGE DEFAULT PASSWORDS IMMEDIATELY**

## Important Reminders

### ⚠️ Critical Issues to Address

1. **File Storage**: Uploaded files will be lost on service restart (ephemeral filesystem)
   - [ ] Plan to implement cloud storage (S3, Cloudinary, etc.)
   - [ ] Or upgrade to paid plan with persistent disk

2. **PostgreSQL Compatibility**: Current `tableInitializer.py` uses SQLite syntax
   - [ ] Monitor database initialization logs
   - [ ] If errors occur, may need to update SQL syntax for PostgreSQL
   - [ ] Or use SQLite by setting `DB_PATH` and removing `DATABASE_URL`

3. **Environment Variables**: 
   - [ ] `VITE_API_URI` must be set BEFORE first frontend build
   - [ ] If changed later, frontend must be rebuilt

4. **Service URLs**: 
   - [ ] Note your backend URL: `https://your-backend-name.onrender.com`
   - [ ] Note your frontend URL: `https://your-frontend-name.onrender.com`
   - [ ] Update `VITE_API_URI` if backend URL changes

## Troubleshooting

If something goes wrong:

1. **Check Build Logs**: Look for specific error messages
2. **Check Runtime Logs**: See what's happening when services run
3. **Verify Environment Variables**: Ensure all required vars are set
4. **Database Issues**: Check if tables were created successfully
5. **API Connection**: Verify `VITE_API_URI` matches backend URL exactly

## Next Steps After Deployment

- [ ] Change default admin/officer passwords
- [ ] Configure custom domain (optional)
- [ ] Set up monitoring/alerts
- [ ] Implement cloud storage for file uploads
- [ ] Update CORS settings to restrict to your frontend domain
- [ ] Set up automated backups for database

## Support Resources

- Full deployment guide: See `RENDER_DEPLOYMENT.md`
- Render documentation: https://render.com/docs
- Service logs: Available in Render dashboard












