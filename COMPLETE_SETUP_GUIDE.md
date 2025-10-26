# LinkScout - Complete Setup Guide

**Smart Analysis. Simple Answers.**

This guide will help you set up and run the complete LinkScout system with both the **web interface** and **browser extension**.

## 🎯 System Overview

LinkScout consists of three main components:

1. **Python Backend Server** (`combined_server.py`) - Handles all AI analysis
2. **Browser Extension** (`extension/`) - Analyze articles directly in your browser
3. **Web Interface** (`web_interface/LinkScout/`) - Modern web app for analysis

**Important**: All three components share the same backend server!

## 📋 Prerequisites

### Required Software

- **Python 3.10+**
- **Node.js 18+** and npm
- **Modern Browser** (Chrome, Edge, Firefox)

### Required Python Packages

All listed in `requirements.txt`. Install with:

```powershell
pip install -r requirements.txt
```

## 🚀 Quick Start (3 Steps)

### Step 1: Start the Backend Server

This is **REQUIRED** for both the extension and website to work.

```powershell
cd d:\LinkScout
python combined_server.py
```

**Wait for**:
```
✅ Server running on http://localhost:5000
```

### Step 2: Option A - Use the Browser Extension

1. Open your browser (Chrome/Edge)
2. Navigate to `chrome://extensions/`
3. Enable "Developer mode"
4. Click "Load unpacked"
5. Select `d:\LinkScout\extension\`
6. Click the LinkScout icon to analyze any webpage!

### Step 2: Option B - Use the Web Interface

```powershell
# In a NEW terminal
cd d:\LinkScout\web_interface\LinkScout
npm install  # First time only
npm run dev
```

Open browser to: **http://localhost:3000**

### Step 3: Analyze Content!

**Extension**:
- Click the extension icon
- Click "Scan Page" to analyze current page
- Or paste URL/text and click "Analyze"

**Website**:
- Go to Search page (`/search`)
- Paste URL or text
- Press Enter

## 📁 Directory Structure

```
d:\LinkScout\
├── combined_server.py          # ⚙️ BACKEND SERVER (must be running)
├── extension/                  # 🧩 BROWSER EXTENSION
│   ├── manifest.json
│   ├── popup.html
│   ├── popup.js
│   ├── background.js
│   ├── content.js
│   └── styles.css
└── web_interface/
    └── LinkScout/              # 🌐 WEB INTERFACE
        ├── app/
        │   ├── page.tsx        # Home page
        │   ├── search/         # Analysis page
        │   ├── extensions/     # Extension download
        │   └── api/            # API routes
        ├── components/
        └── package.json
```

## 🔧 How It Works

```
Browser Extension  →  
                     ↓
              Backend Server (Port 5000)
                     ↑
   Web Interface   →  
```

Both the extension and website send requests to the **same backend server** which:
- Analyzes content with 8 ML models
- Uses Groq AI for intelligent insights
- Runs 8-phase Revolutionary Detection
- Returns comprehensive analysis results

## 📊 Features

### Backend Server (`combined_server.py`)

✅ Groq AI Agentic System (4 Agents)  
✅ Pre-trained Models (8 Models)  
✅ Custom Trained Model  
✅ Revolutionary Detection (8 Phases)  
✅ Category/Label Detection  
✅ Google Search Integration  
✅ Reference Links & Sources  
✅ Image Analysis (AI-generated detection)  
✅ Reinforcement Learning  

### Browser Extension

✅ Analyze current page with one click  
✅ Paste URL or text for analysis  
✅ Highlight suspicious paragraphs  
✅ Real-time credibility scoring  
✅ Detailed breakdown by section  
✅ Source verification  

### Web Interface

✅ Modern, responsive UI  
✅ Real-time analysis  
✅ Beautiful results display  
✅ Extension download page  
✅ Mobile-optimized  
✅ Dark mode theme  

## 🌐 Web Interface Pages

- **`/`** - Home page with hero
- **`/search`** - Main analysis interface ⭐
- **`/extensions`** - Download extension ⭐
- **`/history`** - Analysis history (placeholder)
- **`/settings`** - Settings (placeholder)

## 🎯 Use Cases

### Use Case 1: Check News Article via Extension

1. Navigate to any news article
2. Click LinkScout extension icon
3. Click "Scan Page"
4. View inline highlights + detailed analysis

### Use Case 2: Analyze URL via Website

1. Go to `http://localhost:3000/search`
2. Paste article URL
3. Press Enter
4. View comprehensive analysis

### Use Case 3: Check Suspicious Text

1. Copy suspicious text
2. Open extension OR website
3. Paste text
4. Get instant credibility score

### Use Case 4: Download Extension from Website

1. Go to `http://localhost:3000/extensions`
2. Click "Download Extension"
3. Extract ZIP file
4. Load into browser

## 🐛 Troubleshooting

### Backend Server Won't Start

**Error**: `ModuleNotFoundError`

**Solution**:
```powershell
pip install -r requirements.txt
```

**Error**: `Port 5000 already in use`

**Solution**: Kill process using port 5000 or change port in `combined_server.py`

### Extension Not Working

**Error**: "Server offline"

**Solution**: Make sure backend server is running (`python combined_server.py`)

**Error**: "No content found"

**Solution**: Try clicking "Scan Page" instead of analyzing current URL

### Website Not Loading

**Error**: `npm: command not found`

**Solution**: Install Node.js from https://nodejs.org/

**Error**: "Failed to analyze content"

**Solution**: Ensure backend server is running on port 5000

### Analysis Taking Too Long

**Normal**: First analysis loads models (30-60 seconds)  
**Subsequent**: Should be faster (10-20 seconds)

If still slow, check:
- GPU drivers (if using CUDA)
- Internet connection (for Groq AI)
- Server console for errors

## 🔒 Important Notes

1. **Backend MUST be running** for both extension and website
2. **First analysis is slow** (models loading) - be patient!
3. **Groq API** may have rate limits - fallback to ML models if needed
4. **Extension and website are independent** - use either or both!

## 📝 Configuration

### Backend Server Port

Change in `combined_server.py`:
```python
app.run(host='0.0.0.0', port=5000)  # Change 5000 to desired port
```

### Website Backend URL

Change in `web_interface/LinkScout/.env.local`:
```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:5000
```

### Extension Backend URL

Change in `extension/popup.js`:
```javascript
const SERVER_URL = 'http://localhost:5000';
```

## 🚀 Production Deployment

### Backend

```powershell
# Use gunicorn for production
pip install gunicorn
gunicorn combined_server:app -w 4 -b 0.0.0.0:5000
```

### Web Interface

```powershell
cd web_interface/LinkScout
npm run build
npm run start
```

### Extension

1. Create production build (if using build tools)
2. Package as ZIP
3. Submit to Chrome Web Store / Edge Add-ons

## 📞 Getting Help

### Check Logs

**Backend**: Console where you ran `python combined_server.py`  
**Website**: Browser DevTools → Console  
**Extension**: Chrome → Extensions → LinkScout → Inspect views  

### Common Issues

✅ "Server offline" → Start `combined_server.py`  
✅ "Analysis failed" → Check backend console for errors  
✅ "No results" → Try different content or check internet  
✅ Page not loading → Clear browser cache, restart servers  

## 🎉 You're All Set!

You now have:
- ✅ Backend server running AI analysis
- ✅ Browser extension for quick checks
- ✅ Modern web interface for detailed analysis
- ✅ Extension download capability

**Start analyzing content and fighting misinformation!** 🚀

---

**Questions?** Check the server console for detailed logs.  
**Found a bug?** Check backend + browser console for errors.  

**Made with ❤️ for truth and accuracy.**
