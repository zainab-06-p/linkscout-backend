# 🚀 LinkScout Complete Deployment Guide

## Overview
This guide will help you deploy LinkScout globally for free using:
- **Frontend (Next.js)**: Vercel (Free)
- **Backend (Python Flask)**: Render.com (Free)
- **Extension**: Chrome Web Store ($5 one-time)

---

## 📦 Part 1: Deploy Backend on Render.com (Free)

### Step 1: Prepare Backend for Deployment

1. **Create a `requirements.txt` file** (if not already correct):
```bash
cd D:\LinkScout
```

Create/update `requirements.txt`:
```txt
flask==3.0.0
flask-cors==4.0.0
torch==2.1.0
transformers==4.35.0
pillow==10.1.0
requests==2.31.0
beautifulsoup4==4.12.2
numpy==1.24.3
```

2. **Create a `render.yaml` file** in `D:\LinkScout\`:
```yaml
services:
  - type: web
    name: linkscout-backend
    runtime: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python combined_server.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: PORT
        value: 5000
```

3. **Update `combined_server.py` to use environment PORT**:

Find the line at the bottom of `combined_server.py`:
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

Replace with:
```python
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

4. **Create `.gitignore`** in `D:\LinkScout\`:
```
__pycache__/
*.pyc
*.pyo
models_cache/
D:\huggingface_cache/
.env
*.log
```

### Step 2: Push to GitHub

1. **Initialize Git** (if not already):
```powershell
cd D:\LinkScout
git init
git add .
git commit -m "Initial commit for deployment"
```

2. **Create GitHub repository**:
   - Go to https://github.com/new
   - Name it `linkscout-backend`
   - Don't initialize with README
   - Click "Create repository"

3. **Push to GitHub**:
```powershell
git remote add origin https://github.com/YOUR_USERNAME/linkscout-backend.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy on Render.com

1. **Sign up**: Go to https://render.com and sign up with GitHub
2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository `linkscout-backend`
   - Click "Connect"

3. **Configure Settings**:
   - **Name**: `linkscout-backend`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python combined_server.py`
   - **Instance Type**: `Free`

4. **Environment Variables**:
   - Add: `PYTHON_VERSION` = `3.11.0`
   - Add: `GROQ_API_KEY` = `your_groq_api_key_here`
   - Add: `GOOGLE_API_KEY` = `your_google_api_key_here` (optional)
   - Add: `GOOGLE_CSE_ID` = `your_google_cse_id_here` (optional)

5. **Click "Create Web Service"**

6. **Wait for deployment** (15-20 minutes for first deploy due to model downloads)

7. **Get your backend URL**: 
   - Example: `https://linkscout-backend.onrender.com`
   - **SAVE THIS URL** - you'll need it for frontend!

⚠️ **Important Notes**:
- Free tier sleeps after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds to wake up
- 750 hours/month free (more than enough)

---

## 🌐 Part 2: Deploy Frontend on Vercel (Free)

### Step 1: Prepare Frontend for Deployment

1. **Update API URLs** in frontend to use production backend:

Edit `D:\LinkScout\web_interface\LinkScout\app\search\page.tsx`:

Find all instances of `http://localhost:5000` and replace with your Render backend URL:
```typescript
// Replace this:
const response = await fetch('http://localhost:5000/analyze', {

// With this (use YOUR Render URL):
const response = await fetch('https://linkscout-backend.onrender.com/analyze', {
```

Also update in:
- `app/search/page.tsx` (feedback endpoint)
- `app/api/download-extension/route.ts` (if exists)

2. **Create `vercel.json`** in `D:\LinkScout\web_interface\LinkScout\`:
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://linkscout-backend.onrender.com/:path*"
    }
  ]
}
```

3. **Update environment variables**:

Create `.env.production` in `D:\LinkScout\web_interface\LinkScout\`:
```env
NEXT_PUBLIC_API_URL=https://linkscout-backend.onrender.com
```

### Step 2: Push Frontend to GitHub

1. **Create new repository**:
```powershell
cd D:\LinkScout\web_interface\LinkScout
git init
git add .
git commit -m "Initial frontend commit"
```

2. **Create GitHub repo**:
   - Go to https://github.com/new
   - Name: `linkscout-frontend`
   - Click "Create repository"

3. **Push**:
```powershell
git remote add origin https://github.com/YOUR_USERNAME/linkscout-frontend.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy on Vercel

1. **Sign up**: Go to https://vercel.com and sign up with GitHub

2. **Import Project**:
   - Click "Add New..." → "Project"
   - Select `linkscout-frontend` repository
   - Click "Import"

3. **Configure**:
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `./` (leave as is)
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
   - **Install Command**: `npm install`

4. **Environment Variables**:
   - Add: `NEXT_PUBLIC_API_URL` = `https://linkscout-backend.onrender.com`

5. **Click "Deploy"**

6. **Wait 2-5 minutes** for deployment

7. **Get your live URL**:
   - Example: `https://linkscout-frontend.vercel.app`
   - You can add custom domain later (free)

---

## 🧩 Part 3: Publish Chrome Extension

### Step 1: Prepare Extension Package

1. **Update extension to use production backend**:

Edit `D:\LinkScout\extension\popup.js`:

Find:
```javascript
const API_URL = 'http://localhost:5000';
```

Replace with:
```javascript
const API_URL = 'https://linkscout-backend.onrender.com';
```

2. **Update manifest version** in `D:\LinkScout\extension\manifest.json`:
```json
{
  "manifest_version": 3,
  "name": "LinkScout - AI Fact Checker",
  "version": "1.0.0",
  "description": "AI-powered misinformation detection with 8-phase analysis system",
  ...
}
```

3. **Create ZIP file**:
```powershell
cd D:\LinkScout
Compress-Archive -Path extension\* -DestinationPath linkscout-extension-v1.0.0.zip
```

### Step 2: Publish to Chrome Web Store

1. **Create Developer Account**:
   - Go to https://chrome.google.com/webstore/devconsole
   - Pay $5 one-time registration fee
   - Complete verification

2. **Upload Extension**:
   - Click "New Item"
   - Upload `linkscout-extension-v1.0.0.zip`
   - Fill in details:
     * **Name**: LinkScout - AI Fact Checker
     * **Summary**: AI-powered misinformation detection with 8-phase analysis
     * **Description**: (Copy from your README.md)
     * **Category**: Productivity
     * **Language**: English

3. **Add Assets**:
   - **Icon**: 128x128px PNG (create one)
   - **Screenshots**: 1280x800px (take screenshots of extension in action)
   - **Promotional images**: (optional)

4. **Privacy Practices**:
   - Data usage: Check what data you collect
   - Privacy policy: Create one (use template from https://app-privacy-policy-generator.nisrulz.com/)

5. **Submit for Review**:
   - Click "Submit for Review"
   - Wait 1-3 days for approval
   - Once approved, it's live globally!

### Step 3: Distribute Extension URL

After approval, you'll get:
- **Chrome Web Store URL**: `https://chrome.google.com/webstore/detail/YOUR-EXTENSION-ID`
- Share this link for users to install

---

## 🔄 Alternative: Manual Installation (Before Publishing)

Users can install the extension manually:

1. Download ZIP from your website
2. Extract to folder
3. Open `chrome://extensions`
4. Enable "Developer mode"
5. Click "Load unpacked"
6. Select extracted folder

---

## 📊 Deployment Checklist

### Backend (Render.com)
- [ ] Create `requirements.txt`
- [ ] Create `render.yaml`
- [ ] Update PORT handling in `combined_server.py`
- [ ] Push to GitHub
- [ ] Deploy on Render
- [ ] Test API endpoints
- [ ] Save backend URL

### Frontend (Vercel)
- [ ] Update all API URLs to production
- [ ] Create `vercel.json`
- [ ] Create `.env.production`
- [ ] Push to GitHub
- [ ] Deploy on Vercel
- [ ] Test website functionality
- [ ] Save frontend URL

### Extension (Chrome Web Store)
- [ ] Update API URL in `popup.js`
- [ ] Create ZIP package
- [ ] Pay $5 developer fee
- [ ] Submit to Chrome Web Store
- [ ] Wait for approval (1-3 days)
- [ ] Share extension URL

---

## 🔧 Post-Deployment Configuration

### Update Extension Download Link

Edit `D:\LinkScout\web_interface\LinkScout\app\extensions\page.tsx`:

Find the download function and update to point to Chrome Web Store:
```typescript
const handleDownloadExtension = () => {
  // Redirect to Chrome Web Store
  window.open('https://chrome.google.com/webstore/detail/YOUR-EXTENSION-ID', '_blank');
};
```

### Monitor Usage

**Backend (Render)**:
- Dashboard: https://dashboard.render.com
- View logs, uptime, traffic
- Free tier: 750 hours/month

**Frontend (Vercel)**:
- Dashboard: https://vercel.com/dashboard
- View analytics, deployments
- Free tier: Unlimited bandwidth

**Extension**:
- Chrome Web Store Developer Dashboard
- View installs, ratings, reviews

---

## ⚠️ Important Limitations on Free Tier

### Render.com Backend:
- ✅ 750 hours/month (plenty)
- ⚠️ Sleeps after 15 min inactivity (30-60s wake-up time)
- ⚠️ 512MB RAM (might need optimization)
- ⚠️ Model loading takes time on first request

### Vercel Frontend:
- ✅ Unlimited bandwidth
- ✅ 100GB bandwidth/month
- ✅ Fast global CDN
- ✅ Automatic HTTPS

### Solutions for Backend Sleep Issue:
1. **Cron job ping** (free):
   - Use https://uptimerobot.com (free)
   - Ping your backend every 14 minutes
   - Keeps it awake 24/7

2. **Upgrade to paid** ($7/month):
   - No sleep
   - Better performance
   - More RAM

---

## 🚀 Going Live Checklist

1. **Test Everything**:
   - [ ] Backend API responds
   - [ ] Frontend loads and displays
   - [ ] Extension connects to backend
   - [ ] Analysis works end-to-end
   - [ ] Sources display correctly
   - [ ] RL feedback works

2. **Security**:
   - [ ] Remove debug mode
   - [ ] Secure API keys (use environment variables)
   - [ ] Add rate limiting
   - [ ] Enable CORS only for your domain

3. **Performance**:
   - [ ] Optimize model loading
   - [ ] Add caching
   - [ ] Compress responses
   - [ ] Use CDN for static assets

4. **Monitoring**:
   - [ ] Set up error tracking (Sentry - free tier)
   - [ ] Monitor uptime (UptimeRobot)
   - [ ] Track usage analytics

---

## 💡 Next Steps

1. **Start with Backend**: Deploy on Render first
2. **Then Frontend**: Deploy on Vercel with correct backend URL
3. **Finally Extension**: Publish to Chrome Web Store
4. **Share URLs**: Website + Extension links

Good luck with deployment! 🚀

---

## 🆘 Troubleshooting

### Backend not responding:
- Check Render logs
- Verify environment variables
- Check model loading errors

### Frontend can't connect:
- Verify backend URL is correct
- Check CORS settings
- Test API endpoints directly

### Extension not working:
- Check API URL in popup.js
- Verify manifest permissions
- Test in incognito mode

Need help? Check:
- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- Chrome Extension Docs: https://developer.chrome.com/docs/extensions/
