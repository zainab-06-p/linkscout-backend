# LinkScout Web Interface

**Smart Analysis. Simple Answers.**

A modern Next.js web application for analyzing articles and detecting misinformation using AI-powered analysis.

## 🚀 Features

- **URL & Text Analysis**: Paste any URL or text to analyze for misinformation
- **AI-Powered Insights**: Get detailed analysis using 8 ML models + Revolutionary Detection
- **Beautiful UI**: Modern, responsive design with gradient animations
- **Extension Download**: Download the browser extension directly from the website
- **Real-time Results**: See analysis results instantly with detailed breakdowns

## 📋 Prerequisites

- **Node.js** 18+ and npm
- **Python 3.10+** (for backend server)
- **Backend Server Running** on `http://localhost:5000`

## 🛠️ Installation & Setup

### 1. Install Dependencies

```powershell
cd d:\LinkScout\web_interface\LinkScout
npm install
```

### 2. Start the Backend Server (Required!)

**First, you must start the Python backend server:**

```powershell
cd d:\LinkScout
python combined_server.py
```

Wait until you see:
```
✅ Server running on http://localhost:5000
```

### 3. Start the Web Interface

In a **new terminal**:

```powershell
cd d:\LinkScout\web_interface\LinkScout
npm run dev
```

### 4. Open in Browser

Navigate to: **http://localhost:3000**

## 🎯 Usage

### Analyzing Content

1. Go to the **Search** page (`/search`)
2. Paste a URL or text into the chat input
3. Press Enter or click Send
4. View the comprehensive analysis results

### Downloading the Extension

1. Go to the **Extensions** page (`/extensions`)
2. Click "Download Extension"
3. The ZIP file will be downloaded automatically
4. Extract and load into your browser

## 📁 Project Structure

```
LinkScout/
├── app/
│   ├── page.tsx              # Home page
│   ├── search/page.tsx       # Analysis page
│   ├── extensions/page.tsx   # Extension download
│   └── api/
│       ├── analyze/route.ts  # Analysis API proxy
│       ├── health/route.ts   # Health check
│       └── download-extension/route.ts
├── components/
│   ├── analysis-results.tsx  # Results display component
│   ├── app-layout.tsx        # Main layout
│   └── ui/
│       ├── ai-chat-input.tsx
│       └── animated-shader-hero.tsx
└── package.json
```

## 🔧 Configuration

### Backend URL

By default, the web interface connects to `http://localhost:5000`.

To change this, create a `.env.local` file:

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:5000
```

## 🌐 Available Pages

- **`/`** - Home page with hero and CTA
- **`/search`** - Main analysis interface
- **`/extensions`** - Download browser extension
- **`/history`** - View past analyses (placeholder)
- **`/settings`** - User settings (placeholder)

## 🧪 Development

### Build for Production

```powershell
npm run build
npm run start
```

### Linting

```powershell
npm run lint
```

### Run Tests

```powershell
npm run test:e2e
```

## 🐛 Troubleshooting

### "Failed to analyze content"

**Solution**: Ensure the Python backend server is running on port 5000:

```powershell
cd d:\LinkScout
python combined_server.py
```

### "Extension download failed"

**Solution**: Make sure:
1. Backend server is running
2. The `extension` folder exists in `d:\LinkScout\extension`

### Port Already in Use

If port 3000 is busy, Next.js will automatically use the next available port (3001, 3002, etc.)

## 📊 Architecture

```
User Browser
     ↓
Next.js (Port 3000)
     ↓ (API Routes)
Python Backend (Port 5000)
     ↓
ML Models + Groq AI + Detection Systems
```

The Next.js app acts as a frontend and API proxy, forwarding requests to the Python backend which performs the actual analysis.

## 🔒 Security

- All API routes are CORS-enabled
- No sensitive data is stored on the frontend
- Extension download is served securely

## 📝 Notes

- The web interface and browser extension **share the same backend server** (`combined_server.py`)
- The extension works independently of the website
- All analysis logic is in the Python backend
- Frontend is purely presentational

## 🚀 Next Steps

1. Customize the UI colors/branding in `tailwind.config.ts`
2. Add authentication for personalized history
3. Implement caching for faster repeat analyses
4. Add more visualization options

## 📞 Support

For issues, check:
1. Backend server console for errors
2. Browser DevTools console
3. Network tab for failed requests

---

**Made with ❤️ using Next.js 15 + React 19 + Tailwind CSS**
