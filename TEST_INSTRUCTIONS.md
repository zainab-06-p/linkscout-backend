# 🧪 LINKSCOUT TESTING GUIDE

## ✅ **SERVER IS WORKING PERFECTLY!**

The logs show:
```
✅ Server running on http://127.0.0.1:5000
✅ Health check: 200 OK
✅ RL Stats: 200 OK  
✅ OPTIONS request: 200 OK
```

**The server is NOT crashing - it's waiting for the extension to send data!**

---

## 🔍 **What To Do:**

### **Step 1: Reload Extension**
```
1. Open Chrome
2. Go to: chrome://extensions/
3. Find "LinkScout"
4. Click the 🔄 RELOAD button
5. Enable "Developer mode" if not already
```

### **Step 2: Open Browser Console**
```
1. Open any news article (e.g., NDTV)
2. Press F12 to open DevTools
3. Go to "Console" tab
4. Keep it open to see logs
```

### **Step 3: Click Extension**
```
1. Click the LinkScout icon in toolbar
2. Click "Scan This Page" button
3. Watch the Console tab
```

### **Step 4: Check Logs**

**In Browser Console, you should see:**
```
🔍 LinkScout content script loaded
📊 Analyzing X paragraphs...
📡 Sending POST request to: http://localhost:5000/api/v1/analyze-chunks
📦 Payload size: XXXX bytes
📨 Response status: 200 OK
✅ Analysis complete: APPEARS CREDIBLE
```

**In Server Terminal, you should see:**
```
🚨 ENDPOINT HIT: POST /api/v1/analyze-chunks
📊 LINKSCOUT ANALYSIS STARTED
🤖 [STEP 1/4] Running pre-trained models...
🤖 [STEP 2/4] Running Groq AI agents...
🔥 [STEP 3/4] Running Revolutionary Detection...
📋 [STEP 4/4] Analyzing individual paragraphs...
🖼️ [STEP 5/5] Analyzing images...
✅ Response prepared successfully
```

---

## ❌ **If You See Errors:**

### **Error: "Failed to fetch"**
**Cause:** Server not running or wrong URL
**Fix:**
1. Check server is running in terminal
2. Visit http://localhost:5000/health in browser
3. Should show JSON with `"status": "healthy"`

### **Error: "Network timeout"**
**Cause:** Article too large, analysis taking too long
**Fix:**
1. Try a shorter article first
2. Check server terminal for progress logs
3. Wait longer (can take 30-60 seconds for large articles)

### **Error: "CORS policy"**
**Cause:** CORS headers issue
**Fix:**
1. Server already has CORS enabled
2. Check if extension is making request from correct origin
3. Reload extension

### **Error: "JSON parse error"**
**Cause:** Server returned non-JSON response
**Fix:**
1. Check server terminal for Python errors
2. Make sure all imports work
3. Check if image_analysis.py is present

---

## 🎯 **Quick Test:**

**Open this URL in Chrome:**
```
https://www.ndtv.com/india-news/bihar-election-chirag-paswan-rjd-nothing-called-friendly-fight-chirag-paswans-dig-after-rjds-bihar-list-9487027
```

**Then:**
1. Click LinkScout icon
2. Click "Scan This Page"
3. Wait 20-30 seconds
4. Check tabs:
   - ✅ Overview (with all 5 sections)
   - ✅ Details  
   - ✅ Sources
   - ✅ 🖼️ Images (NEW!)

---

## 📊 **Expected Results:**

### **Overview Tab:**
- ✅ What's Correct (green)
- ❌ What's Wrong (red)
- 🌐 What Internet Says (blue)
- 💡 Recommendation (yellow)
- ⚠️ Why This Matters (purple)

### **Images Tab:**
- 📊 Statistics (Total/AI-Generated/Real)
- 🖼️ Summary
- ⚠️ Suspicious images (if any)
- 📋 All images list

---

## 🐛 **Still Having Issues?**

**Send me:**
1. Browser console logs (F12 → Console tab)
2. Server terminal output
3. Screenshot of error message

**Most likely cause:** Extension not reloaded after code changes!

---

## ✅ **All Changes Made:**

1. ✅ Server crash protection
2. ✅ Enhanced Groq API error handling
3. ✅ Image analysis integration
4. ✅ Images tab in extension
5. ✅ Overview section with all 5 sections
6. ✅ Better error logging
7. ✅ Removed problematic `AbortSignal.timeout()`

**Everything is ready - just reload the extension and test!** 🚀
