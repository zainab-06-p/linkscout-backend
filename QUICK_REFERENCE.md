# LinkScout - Quick Reference 🚀

## ⚡ Quick Start (2 Commands)

### 1. Start Backend (REQUIRED)
```powershell
python combined_server.py
```
**Wait for**: `✅ Server running on http://localhost:5000`

### 2. Start Website (Optional)
```powershell
cd web_interface\LinkScout
npm run dev
```
**Open**: `http://localhost:3000`

---

## 📍 URLs & Ports

| Component | URL | Port |
|-----------|-----|------|
| Backend Server | `http://localhost:5000` | 5000 |
| Web Interface | `http://localhost:3000` | 3000 |
| Extension | `chrome://extensions/` | N/A |

---

## 🎯 Main Features

### Web Interface Pages
- **`/`** - Home page
- **`/search`** - Analyze URLs/text ⭐
- **`/extensions`** - Download extension ⭐
- **`/history`** - Past analyses
- **`/settings`** - Settings

### Extension Features
- Analyze current page
- Paste URL/text
- Highlight suspicious content
- Real-time scoring

---

## 🔧 Common Tasks

### Analyze a URL
**Website**: Go to `/search` → Paste URL → Enter  
**Extension**: Click icon → Paste URL → Analyze

### Download Extension
**Website**: Go to `/extensions` → Click Download  
**Manual**: Load `d:\LinkScout\extension` in browser

### Check Backend Status
**Test**: Open `http://localhost:5000/health`  
**Should see**: `{"status": "healthy", ...}`

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Server offline" | Run `python combined_server.py` |
| "Analysis failed" | Check backend console for errors |
| Port 5000 in use | Kill process or change port |
| Extension not working | Restart backend server |
| Website won't start | Run `npm install` first |

---

## 📂 Important Files

| File | Purpose |
|------|---------|
| `combined_server.py` | Backend server ⭐ |
| `extension/` | Browser extension ⭐ |
| `web_interface/LinkScout/` | Web app ⭐ |
| `START_BACKEND.bat` | Quick backend start |
| `START_WEBSITE.bat` | Quick website start |

---

## 🎨 Key Components

### Backend API Endpoints
- `/api/v1/analyze-chunks` - Main analysis
- `/health` - Health check
- `/download-extension` - Extension ZIP

### Web API Routes
- `/api/analyze` - Analysis proxy
- `/api/health` - Health proxy
- `/api/download-extension` - Download proxy

---

## 💡 Tips

✅ **Always start backend first**  
✅ **First analysis is slow (models loading)**  
✅ **Keep backend terminal open**  
✅ **Extension and website work independently**  
✅ **Both use the same backend server**  

---

## 📞 Need Help?

1. Check backend console for errors
2. Check browser console (F12)
3. Read `COMPLETE_SETUP_GUIDE.md`
4. Check `INTEGRATION_COMPLETE.md` for details

---

**Made with ❤️ - Smart Analysis. Simple Answers.**
