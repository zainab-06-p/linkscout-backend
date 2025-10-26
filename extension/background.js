/**
 * LinkScout Background Service Worker
 * Smart Analysis. Simple Answers.
 */

console.log('🚀 LinkScout background service worker loaded');

// Handle extension icon click
chrome.action.onClicked.addListener((tab) => {
    console.log('Extension icon clicked');
});

// Handle messages from content scripts/popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('📨 Background received message:', request.action);
    
    if (request.action === 'fetchAndAnalyze') {
        // Fetch URL content in background
        fetchAndAnalyze(request.url)
            .then(sendResponse)
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true; // Keep message channel open for async response
    }
    
    if (request.action === 'checkServer') {
        checkServerStatus()
            .then(sendResponse)
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true;
    }
});

// Fetch and analyze URL
async function fetchAndAnalyze(url) {
    try {
        console.log('🌐 Fetching URL:', url);
        
        // Fetch the webpage
        const response = await fetch(url, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const html = await response.text();
        
        // Parse HTML
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        
        // Extract content
        const title = doc.querySelector('title')?.textContent || 'Untitled';
        const paragraphs = Array.from(doc.querySelectorAll('p, article'));
        
        const content = paragraphs
            .map(p => p.textContent.trim())
            .filter(text => text.length > 100)
            .join('\n\n');
        
        if (!content) {
            throw new Error('No content found');
        }
        
        // Send to analysis server
        console.log('📤 Sending to analysis server...');
        const analysisResponse = await fetch('http://localhost:5000/api/v1/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                content,
                url,
                title,
                source: new URL(url).hostname
            })
        });
        
        if (!analysisResponse.ok) {
            throw new Error(`Analysis failed: ${analysisResponse.status}`);
        }
        
        const result = await analysisResponse.json();
        
        console.log('✅ Analysis complete');
        return { success: true, result };
        
    } catch (error) {
        console.error('❌ Fetch and analyze error:', error);
        return { success: false, error: error.message };
    }
}

// Check server status
async function checkServerStatus() {
    try {
        const response = await fetch('http://localhost:5000/health', {
            method: 'GET',
            signal: AbortSignal.timeout(5000)
        });
        
        if (response.ok) {
            const data = await response.json();
            return { success: true, status: data };
        } else {
            return { success: false, error: 'Server error' };
        }
    } catch (error) {
        return { success: false, error: error.message };
    }
}

console.log('✅ LinkScout background service worker ready');
