# 🚀 Quick Deployment to Render

## ✅ Files Ready for Deployment

Your application is now fully configured for Render deployment with:
- ✅ `render.yaml` - Automatic service configuration
- ✅ `Dockerfile` - Docker-based deployment (alternative)
- ✅ `.dockerignore` - Optimized Docker builds
- ✅ Selenium/Chrome support built-in
- ✅ Email templates ready
- ✅ PDF authentication enabled

---

## 🎯 Deploy in 3 Steps

### Step 1: Push to GitHub (2 minutes)
```bash
cd /Users/arjunjoshi/Desktop/Malav/security-audit-tool

# Add all files
git add .

# Commit changes
git commit -m "Add Selenium support, email templates, and Render deployment config"

# Push to GitHub
git push origin main
```

### Step 2: Connect to Render (3 minutes)
1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Blueprint"**
3. Select your GitHub repository
4. Render will detect `render.yaml` automatically
5. Click **"Apply"**

### Step 3: Configure Environment (2 minutes)
In the **backend service**, add these environment variables:

| Variable | Value | Where to Find |
|----------|-------|---------------|
| `SUPABASE_URL` | `https://xxxxx.supabase.co` | Supabase Dashboard → Settings → API |
| `SUPABASE_KEY` | `eyJxxx...` | Supabase Dashboard → Settings → API → anon key |

**Done!** 🎉 Render will automatically build and deploy both services.

---

## 📋 What Gets Deployed

### Backend Service
- **Name**: `security-audit-backend`
- **Type**: Python Web Service
- **Features**:
  - ✅ FastAPI server
  - ✅ Google Chrome installed
  - ✅ Selenium support
  - ✅ PDF generation
  - ✅ Email integration
  - ✅ JWT authentication
- **URL**: `https://security-audit-backend.onrender.com`

### Frontend Service
- **Name**: `security-audit-frontend`
- **Type**: Static Site
- **Features**:
  - ✅ React application
  - ✅ Modern UI
  - ✅ Authentication flow
  - ✅ Scan dashboard
- **URL**: `https://security-audit-frontend.onrender.com`

---

## ⚙️ Configuration Details

### render.yaml Highlights

**Backend Build Command**:
```bash
# Installs Chrome + ChromeDriver
apt-get install -y google-chrome-stable
pip install -r requirements.txt
```

**Backend Start Command**:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Frontend Build Command**:
```bash
npm install && npm run build
```

---

## 🧪 Testing After Deployment

### 1. Test Backend
```bash
# Replace with your actual backend URL
curl https://security-audit-backend.onrender.com/

# Should return:
# {"message": "CyberSecure API with Supabase is Running."}
```

### 2. Test Frontend
Visit: `https://security-audit-frontend.onrender.com`
- ✅ Page loads
- ✅ Can enter URL
- ✅ Sign-up works
- ✅ Email confirmation received
- ✅ Scan runs successfully
- ✅ PDF download requires sign-in

### 3. Test Selenium (Optional)
Run a scan and check logs for:
```
[SELENIUM SCANNER] Starting enhanced scan for...
```

---

## 🔧 Post-Deployment Tasks

### 1. Update Frontend API URL (If Needed)
If your backend URL is different, update `frontend/src/api.js`:
```javascript
const API_BASE_URL = 'https://your-actual-backend.onrender.com';
```

### 2. Configure Email Template
1. Go to Supabase Dashboard
2. Navigate to: **Authentication** → **Email Templates**
3. Select: **"Confirm signup"**
4. Copy content from: `backend/email_templates/confirmation_email.html`
5. Paste and **Save**

### 3. Update CORS (Production)
In `backend/main.py`, update for production:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.onrender.com"],  # Your actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. Set Up Custom Domain (Optional)
1. In Render Dashboard → Frontend Service → Settings
2. Add custom domain
3. Update DNS records as instructed
4. Update CORS in backend

---

## 📊 Expected Build Times

| Service | First Build | Subsequent Builds |
|---------|-------------|-------------------|
| Backend | 5-8 minutes | 2-4 minutes |
| Frontend | 2-3 minutes | 1-2 minutes |

**Note**: First build takes longer due to Chrome installation.

---

## 🐛 Common Issues & Fixes

### Issue: Build fails with "Chrome not found"
**Fix**: render.yaml already includes Chrome installation. Check build logs.

### Issue: "Module not found" error
**Fix**: Ensure `requirements.txt` is in `backend/` directory.

### Issue: Frontend can't connect to backend
**Fix**: 
1. Check backend is running: Visit backend URL
2. Update `frontend/src/api.js` with correct backend URL
3. Redeploy frontend

### Issue: Selenium scan fails
**Fix**: Check logs for specific error. Common fixes:
- Ensure `--no-sandbox` flag is set (already in code)
- Verify Chrome installed: Check build logs
- Increase memory if needed (upgrade plan)

---

## 💰 Cost Estimate

### Starter Plan (Recommended for Testing)
- **Backend**: $7/month (Starter plan)
- **Frontend**: $0/month (Free plan)
- **Total**: **$7/month**

### Production Plan (For Higher Traffic)
- **Backend**: $25/month (Standard plan - 2GB RAM)
- **Frontend**: $7/month (Custom domain)
- **Total**: **$32/month**

**Free Trial**: Render offers free trial credits for new users.

---

## 📈 Monitoring

### View Logs
```bash
# In Render Dashboard
1. Select service
2. Click "Logs" tab
3. Filter by Deploy/Runtime
```

### Set Up Alerts
```bash
# In Render Dashboard
1. Service → Settings → Notifications
2. Add email for:
   - Deploy failures
   - Service crashes
   - High memory usage
```

---

## 🔒 Security Checklist

Before going live:
- [ ] Environment variables set (not in code)
- [ ] CORS configured for production domain
- [ ] HTTPS enabled (automatic on Render)
- [ ] Email template configured in Supabase
- [ ] Rate limiting enabled (optional)
- [ ] Monitoring/alerts set up
- [ ] Custom domain configured (optional)

---

## 📞 Need Help?

- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com
- **Full Guide**: See `RENDER_DEPLOYMENT.md`

---

## ✨ You're All Set!

Your application is ready to deploy to Render with:
- ✅ Full Selenium support
- ✅ Email confirmation
- ✅ PDF authentication
- ✅ Production-ready configuration

**Next Step**: Push to GitHub and connect to Render!

---

**Quick Deploy Checklist**:
1. ✅ Files configured
2. ⏳ Push to GitHub
3. ⏳ Connect to Render
4. ⏳ Add environment variables
5. ⏳ Deploy!

**Estimated Total Time**: 10-15 minutes

---

**Last Updated**: February 4, 2026  
**Deployment Version**: 1.0
