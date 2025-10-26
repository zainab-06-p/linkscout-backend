# LinkScout - Quick Test Guide

## 🚀 Quick Start (2 Steps)

### Step 1: Start Backend
```bash
cd D:\LinkScout
python combined_server.py
```

**Wait for:**
```
✅ RoBERTa loaded
✅ Emotion model loaded
Server: http://localhost:5000
```

### Step 2: Start Website
```bash
cd D:\LinkScout\web_interface\LinkScout
npm run dev
```

**Wait for:**
```
✓ Ready in 2.5s
Local: http://localhost:3000
```

---

## ✅ Test 1: URL Analysis

**Steps:**
1. Open: http://localhost:3000/search
2. Paste: `https://www.bbc.com/news/articles/c93dy2kk7vzo`
3. Press Enter

**Expected Result:**
```
✅ URL is scraped
✅ 30+ paragraphs extracted
✅ Full AI analysis displayed
✅ Risk score shown (not 0%)
✅ Categories detected
✅ "What's Correct" section filled
✅ "What's Wrong" section filled
✅ Sources shown
```

**If you see "0% risk" or "Article":**
- ❌ URL scraping failed
- Check backend console for errors
- Try a different URL

---

## ✅ Test 2: Mobile Responsiveness

**Steps:**
1. Press F12 (DevTools)
2. Press Ctrl+Shift+M (Mobile view)
3. Select: iPhone 14 Pro
4. Click the input box

**Expected Result:**
```
✅ Input doesn't overlap keyboard
✅ Content scrolls smoothly
✅ Buttons are easy to tap
✅ Text is readable
✅ Swipe handle shows at top
```

**If input overlaps keyboard:**
- ❌ Hard refresh: Ctrl+Shift+R
- Clear browser cache

---

## ✅ Test 3: Extension Download

### From Homepage:
**Steps:**
1. Go to: http://localhost:3000
2. Click: "Get Extension"

**Expected Result:**
```
✅ Button shows "Downloading..."
✅ File downloads: linkscout-extension.zip
✅ Page redirects to /extensions
✅ Success message appears
```

### From Extensions Page:
**Steps:**
1. Go to: http://localhost:3000/extensions
2. Click: "Download Extension" (big button)

**Expected Result:**
```
✅ Button shows loading spinner
✅ File downloads: linkscout-extension.zip
✅ Alert: "Extension downloaded! Extract..."
```

**If download fails:**
- ❌ Backend not running → Start `python combined_server.py`
- Check browser console (F12) for errors

---

## ✅ Test 4: Install Extension

**Steps:**
1. Extract `linkscout-extension.zip`
2. Open Chrome/Edge
3. Go to: `chrome://extensions` or `edge://extensions`
4. Enable "Developer mode" (top-right toggle)
5. Click "Load unpacked"
6. Select extracted folder

**Expected Result:**
```
✅ Extension appears in list
✅ No errors shown
✅ Extension icon in toolbar
✅ Click icon → Popup opens
✅ Can analyze URLs from popup
```

---

## 🐛 Common Issues

### **Issue: "Download failed"**
**Solution:**
```bash
# Start backend first!
python combined_server.py
```

### **Issue: "No content found at this URL"**
**Solution:**
```bash
# Try these test URLs:
https://www.bbc.com/news
https://www.cnn.com
https://www.reddit.com/r/news
```

### **Issue: "Analysis failed"**
**Solution:**
```bash
# Check backend is running on port 5000
# Check backend console for errors
# Try restarting backend
```

### **Issue: Mobile input still overlapping**
**Solution:**
```bash
# Hard refresh browser
Ctrl + Shift + R (Windows)
Cmd + Shift + R (Mac)

# Or clear cache:
DevTools → Application → Clear storage
```

---

## 📊 Success Criteria

### ✅ **URL Analysis Works When:**
- URL scraping extracts 20+ paragraphs
- Risk score is not 0% (unless truly credible)
- Categories are detected (not just "Other")
- "What's Correct" has actual content
- "What's Wrong" has actual content

### ✅ **Mobile Works When:**
- Input never hidden by keyboard
- Can type and scroll smoothly
- All buttons easily tappable
- Content visible at all times

### ✅ **Download Works When:**
- ZIP file downloads successfully
- File size is ~50-100 KB
- Can extract without errors
- Extension loads in browser

---

## 🎯 Quick Verification

### Run This Test (30 seconds):
```bash
1. Start backend: python combined_server.py
2. Start frontend: npm run dev
3. Open: http://localhost:3000/search
4. Paste: https://www.bbc.com/news
5. Verify: Risk score ≠ 0%, categories shown
6. Click: Download Extension (any page)
7. Verify: ZIP downloads
8. Done! ✅
```

---

## 📞 If Everything Works:

**You should see:**
- ✅ URLs being properly analyzed
- ✅ Mobile layout perfect
- ✅ Extension downloading
- ✅ No console errors

**Congratulations! All 3 fixes are working! 🎉**

---

## 📝 What Got Fixed:

1. **URL Analysis** → Now scrapes actual content
2. **Mobile UI** → Perfect positioning, no overlap
3. **Extension Download** → Real ZIP download with install guide

**All systems operational! 🚀**
