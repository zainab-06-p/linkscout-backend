# LinkScout - Smart Analysis. Simple Answers.

**The Ultimate AI-Powered Misinformation Detection Extension**

LinkScout combines the best of both worlds - powerful AI analysis from Groq with pre-trained machine learning models to provide comprehensive fact-checking and misinformation detection.

## 🚀 Features

### Dual AI Analysis System
- **Groq AI Agent**: Advanced natural language understanding and reasoning
- **Pre-trained Models**: RoBERTa, Emotion Analysis, NER, Hate Speech Detection, Clickbait Detection, Bias Detection

### Revolutionary Detection (8 Phases)
1. **Linguistic Fingerprint Analysis**: Detects manipulation patterns in text
2. **Claim-by-Claim Verification**: Verifies individual claims against databases
3. **Source Credibility Analysis**: Rates source reliability
4. **Entity Verification**: Validates people, organizations, places
5. **Propaganda Detection**: Identifies propaganda techniques
6. **Contradiction Detection**: Finds logical inconsistencies
7. **Network Analysis**: Detects bot/astroturfing patterns
8. **Reinforcement Learning**: Learns from user feedback to improve accuracy

### User Interface Features
- **Smart Paragraph Highlighting**: Color-coded suspicious content detection
- **Sidebar Analysis Report**: Comprehensive results without blocking the page
- **Real-time Google Search Integration**: Verifies claims with recent sources
- **Interactive Results Display**: Organized tabs for overview, details, and sources
- **One-Click Analysis**: Analyze entire pages or paste text/URLs

### Technical Capabilities
- **Chunk-based Analysis**: Analyzes content paragraph-by-paragraph for precision
- **Multi-language Support**: English, Hindi, Marathi, and 15+ Indian languages
- **Image Analysis**: Detects AI-generated/manipulated images
- **Offline Database**: Fast local verification of known false claims
- **Context-Aware Scoring**: Adjusts detection based on content type and category

## 📦 Installation

### Prerequisites
- Python 3.8+
- Node.js (optional, for development)
- Google Chrome or Microsoft Edge browser

### Backend Setup

1. **Install Python Dependencies**:
```powershell
cd d:\mis_2\LinkScout
pip install -r requirements_mis.txt
pip install flask flask-cors requests beautifulsoup4 torch transformers pillow
```

2. **Download AI Models** (if not already cached):
```powershell
# Models will auto-download to D:\huggingface_cache
# Requires ~5GB disk space
python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('hamzab/roberta-fake-news-classification', cache_dir=r'D:\huggingface_cache')"
```

3. **Configure Google Search** (optional):
   - Get Google Custom Search API key from https://developers.google.com/custom-search
   - Update `google_config.json` with your API key and CSE ID

4. **Start the Server**:
```powershell
python combined_server.py
```

Server will start at `http://localhost:5000`

### Extension Installation

1. **Open Chrome/Edge**
2. **Navigate to Extensions**: `chrome://extensions` or `edge://extensions`
3. **Enable Developer Mode**: Toggle in top-right corner
4. **Load Unpacked**: Click button and select `d:\mis_2\LinkScout\extension` folder
5. **Pin Extension**: Click puzzle icon and pin LinkScout for easy access

## 🎯 Usage

### Method 1: Analyze Current Page
1. Navigate to any news article or webpage
2. Click the LinkScout extension icon
3. Click **"Scan Page"**
4. View results in popup and check highlighted suspicious content on page

### Method 2: Paste Text or URL
1. Click the LinkScout extension icon
2. Paste text or URL in the input box
3. Click **"Analyze"**
4. Review comprehensive analysis results

### Method 3: Highlight Suspicious Content
1. After scanning a page, click **"Highlight"** button
2. Suspicious paragraphs will be color-coded:
   - 🔴 **Red**: High risk (>70% suspicious)
   - 🟡 **Yellow**: Medium risk (40-70% suspicious)
   - 🔵 **Blue**: Low risk (<40% suspicious)
3. Click **"Clear"** to remove highlights

### Method 4: View Detailed Report
- Analysis results appear in a sidebar on the right
- Shows percentage score, verdict, summary, and flagged content
- Includes Google search results for fact-checking

## 🔧 Configuration

### Server Configuration
Edit `combined_server.py`:
```python
# Groq API Key (for AI analysis)
GROQ_API_KEY = 'your_groq_api_key_here'

# Change port if needed
app.run(host='0.0.0.0', port=5000, debug=False)
```

### Extension Configuration
Edit `extension/content.js`:
```javascript
const CONFIG = {
    API_ENDPOINT: 'http://localhost:5000/api/v1/analyze-chunks',
    REQUEST_TIMEOUT: 180000, // 3 minutes
    AUTO_SCAN_DELAY: 3000
};
```

## 📊 How It Works

### Analysis Pipeline

1. **Content Extraction**
   - Extracts all paragraphs, headings, and article text
   - Filters out navigation, ads, and boilerplate

2. **Multi-Model Analysis**
   - RoBERTa: Fake news probability
   - Emotion Model: Sentiment and emotional manipulation
   - NER: Entity extraction and verification
   - Hate Speech: Toxic content detection
   - Clickbait: Sensationalism detection
   - Bias: Political/ideological bias detection

3. **Revolutionary Detection**
   - Linguistic patterns (sentence structure, word choice)
   - Claim extraction and database verification
   - Source credibility scoring
   - Entity validation (real people/organizations)
   - Propaganda technique identification
   - Logical contradiction detection
   - Bot/astroturfing pattern analysis

4. **Google Research**
   - Searches recent sources for claims
   - Compares against credible news outlets
   - Provides links for manual verification

5. **Scoring & Verdict**
   - Combines all signals into final score (0-100%)
   - Determines verdict: FAKE, SUSPICIOUS, or REAL
   - Generates human-readable explanation

6. **Reinforcement Learning**
   - Learns from user feedback
   - Improves accuracy over time
   - Adapts to new misinformation patterns

## 🎓 Understanding Results

### Misinformation Percentage
- **0-30%**: Low Risk - Mostly Credible
- **30-60%**: Medium Risk - Verify Claims
- **60-100%**: High Risk - Likely Misinformation

### Verdict Types
- **REAL**: Content appears authentic and fact-checked
- **SUSPICIOUS**: Mixed signals, requires verification
- **FAKE**: Strong indicators of misinformation

### Confidence Indicators
- High confidence: Multiple models agree + external verification
- Medium confidence: Some conflicting signals
- Low confidence: Limited data or unclear content

## 🐛 Troubleshooting

### Server Won't Start
- Check if port 5000 is available: `netstat -ano | findstr :5000`
- Ensure Python dependencies are installed
- Check for errors in terminal output

### Extension Not Working
- Verify server is running at http://localhost:5000
- Check browser console for errors (F12 → Console)
- Try reloading the extension
- Ensure you're on a valid webpage (not chrome:// pages)

### Models Not Loading
- Check disk space (requires ~5GB)
- Verify D:\huggingface_cache directory exists and is writable
- Run download script manually if needed

### Slow Analysis
- Large articles (>100 paragraphs) take 1-2 minutes
- Check CPU/GPU usage
- Consider reducing `REQUEST_TIMEOUT` for faster (less accurate) results

## 🤝 Contributing

This project combines features from two advanced misinformation detection systems. To contribute:

1. Keep backend functionality intact - both systems are working correctly
2. Test thoroughly before committing changes
3. Maintain clean, organized frontend code
4. Update documentation for new features

## 📝 Credits

**LinkScout** combines:
- **MIS Extension**: Groq AI agentic analysis, RL, image detection, revolutionary detection phases
- **MIS_2 Extension**: Pre-trained models, chunk analysis, Google search, sidebar UI

Created by combining the best features of both systems into one powerful tool.

## 🔒 Privacy & Security

- All analysis is performed locally or through your own API keys
- No data is collected or stored by LinkScout
- Google Search API (if configured) follows Google's privacy policy
- Groq API usage follows Groq's terms of service

## 📄 License

For educational and research purposes. Please respect API usage limits and terms of service.

---

**LinkScout - Smart Analysis. Simple Answers.** 🔍✨
