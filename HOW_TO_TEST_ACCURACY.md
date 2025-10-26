# 🧪 HOW TO RUN ACCURACY TEST

## Quick Test Instructions

### Step 1: Start the Server
Open a PowerShell terminal and run:
```powershell
cd D:\mis_2\LinkScout
python combined_server.py
```

**Wait until you see**:
```
✅ Core models loaded (RoBERTa, Emotion, NER, Hate, Clickbait, Bias)
🤖 [RL] Reinforcement Learning Agent initialized
  RL Agent: READY (Episodes: 0)
  Server starting...
```

### Step 2: Run the Test (in a NEW terminal)
Open a **NEW** PowerShell window and run:
```powershell
cd D:\mis_2\LinkScout
python test_simple_manual.py
```

Press ENTER when prompted.

### Step 3: Review Results
The test will process 10 samples:
- **5 Fake News** (COVID conspiracies, election fraud, chemtrails, 5G, cancer cures)
- **5 Real News** (WHO, NASA, MIT, CDC, Federal Reserve)

You'll see:
- ✅ **Accuracy** (target: 70%+)
- ✅ **False Positive Rate** (target: <20%)
- ✅ **Recall** (target: 60%+)
- ✅ **Precision** (target: 60%+)

Results saved to: `simple_test_results.json`

---

## What the Test Validates

### ✅ Database Expansion (97 false claims)
The test includes content matching claims from our expanded database:
- COVID vaccine misinformation
- Election fraud claims  
- Chemtrails conspiracy
- 5G health concerns
- Alternative medicine claims

### ✅ ML Model Integration (35% weight)
RoBERTa fake news classifier analyzes all samples and contributes 35% to risk score.

### ✅ Revolutionary Detection (40% weight)
8-phase linguistic analysis detects propaganda, emotional manipulation, etc.

---

## Expected Results

Based on our improvements:

### Before Improvements:
- Accuracy: ~48%
- Many false claims missed
- ML model not used

### After Improvements (Target):
- Accuracy: **70-80%** ✅
- False Positive Rate: **<20%** ✅
- Recall: **60-80%** ✅
- Database + ML working together

---

## Sample Output

```
🔍 Testing Sample #1: COVID vaccine conspiracy theories
   Expected: FAKE
   Content: COVID-19 vaccines contain microchips...
   ✅ Risk Score: 78.5%
   ✅ CORRECT - Detected as high risk

🔍 Testing Sample #6: Credible science reporting
   Expected: REAL
   Content: According to peer-reviewed study in Nature...
   ✅ Risk Score: 18.2%
   ✅ CORRECT - Detected as low risk

📈 FINAL RESULTS
================================================================================
📊 Confusion Matrix:
   True Positives (TP):  4 - Fake news correctly detected
   True Negatives (TN):  4 - Real news correctly identified
   False Positives (FP): 1 - Real news marked as fake
   False Negatives (FN): 1 - Fake news missed

🎯 Key Metrics:
   Accuracy:  80.0%  ✅
   FP Rate:   20.0%  ✅
   Recall:    80.0%  ✅
   Precision: 80.0%  ✅

✅ EXCELLENT - System performing well!
```

---

## Troubleshooting

### Server won't start:
```powershell
# Make sure you're in the right directory
cd D:\mis_2\LinkScout
ls combined_server.py  # Should exist

# Try running directly
python combined_server.py
```

### Test says "Connection refused":
- Server not running yet
- Wait 30 seconds after starting server
- Check server terminal shows "Server starting..."

### All tests fail:
- Check server didn't crash (look at server terminal)
- Server might be overloaded - restart it
- Try running test again

---

## Alternative: Manual Testing

If automated test has issues, test manually:

1. Start server: `python combined_server.py`
2. Open Chrome extension
3. Visit these sites:
   - **Fake**: conspiracy theory sites, health misinformation
   - **Real**: BBC, Reuters, Nature, WHO official pages
4. Click "Scan Page" and check risk scores
5. Fake news should show **60-100% risk**
6. Real news should show **0-40% risk**

---

**The test will show if our 3 implementations (Database + ML + Test Suite) improved accuracy from 48% to 70-80%!** 🎯
