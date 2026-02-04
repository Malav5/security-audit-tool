# 🚀 Render Deployment Guide

## Overview
This guide will help you deploy your Security Audit Tool to Render with full Selenium support.

## 📋 Prerequisites

1. **Render Account**: Sign up at https://render.com
2. **GitHub Repository**: Push your code to GitHub
3. **Supabase Project**: Have your Supabase credentials ready

## 🎯 Deployment Options

### Option 1: Using render.yaml (Recommended)

This is the easiest method - Render will automatically detect and deploy both services.

#### Step 1: Push to GitHub
```bash
cd /Users/arjunjoshi/Desktop/Malav/security-audit-tool
git add .
git commit -m "Add Selenium support and email templates"
git push origin main
```

#### Step 2: Connect to Render
1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml`
5. Click **"Apply"**

#### Step 3: Configure Environment Variables
Render will create two services. For the **backend service**, add:

| Variable | Value | Notes |
|----------|-------|-------|
| `SUPABASE_URL` | Your Supabase URL | From Supabase dashboard |
| `SUPABASE_KEY` | Your Supabase anon key | From Supabase dashboard |
| `CHROME_BIN` | `/usr/bin/google-chrome-stable` | Auto-set in render.yaml |
| `CHROMEDRIVER_PATH` | `/usr/local/bin/chromedriver` | Auto-set in render.yaml |

#### Step 4: Deploy
- Render will automatically build and deploy both services
- Backend: Python service with Selenium/Chrome
- Frontend: Static site

---

### Option 2: Using Dockerfile (Alternative)

If you prefer Docker-based deployment:

#### Step 1: Create Web Service
1. Go to Render Dashboard
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `security-audit-backend`
   - **Region**: Oregon (or closest to you)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Docker
   - **Dockerfile Path**: `../Dockerfile`
   - **Plan**: Starter ($7/month)

#### Step 2: Add Environment Variables
Same as Option 1 above.

#### Step 3: Deploy Frontend
1. Click **"New +"** → **"Static Site"**
2. Connect repository
3. Configure:
   - **Name**: `security-audit-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

---

## ⚙️ Configuration Details

### Backend Service Configuration

**Build Command** (from render.yaml):
```bash
# Install Chrome
apt-get update
apt-get install -y wget gnupg unzip
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
apt-get update
apt-get install -y google-chrome-stable

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

**Start Command**:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Frontend Service Configuration

**Build Command**:
```bash
npm install && npm run build
```

**Publish Directory**: `dist`

**Rewrite Rules**: All routes → `/index.html` (for SPA routing)

---

## 🔒 Environment Variables Setup

### Required Variables

1. **SUPABASE_URL**
   - Get from: Supabase Dashboard → Settings → API
   - Format: `https://xxxxx.supabase.co`

2. **SUPABASE_KEY**
   - Get from: Supabase Dashboard → Settings → API → anon/public key
   - Format: Long string starting with `eyJ...`

### Optional Variables (Auto-configured)

- `CHROME_BIN`: Path to Chrome binary
- `CHROMEDRIVER_PATH`: Path to ChromeDriver
- `PYTHON_VERSION`: 3.11.0
- `NODE_VERSION`: 18.17.0

---

## 🧪 Testing Deployment

### 1. Check Backend Health
```bash
curl https://your-backend.onrender.com/
# Should return: {"message": "CyberSecure API with Supabase is Running."}
```

### 2. Test Scan Endpoint
```bash
curl -X POST https://your-backend.onrender.com/generate-audit \
  -H "Content-Type: application/json" \
  -d '{"url": "example.com"}'
```

### 3. Test Frontend
- Visit: `https://your-frontend.onrender.com`
- Try running a scan
- Test sign-up/sign-in flow
- Verify PDF download (requires sign-in)

---

## 🐛 Troubleshooting

### Issue: Chrome/ChromeDriver not found

**Solution**: Verify build command in render.yaml includes Chrome installation:
```yaml
buildCommand: |
  apt-get update
  apt-get install -y google-chrome-stable
  pip install -r requirements.txt
```

### Issue: Selenium scan fails

**Check logs**:
```bash
# In Render dashboard, go to your service → Logs
```

**Common fixes**:
1. Ensure `--no-sandbox` flag is set (already in selenium_scanner.py)
2. Verify Chrome is installed: Add to build command:
   ```bash
   google-chrome --version
   ```

### Issue: Build fails

**Solution**: Check Python version compatibility
```yaml
envVars:
  - key: PYTHON_VERSION
    value: 3.11.0
```

### Issue: Frontend can't connect to backend

**Solution**: Update API base URL in `frontend/src/api.js`:
```javascript
const API_BASE_URL = 'https://your-backend.onrender.com';
```

### Issue: CORS errors

**Solution**: Already configured in `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update to specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

For production, update to:
```python
allow_origins=["https://your-frontend.onrender.com"],
```

---

## 📊 Resource Requirements

### Backend Service

| Plan | RAM | CPU | Price | Suitable For |
|------|-----|-----|-------|--------------|
| Starter | 512 MB | 0.5 CPU | $7/mo | Testing, low traffic |
| Standard | 2 GB | 1 CPU | $25/mo | Production, moderate traffic |
| Pro | 4 GB | 2 CPU | $85/mo | High traffic, many scans |

**Recommendation**: Start with **Starter** plan, upgrade if needed.

**Note**: Selenium scans use ~200-500 MB RAM per scan. Limit concurrent scans to 1-2 on Starter plan.

### Frontend Service

| Plan | Price | Suitable For |
|------|-------|--------------|
| Free | $0/mo | Testing, personal use |
| Starter | $7/mo | Production, custom domain |

**Recommendation**: **Free** plan is sufficient for frontend.

---

## 🔧 Performance Optimization

### 1. Limit Concurrent Selenium Scans

Add to `backend/main.py`:
```python
from asyncio import Semaphore

# Limit to 2 concurrent Selenium scans
selenium_semaphore = Semaphore(2)

@app.post("/generate-audit")
async def generate_audit(...):
    if use_selenium:
        async with selenium_semaphore:
            # Run Selenium scan
            ...
```

### 2. Add Caching

Install Redis on Render and cache scan results:
```python
# Cache results for 1 hour
cache_key = f"scan:{hostname}"
cached_result = redis.get(cache_key)
if cached_result:
    return json.loads(cached_result)
```

### 3. Use Background Jobs

For long scans, use background tasks:
```python
@app.post("/generate-audit")
async def generate_audit(background_tasks: BackgroundTasks, ...):
    background_tasks.add_task(run_scan_async, url, user_id)
    return {"status": "queued", "scan_id": scan_id}
```

---

## 🌐 Custom Domain Setup

### 1. Add Custom Domain to Frontend
1. Go to Frontend service → Settings → Custom Domains
2. Add your domain (e.g., `cybersecure.yourdomain.com`)
3. Update DNS records as instructed by Render

### 2. Update Backend CORS
In `backend/main.py`:
```python
allow_origins=["https://cybersecure.yourdomain.com"],
```

### 3. Update Frontend API URL
In `frontend/src/api.js`:
```javascript
const API_BASE_URL = 'https://api.yourdomain.com';
```

---

## 📈 Monitoring & Logs

### View Logs
1. Go to Render Dashboard
2. Select your service
3. Click **"Logs"** tab
4. Filter by:
   - Deploy logs (build process)
   - Runtime logs (application logs)

### Set Up Alerts
1. Go to Service → Settings → Notifications
2. Add email for:
   - Deploy failures
   - Service crashes
   - High memory usage

### Monitor Performance
```python
# Add logging in main.py
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/generate-audit")
async def generate_audit(...):
    logger.info(f"Scan started for {url}")
    # ... scan logic ...
    logger.info(f"Scan completed in {duration}s")
```

---

## 🔐 Security Best Practices

### 1. Environment Variables
- ✅ Never commit `.env` files
- ✅ Use Render's environment variables
- ✅ Rotate Supabase keys regularly

### 2. CORS Configuration
```python
# Production setting
allow_origins=["https://your-frontend.onrender.com"],
```

### 3. Rate Limiting
Add to `backend/main.py`:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/generate-audit")
@limiter.limit("5/minute")  # 5 scans per minute
async def generate_audit(...):
    ...
```

### 4. HTTPS Only
Render provides free SSL certificates automatically.

---

## 📝 Deployment Checklist

Before deploying:
- [ ] Push code to GitHub
- [ ] Update `frontend/src/api.js` with production backend URL
- [ ] Set up Supabase email templates
- [ ] Configure environment variables in Render
- [ ] Test locally with `docker build` (if using Dockerfile)
- [ ] Review CORS settings
- [ ] Set up custom domain (optional)
- [ ] Configure monitoring/alerts

After deploying:
- [ ] Test backend health endpoint
- [ ] Test scan functionality
- [ ] Test authentication flow
- [ ] Test PDF download
- [ ] Test email confirmation
- [ ] Test Selenium scan (if enabled)
- [ ] Monitor logs for errors
- [ ] Set up backups (Supabase handles this)

---

## 🆘 Support Resources

- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com
- **Selenium Docs**: https://selenium.dev/documentation
- **Supabase Docs**: https://supabase.com/docs

---

## 💡 Quick Commands

### Deploy from CLI
```bash
# Install Render CLI
npm install -g render-cli

# Login
render login

# Deploy
render deploy
```

### View Logs
```bash
render logs -s your-service-name
```

### Restart Service
```bash
render restart -s your-service-name
```

---

**Last Updated**: February 4, 2026  
**Version**: 1.0  
**Author**: CyberSecure India Development Team
