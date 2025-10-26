# Environment Variables Setup

This project requires the following environment variables to be set:

## Required Variables

### GROQ_API_KEY
- **Description**: API key for Groq AI service
- **Get it from**: https://console.groq.com/keys
- **Example**: `gsk_xxxxxxxxxxxxxxxxxxxxx`

## Optional Variables

### GOOGLE_API_KEY
- **Description**: Google Custom Search API key (for enhanced fact-checking)
- **Get it from**: https://developers.google.com/custom-search/v1/introduction
- **Example**: `AIzaSyxxxxxxxxxxxxxxxxxxxxx`

### GOOGLE_CSE_ID
- **Description**: Google Custom Search Engine ID
- **Get it from**: https://programmablesearchengine.google.com/
- **Example**: `11cbd49459703xxxx`

### PORT
- **Description**: Server port (default: 5000)
- **Default**: `5000`

## Setup Instructions

### Local Development

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your actual API keys:
   ```env
   GROQ_API_KEY=your_actual_groq_key_here
   GOOGLE_API_KEY=your_actual_google_key_here
   GOOGLE_CSE_ID=your_actual_cse_id_here
   PORT=5000
   ```

3. The server will automatically load these from the `.env` file

### Production Deployment (Render.com)

Add environment variables in the Render dashboard:

1. Go to your service settings
2. Click "Environment" tab
3. Add each variable:
   - `GROQ_API_KEY` = your key
   - `GOOGLE_API_KEY` = your key (optional)
   - `GOOGLE_CSE_ID` = your ID (optional)
   - `PORT` = 5000

## Security Notes

⚠️ **NEVER commit `.env` files or hardcode API keys in your code!**

- `.env` is in `.gitignore` and will not be committed
- Use environment variables for all sensitive data
- Rotate API keys if they are accidentally exposed
