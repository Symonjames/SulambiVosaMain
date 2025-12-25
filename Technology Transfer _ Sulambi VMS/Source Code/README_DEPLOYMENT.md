# Quick Start: Deploy to Render

This repository is ready for deployment to Render! 🚀

## Repository Structure

```
SULAMBI/
├── Technology Transfer _ Sulambi VMS/
│   └── Source Code/              ← Render Blueprint Root Directory
│       ├── render.yaml           ← Render configuration
│       ├── RENDER_DEPLOYMENT.md  ← Full deployment guide
│       ├── DEPLOYMENT_CHECKLIST.md
│       ├── sulambi-backend-main/
│       │   └── sulambi-backend-main/
│       │       ├── server.py
│       │       ├── requirements.txt
│       │       └── start.sh
│       └── sulambi-frontend-main/
│           └── sulambi-frontend-main/
│               ├── package.json
│               └── build.sh
```

## Quick Deploy (3 Steps)

### 1. Connect Repository to Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Blueprint"**
3. Connect repository: `https://github.com/Symonjames/SULAMBI`
4. **Set Root Directory**: `Technology Transfer _ Sulambi VMS/Source Code`
5. Click **"Apply"**

### 2. Configure Environment Variables

After services are created, go to each service's **Environment** tab:

**Backend (`sulambi-backend`)**:
- `AUTOMAILER_EMAIL`: Your email
- `AUTOMAILER_PASSW`: Email password

**Frontend (`sulambi-frontend`)**:
- `VITE_API_URI`: `https://sulambi-backend.onrender.com/api`
  - ⚠️ **Set this BEFORE first build!**
  - Replace `sulambi-backend` with your actual backend service name

### 3. Deploy!

Render will automatically:
- ✅ Create PostgreSQL database
- ✅ Build and deploy backend
- ✅ Build and deploy frontend
- ✅ Initialize database tables

## Default Login Credentials

After deployment, use these to log in (change immediately!):

- **Admin**: `Admin` / `sulambi@2024`
- **Officer**: `Sulambi-Officer` / `password@2024`

## Important Notes

⚠️ **File Storage**: Uploaded files are lost on service restart (ephemeral filesystem). Consider cloud storage for production.

📖 **Full Guide**: See [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md) for detailed instructions.

✅ **Checklist**: Use [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) to track your deployment.

## Support

- Repository: https://github.com/Symonjames/SULAMBI
- Render Docs: https://render.com/docs
- Issues: Open an issue on GitHub

