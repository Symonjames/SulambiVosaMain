# Sulambi VMS Deployment Guide

## Step-by-Step Hosting Setup

### Prerequisites
- A VPS (Virtual Private Server) - Recommended: DigitalOcean ($6/month)
- Domain name (optional but recommended)
- SSH access to your server

---

## Part 1: Server Setup

### 1. Connect to Your Server
```bash
ssh root@YOUR_SERVER_IP
```

### 2. Update System
```bash
apt update && apt upgrade -y
```

### 3. Install Required Software
```bash
# Python and pip
apt install python3 python3-pip python3-venv -y

# Node.js (for frontend build)
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# Nginx (web server)
apt install nginx -y

# PostgreSQL (database)
apt install postgresql postgresql-contrib -y

# Git
apt install git -y
```

### 4. Set Up PostgreSQL Database
```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL prompt, run:
CREATE DATABASE sulambi_db;
CREATE USER sulambi_user WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE sulambi_db TO sulambi_user;
\q
```

---

## Part 2: Backend Deployment

### 1. Create Application Directory
```bash
mkdir -p /var/www/sulambi-backend
cd /var/www/sulambi-backend
```

### 2. Upload Your Code
**Option A: Using Git**
```bash
git clone YOUR_GITHUB_REPO_URL .
cd sulambi-backend-main
```

**Option B: Using SFTP/SCP**
- Use FileZilla or WinSCP to upload files to `/var/www/sulambi-backend`

### 3. Set Up Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create Environment File
```bash
nano .env
```

Add these lines:
```
DATABASE_URL=postgresql://sulambi_user:your_secure_password_here@localhost/sulambi_db
DEBUG=False
FLASK_ENV=production
HOST=0.0.0.0
PORT=8000
AUTOMAILER_EMAIL=your-email@example.com
AUTOMAILER_PASSW=your-password
```

Save: `Ctrl+X`, then `Y`, then `Enter`

### 5. Initialize Database
```bash
source venv/bin/activate
python server.py --init
```

### 6. Test Backend
```bash
source venv/bin/activate
gunicorn -w 4 -b 0.0.0.0:8000 server:app
```

Press `Ctrl+C` to stop. If it works, continue!

---

## Part 3: Set Up Gunicorn Service

### 1. Create Systemd Service
```bash
nano /etc/systemd/system/sulambi-backend.service
```

Add this content:
```ini
[Unit]
Description=Sulambi VMS Backend
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/sulambi-backend
Environment="PATH=/var/www/sulambi-backend/venv/bin"
ExecStart=/var/www/sulambi-backend/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 server:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Save and exit.

### 2. Start the Service
```bash
systemctl daemon-reload
systemctl enable sulambi-backend
systemctl start sulambi-backend
systemctl status sulambi-backend
```

---

## Part 4: Configure Nginx

### 1. Create Nginx Configuration
```bash
nano /etc/nginx/sites-available/sulambi
```

Add this content (replace `your-domain.com` with your domain or server IP):
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend (static files)
    location / {
        root /var/www/sulambi-frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Uploads
    location /uploads {
        alias /var/www/sulambi-backend/uploads;
    }
}
```

### 2. Enable Site
```bash
ln -s /etc/nginx/sites-available/sulambi /etc/nginx/sites-enabled/
nginx -t  # Test configuration
systemctl restart nginx
```

---

## Part 5: Frontend Deployment

### 1. Build Frontend Locally (on your computer)
```bash
cd sulambi-frontend-main
npm install
npm run build
```

### 2. Upload Build Files
Upload the `dist` folder to `/var/www/sulambi-frontend/dist` on your server

### 3. Update API URL
Before building, update your frontend API URL in `.env.production`:
```
VITE_API_URL=http://your-domain.com/api
```

Then rebuild and upload again.

---

## Part 6: SSL Certificate (HTTPS) - Optional but Recommended

### Install Certbot
```bash
apt install certbot python3-certbot-nginx -y
```

### Get SSL Certificate
```bash
certbot --nginx -d your-domain.com -d www.your-domain.com
```

Follow the prompts. Certbot will automatically update your Nginx config.

---

## Part 7: Firewall Setup

### Configure UFW Firewall
```bash
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

---

## Maintenance Commands

### View Backend Logs
```bash
journalctl -u sulambi-backend -f
```

### Restart Backend
```bash
systemctl restart sulambi-backend
```

### Restart Nginx
```bash
systemctl restart nginx
```

### Update Code
```bash
cd /var/www/sulambi-backend
source venv/bin/activate
git pull  # or upload new files
pip install -r requirements.txt
systemctl restart sulambi-backend
```

---

## Troubleshooting

### Backend Not Starting
```bash
# Check logs
journalctl -u sulambi-backend -n 50

# Check if port is in use
netstat -tulpn | grep 8000
```

### Database Connection Issues
```bash
# Test PostgreSQL connection
sudo -u postgres psql -d sulambi_db -U sulambi_user
```

### Nginx Errors
```bash
# Check Nginx error log
tail -f /var/log/nginx/error.log

# Test configuration
nginx -t
```

---

## Cost Breakdown

- **VPS (DigitalOcean)**: $6/month
- **Domain Name**: ~$10-15/year (optional)
- **Total**: ~$6-7/month

---

## Security Checklist

- [ ] Changed default SSH port (optional)
- [ ] Set up SSH key authentication
- [ ] Firewall configured
- [ ] Strong database password
- [ ] SSL certificate installed
- [ ] Regular backups configured
- [ ] Environment variables secured

---

## Backup Strategy

### Database Backup
```bash
# Create backup script
nano /root/backup-db.sh
```

Add:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U sulambi_user sulambi_db > /root/backups/db_$DATE.sql
```

### Set Up Cron Job
```bash
crontab -e
# Add: 0 2 * * * /root/backup-db.sh
```

---

## Support

If you encounter issues:
1. Check logs: `journalctl -u sulambi-backend -f`
2. Verify environment variables
3. Test database connection
4. Check Nginx configuration

Good luck with your deployment! 🚀









