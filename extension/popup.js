/**
 * LinkScout - Combined Popup Script
 * Smart Analysis. Simple Answers.
 * Combines features from both mis and mis_2 extensions
 */

const SERVER_URL = 'http://localhost:5000';
const API_ENDPOINT = `${SERVER_URL}/api/v1/analyze-chunks`;

// DOM Elements
const searchInput = document.getElementById('searchInput');
const clearBtn = document.getElementById('clearBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const scanPageBtn = document.getElementById('scanPageBtn');
const highlightBtn = document.getElementById('highlightBtn');
const clearHighlightBtn = document.getElementById('clearHighlightBtn');
const resultsSection = document.getElementById('resultsSection');

let isAnalyzing = false;
let lastAnalysis = null;

// =============  INITIALIZATION =============

document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    checkServerConnection();
});

function setupEventListeners() {
    // Input handlers
    searchInput.addEventListener('input', (e) => {
        const hasValue = e.target.value.trim().length > 0;
        clearBtn.style.display = hasValue ? 'block' : 'none';
        analyzeBtn.disabled = !hasValue;
    });
    
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && searchInput.value.trim()) {
            handleAnalyze();
        }
    });
    
    // Button handlers
    clearBtn.addEventListener('click', () => {
        searchInput.value = '';
        clearBtn.style.display = 'none';
        analyzeBtn.disabled = true;
    });
    
    analyzeBtn.addEventListener('click', handleAnalyze);
    scanPageBtn.addEventListener('click', handleScanPage);
    highlightBtn.addEventListener('click', handleHighlight);
    clearHighlightBtn.addEventListener('click', handleClearHighlights);
}

async function checkServerConnection() {
    try {
        const response = await fetch(`${SERVER_URL}/health`, {
            method: 'GET',
            signal: AbortSignal.timeout(5000)
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Server connected:', data.name);
        } else {
            console.warn('⚠️ Server responded with error:', response.status);
        }
    } catch (error) {
        console.error('❌ Server connection failed:', error);
        showStatus('Server offline. Please start the server.', 'warning');
    }
}

// ============= ANALYZE TEXT/URL =============

async function handleAnalyze() {
    const input = searchInput.value.trim();
    
    if (!input || isAnalyzing) return;
    
    showLoading('Analyzing with AI...');
    
    try {
        let result;
        
        if (isURL(input)) {
            result = await analyzeURL(input);
        } else {
            result = await analyzeText(input);
        }
        
        if (result) {
            lastAnalysis = result;
            displayResults(result);
            chrome.storage.local.set({ lastAnalysis: result });
        }
        
    } catch (error) {
        console.error('Analysis error:', error);
        showError('Analysis Failed', error.message);
    } finally {
        isAnalyzing = false;
    }
}

function isURL(str) {
    try {
        new URL(str);
        return true;
    } catch {
        return str.startsWith('http://') || str.startsWith('https://');
    }
}

async function analyzeText(text) {
    const response = await fetch(`${API_ENDPOINT}`, {  // ✅ FIX: Use API_ENDPOINT constant
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            content: text,
            paragraphs: [{ index: 0, text: text, type: 'p' }]
        }),
        signal: AbortSignal.timeout(60000)
    });
    
    if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
    }
    
    return await response.json();
}

async function analyzeURL(url) {
    // ✅ FIX: First fetch URL content, then analyze
    showLoading('Fetching URL content...');
    
    // Try to fetch content from URL
    try {
        const fetchResponse = await fetch(url, {
            method: 'GET',
            signal: AbortSignal.timeout(10000)
        });
        
        if (!fetchResponse.ok) {
            throw new Error('Could not fetch URL');
        }
        
        const html = await fetchResponse.text();
        
        // Basic content extraction
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const paragraphs = Array.from(doc.querySelectorAll('p, article, .content'))
            .map((el, index) => ({ index, text: el.textContent.trim(), type: 'p' }))
            .filter(p => p.text.length > 50);
        
        showLoading('Analyzing content...');
        
        // Send to analysis with URL context
        const response = await fetch(`${API_ENDPOINT}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: url,
                paragraphs: paragraphs.length > 0 ? paragraphs : [{ index: 0, text: html, type: 'p' }],
                content: paragraphs.map(p => p.text).join('\n\n') || html
            }),
            signal: AbortSignal.timeout(60000)
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        return await response.json();
        
    } catch (error) {
        console.warn('Direct URL fetch failed, trying server-side:', error);
        
        // Fallback: Let server handle URL fetching
        const response = await fetch(`${API_ENDPOINT}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: url,
                paragraphs: [{ index: 0, text: url, type: 'url' }]
            }),
            signal: AbortSignal.timeout(60000)
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        return await response.json();
    }
}

// ============= SCAN CURRENT PAGE =============

async function handleScanPage() {
    if (isAnalyzing) return;
    
    showLoading('Scanning page...');
    isAnalyzing = true;
    
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        // Check if content script is loaded
        try {
            await chrome.tabs.sendMessage(tab.id, { action: 'ping' });
        } catch (e) {
            console.log('Injecting content script...');
            await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                files: ['utils/contentExtractor_v2.js', 'utils/cache.js', 'content.js']
            });
            await new Promise(resolve => setTimeout(resolve, 500));
        }
        
        // Request analysis
        const response = await chrome.tabs.sendMessage(tab.id, {
            action: 'analyzeCurrentPage'
        });
        
        if (response && response.success) {
            lastAnalysis = response.result;
            displayResults(response.result);
            showStatus('Analysis complete! Check the page for highlights.', 'success');
        } else {
            throw new Error(response.error || 'Analysis failed');
        }
        
    } catch (error) {
        console.error('Scan error:', error);
        showError('Scan Failed', error.message);
    } finally {
        isAnalyzing = false;
    }
}

// ============= HIGHLIGHT FUNCTIONS =============

async function handleHighlight() {
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        const response = await chrome.tabs.sendMessage(tab.id, {
            action: 'highlightSuspicious'
        });
        
        if (response && response.success) {
            showStatus('✅ Suspicious content highlighted!', 'success');
        } else {
            showError('Highlight Failed', 'Please scan the page first');
        }
    } catch (error) {
        console.error('Highlight error:', error);
        showError('Highlight Failed', error.message);
    }
}

async function handleClearHighlights() {
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        await chrome.tabs.sendMessage(tab.id, {
            action: 'clearHighlights'
        });
        
        showStatus('✅ Highlights cleared', 'success');
    } catch (error) {
        console.error('Clear error:', error);
    }
}

// ============= DISPLAY RESULTS =============

function displayResults(data) {
    console.log('📊 Displaying results:', data);
    
    if (!data) {
        showError('No Data', 'No analysis data received');
        return;
    }
    
    const percentage = data.fake_percentage || data.misinformation_percentage || 0;
    const verdict = data.verdict || 'unknown';
    const title = data.title || 'Analysis Result';
    
    // ✅ FIX: Round percentage to 1 decimal place for clean display
    const displayPercentage = Math.round(percentage * 10) / 10;
    
    // Determine percentage class
    let percentageClass = 'low';
    if (percentage > 60) percentageClass = 'high';
    else if (percentage > 30) percentageClass = 'medium';
    
    // Build HTML
    let html = `
        <div class="percentage-display">
            <div class="percentage-value ${percentageClass}">
                ${displayPercentage}%
            </div>
            <div class="verdict-text">
                ${verdict.toUpperCase()}
            </div>
        </div>
    `;
    
    // Tabs
    html += `
        <div class="tabs">
            <button class="tab-btn active" data-tab="overview">Overview</button>
            <button class="tab-btn" data-tab="details">Details</button>
            <button class="tab-btn" data-tab="sources">Sources</button>
            <button class="tab-btn" data-tab="images">🖼️ Images</button>
        </div>
    `;
    
    // Tab: Overview
    html += `<div class="tab-content active" id="overview">`;
    
    // Categories/Labels
    if (data.pretrained_models && data.pretrained_models.categories && data.pretrained_models.categories.length > 0) {
        html += `
            <div class="section" style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-left-color: #f59e0b;">
                <div class="section-title" style="color: #78350f;">🏷️ Article Category</div>
                <div class="section-content" style="color: #78350f;">
                    ${data.pretrained_models.categories.map(cat => `<span style="display: inline-block; background: #fbbf24; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; margin: 2px; font-weight: 600;">${cat}</span>`).join('')}
                </div>
            </div>
        `;
    }
    
    // Entities - BEAUTIFIED with badges
    if (data.pretrained_models && data.pretrained_models.named_entities && data.pretrained_models.named_entities.length > 0) {
        html += `
            <div class="section" style="background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%); border-left-color: #9c27b0;">
                <div class="section-title" style="color: #6a1b9a;">👥 Key Entities</div>
                <div class="section-content" style="line-height: 2.2;">
                    ${data.pretrained_models.named_entities.slice(0, 10).map(entity => `<span style="display: inline-block; background: linear-gradient(135deg, #9c27b0 0%, #7b1fa2 100%); color: white; padding: 5px 11px; border-radius: 14px; margin: 3px; font-size: 11px; font-weight: 600; box-shadow: 0 2px 4px rgba(156, 39, 176, 0.25);">${entity}</span>`).join(' ')}${data.pretrained_models.named_entities.length > 10 ? '<span style="color: #6a1b9a;">...</span>' : ''}
                </div>
            </div>
        `;
    }
    
    // What's Correct (formatted properly) - ONLY if not default
    if (data.what_is_right && data.what_is_right !== 'See conclusion' && data.what_is_right !== 'See full conclusion') {
        // ✅ FIX: Remove ALL asterisks and duplicate headers
        let correctText = data.what_is_right
            .replace(/\*\*/g, '')  // Remove all **
            .replace(/WHAT IS CORRECT:/gi, '')  // Remove header
            .replace(/What is correct:/gi, '')
            .trim();
        
        // Remove leading * if present
        correctText = correctText.replace(/^\*+\s*/gm, '');
        
        html += `
            <div class="section" style="background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); border-left-color: #10b981;">
                <div class="section-title" style="color: #065f46;">✅ What's Correct</div>
                <div class="section-content" style="color: #065f46; white-space: pre-line;">
                    ${correctText}
                </div>
            </div>
        `;
    } else if (data.what_is_right) {
        // Show placeholder when Groq API failed
        html += `
            <div class="section" style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-left-color: #f59e0b;">
                <div class="section-title" style="color: #78350f;">✅ What's Correct</div>
                <div class="section-content" style="color: #78350f;">
                    ⚠️ AI analysis unavailable (API rate limit). Analysis based on 8 ML models + Revolutionary Detection.
                </div>
            </div>
        `;
    }
    
    // Hide default "See conclusion" sections - ONLY show real data
    // What's Wrong
    if (data.what_is_wrong && data.what_is_wrong !== 'See conclusion' && data.what_is_wrong !== 'See full conclusion') {
        // ✅ FIX: Remove ALL asterisks and duplicate headers
        let wrongText = data.what_is_wrong
            .replace(/\*\*/g, '')  // Remove all **
            .replace(/WHAT IS WRONG:/gi, '')  // Remove header
            .replace(/What is wrong:/gi, '')
            .trim();
        
        // Remove leading * if present
        wrongText = wrongText.replace(/^\*+\s*/gm, '');
        
        html += `
            <div class="section" style="background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); border-left-color: #ef4444;">
                <div class="section-title" style="color: #991b1b;">❌ What's Wrong</div>
                <div class="section-content" style="color: #991b1b; white-space: pre-line;">
                    ${wrongText}
                </div>
            </div>
        `;
    }
    
    // What Internet Says
    if (data.internet_says && data.internet_says !== 'See conclusion' && data.internet_says !== 'See full conclusion') {
        // ✅ FIX: Remove ALL asterisks and duplicate headers
        let internetText = data.internet_says
            .replace(/\*\*/g, '')
            .replace(/WHAT THE INTERNET SAYS:/gi, '')
            .replace(/What the internet says:/gi, '')
            .trim();
        
        internetText = internetText.replace(/^\*+\s*/gm, '');
        
        html += `
            <div class="section" style="background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); border-left-color: #3b82f6;">
                <div class="section-title" style="color: #1e3a8a;">🌐 What the Internet Says</div>
                <div class="section-content" style="color: #1e3a8a; white-space: pre-line;">
                    ${internetText}
                </div>
            </div>
        `;
    }
    
    // Recommendation - ONLY show if meaningful
    if (data.recommendation && data.recommendation !== 'Verify with credible sources' && data.recommendation.length > 30) {
        // ✅ FIX: Remove ALL asterisks and duplicate headers
        let recommendationText = data.recommendation
            .replace(/\*\*/g, '')
            .replace(/MY RECOMMENDATION:/gi, '')
            .replace(/Recommendation:/gi, '')
            .trim();
        
        recommendationText = recommendationText.replace(/^\*+\s*/gm, '');
        
        html += `
            <div class="section" style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-left-color: #f59e0b;">
                <div class="section-title" style="color: #78350f;">💡 Recommendation</div>
                <div class="section-content" style="color: #78350f; white-space: pre-line;">
                    ${recommendationText}
                </div>
            </div>
        `;
    }
    
    // Why It Matters - ONLY show if meaningful
    if (data.why_matters && data.why_matters !== 'Critical thinking is essential' && data.why_matters.length > 30) {
        // ✅ FIX: Remove ALL asterisks and duplicate headers
        let whyMattersText = data.why_matters
            .replace(/\*\*/g, '')
            .replace(/WHY THIS MATTERS:/gi, '')
            .replace(/Why this matters:/gi, '')
            .trim();
        
        whyMattersText = whyMattersText.replace(/^\*+\s*/gm, '');
        html += `
            <div class="section" style="background: linear-gradient(135deg, #e9d5ff 0%, #d8b4fe 100%); border-left-color: #a855f7;">
                <div class="section-title" style="color: #581c87;">⚠️ Why This Matters</div>
                <div class="section-content" style="color: #581c87; white-space: pre-line;">
                    ${whyMattersText}
                </div>
            </div>
        `;
    }
    
    // Show summary stats if Groq failed
    if ((!data.what_is_right || data.what_is_right === 'See conclusion') && 
        (!data.research || !data.research.research_findings)) {
        html += `
            <div class="section" style="background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%); border-left-color: #6b7280;">
                <div class="section-title" style="color: #374151;">📊 Analysis Summary</div>
                <div class="section-content" style="color: #374151;">
                    <strong>Misinformation Score:</strong> ${percentage.toFixed(1)}%<br/>
                    <strong>Verdict:</strong> ${verdict.toUpperCase()}<br/>
                    <strong>Analyzed Paragraphs:</strong> ${data.overall?.total_paragraphs || 0}<br/>
                    <strong>Suspicious Paragraphs:</strong> ${data.overall?.suspicious_paragraphs || 0}<br/>
                    <strong>Models Used:</strong> 8 ML Models + Revolutionary Detection
                </div>
            </div>
        `;
    }
    
    html += `</div>`;
    
    // Tab: Details
    html += `<div class="tab-content" id="details">`;
    
    // Groq AI Research Results
    if (data.research && data.research.research_findings) {
        html += `
            <div class="section" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                <div class="section-title" style="color: white;">🤖 Groq AI Research</div>
                <div class="section-content" style="color: white; opacity: 0.95;">
                    ${data.research.research_findings.replace(/\n/g, '<br/>')}
                </div>
            </div>
        `;
    }
    
    if (data.research && data.research.detailed_analysis) {
        html += `
            <div class="section" style="background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%); color: white;">
                <div class="section-title" style="color: white;">🔬 Detailed Analysis</div>
                <div class="section-content" style="color: white; opacity: 0.95;">
                    ${data.research.detailed_analysis.replace(/\n/g, '<br/>')}
                </div>
            </div>
        `;
    }
    
    if (data.research && data.research.final_conclusion) {
        html += `
            <div class="section" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white;">
                <div class="section-title" style="color: white;">✅ Conclusion</div>
                <div class="section-content" style="color: white; opacity: 0.95;">
                    ${data.research.final_conclusion.replace(/\n/g, '<br/>')}
                </div>
            </div>
        `;
    }
    
    // ML Models section removed - entities shown in Overview tab only
    
    // ========================================
    // REVOLUTIONARY DETECTION - 8 PHASES
    // ========================================
    html += `<div class="section" style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); color: white; padding: 16px;">
        <div class="section-title" style="color: white; font-size: 14px; margin-bottom: 12px;">⚡ Revolutionary Detection System (8 Phases)</div>
    </div>`;
    
    // ✅ NEW: Combined Credibility Summary (replaces 8 individual phases)
    if (data.combined_analysis) {
        const combined = data.combined_analysis;
        const score = combined.overall_score || 0;
        const verdict = combined.verdict || 'UNKNOWN';
        const color = combined.verdict_color || '#607D8B';
        
        // Meter visualization
        const meterWidth = Math.min(score, 100);
        let meterColor = '#10b981';  // Green (credible)
        if (score > 50) meterColor = '#ef4444';  // Red (not credible)
        else if (score > 35) meterColor = '#f59e0b';  // Orange (questionable)
        else if (score > 20) meterColor = '#3b82f6';  // Blue (mostly credible)
        
        html += `
            <div class="section" style="border-left-color: ${color}; background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);">
                <div class="section-title" style="font-size: 18px; color: ${color};">
                    🎯 Overall Credibility Analysis
                </div>
                <div class="section-content">
                    <!-- Credibility Meter -->
                    <div style="margin: 20px 0;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="font-size: 14px; font-weight: 600; color: #64748b;">Risk Score</span>
                            <span style="font-size: 24px; font-weight: 700; color: ${color};">${score.toFixed(0)}/100</span>
                        </div>
                        
                        <!-- Meter Bar -->
                        <div style="background: #e5e7eb; border-radius: 12px; height: 24px; overflow: hidden; position: relative;">
                            <div style="background: linear-gradient(90deg, ${meterColor}, ${meterColor}dd); width: ${meterWidth}%; height: 100%; border-radius: 12px; transition: all 0.5s ease;"></div>
                            <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 12px; color: ${meterWidth > 50 ? 'white' : '#1f2937'};">
                                ${verdict}
                            </div>
                        </div>
                        
                        <!-- Legend -->
                        <div style="display: flex; justify-content: space-between; margin-top: 6px; font-size: 10px; color: #9ca3af;">
                            <span>0 - Highly Credible</span>
                            <span>100 - Not Credible</span>
                        </div>
                    </div>
                    
                    <!-- Quick Stats -->
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 16px;">
                        <div style="background: #f8fafc; padding: 12px; border-radius: 8px; text-align: center; border: 1px solid #e5e7eb;">
                            <div style="font-size: 24px; font-weight: 700; color: #ef4444;">${data.overall?.fake_paragraphs || 0}</div>
                            <div style="font-size: 11px; color: #64748b; margin-top: 4px;">High Risk Paragraphs</div>
                        </div>
                        <div style="background: #f8fafc; padding: 12px; border-radius: 8px; text-align: center; border: 1px solid #e5e7eb;">
                            <div style="font-size: 24px; font-weight: 700; color: #f59e0b;">${data.overall?.suspicious_paragraphs || 0}</div>
                            <div style="font-size: 11px; color: #64748b; margin-top: 4px;">Medium Risk Paragraphs</div>
                        </div>
                    </div>
                    
                    <!-- Detection Systems Note -->
                    <div style="margin-top: 16px; padding: 12px; background: #fef3c7; border-radius: 8px; border-left: 3px solid #f59e0b;">
                        <div style="font-size: 12px; color: #92400e; line-height: 1.5;">
                            <strong>📊 Analysis Based On:</strong><br/>
                            8 detection systems including linguistic patterns, claim verification, source credibility, entity verification, propaganda detection, network analysis, contradiction detection, and AI propagation analysis.
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    // What's Correct/Wrong sections removed - shown in Overview tab only
    
    if (data.suspicious_items || data.chunks) {
        // ✅ STRICTER: Only show truly suspicious chunks (score >= 60)
        const allItems = data.suspicious_items || data.chunks || [];
        const items = allItems.filter(item => {
            const score = item.suspicious_score || item.score || 0;
            return score >= 60;  // Changed from 40 to 60
        });
        
        if (items.length > 0) {
            html += `
                <div class="section">
                    <div class="section-title">⚠️ Suspicious Items (${items.length})</div>
            `;
            items.slice(0, 10).forEach((item, idx) => {
                const severity = item.severity || 'medium';
                const chunkIndex = item.index !== undefined ? item.index : (item.chunk_index !== undefined ? item.chunk_index : idx);
                const score = item.suspicious_score || item.score || 0;
                html += `
                    <div class="suspicious-item ${severity.toLowerCase()} clickable-paragraph" data-chunk-index="${chunkIndex}" style="cursor: pointer; transition: transform 0.2s;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                            <strong style="font-size: 11px;">📍 Paragraph ${chunkIndex + 1}</strong>
                            <span style="background: ${severity === 'high' ? '#ef4444' : '#f59e0b'}; color: white; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: 600;">
                                ${score}/100
                            </span>
                        </div>
                        <div style="font-style: italic; margin-bottom: 6px; font-size: 11px; color: #666;">
                            "${item.text_preview || item.text || 'Suspicious content'}"
                        </div>
                        <div style="font-size: 11px; font-weight: 600; color: #555;">
                            ${item.why_flagged || item.reason || 'Flagged as suspicious'}
                        </div>
                        <div style="font-size: 10px; opacity: 0.7; margin-top: 6px; color: #3b82f6; font-weight: 600;">
                            👆 Click to jump to this paragraph
                        </div>
                    </div>
                `;
            });
            html += `</div>`;
        }
    }
    
    html += `</div>`;
    
    // Tab: Sources
    html += `<div class="tab-content" id="sources">`;
    
    // Google Search Results
    if (data.research && data.research.google_results && data.research.google_results.length > 0) {
        html += `
            <div class="section">
                <div class="section-title">🔗 Google Search Results (${data.research.google_results.length})</div>
        `;
        data.research.google_results.forEach((result, idx) => {
            html += `
                <a href="${result.link}" class="source-link" target="_blank">
                    <strong>${idx + 1}. ${result.title}</strong><br/>
                    <span style="font-size: 11px; opacity: 0.8;">${result.snippet || ''}</span>
                </a>
            `;
        });
        html += `</div>`;
    }
    
    if (data.research_sources || data.sources_found) {
        const sources = data.research_sources || data.sources_found || [];
        if (sources.length > 0) {
            html += `
                <div class="section">
                    <div class="section-title">🔗 Research Sources (${sources.length})</div>
            `;
            sources.forEach((source, idx) => {
                const url = typeof source === 'string' ? source : source.url;
                const name = typeof source === 'object' ? source.name || source.title : `Source ${idx + 1}`;
                html += `
                    <a href="${url}" class="source-link" target="_blank">
                        ${name || url}
                    </a>
                `;
            });
            html += `</div>`;
        }
    }
    
    html += `</div>`;
    
    // Tab: Images (NEW!)
    html += `<div class="tab-content" id="images">`;
    
    if (data.image_analysis && data.image_analysis.analyzed_images > 0) {
        const img_data = data.image_analysis;
        
        // Summary
        html += `
            <div class="section" style="background: linear-gradient(135deg, ${img_data.ai_generated_count > 0 ? '#fee2e2 0%, #fecaca 100%' : '#d1fae5 0%, #a7f3d0 100%'}); border-left-color: ${img_data.ai_generated_count > 0 ? '#ef4444' : '#10b981'};">
                <div class="section-title" style="color: ${img_data.ai_generated_count > 0 ? '#991b1b' : '#065f46'};">🖼️ Image Analysis Summary</div>
                <div class="section-content" style="color: ${img_data.ai_generated_count > 0 ? '#991b1b' : '#065f46'}; white-space: pre-line;">
                    ${img_data.summary || 'No summary available'}
                </div>
            </div>
        `;
        
        // Statistics
        html += `
            <div class="section" style="background: #f8fafc; border-left-color: #3b82f6;">
                <div class="section-title">📊 Statistics</div>
                <div style="display: flex; gap: 12px; text-align: center;">
                    <div style="flex: 1; background: white; padding: 12px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                        <div style="font-size: 24px; font-weight: 700; color: #3b82f6;">${img_data.analyzed_images}</div>
                        <div style="font-size: 11px; color: #64748b; margin-top: 4px;">Analyzed</div>
                    </div>
                    <div style="flex: 1; background: white; padding: 12px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                        <div style="font-size: 24px; font-weight: 700; color: #ef4444;">${img_data.ai_generated_count}</div>
                        <div style="font-size: 11px; color: #64748b; margin-top: 4px;">AI-Generated</div>
                    </div>
                    <div style="flex: 1; background: white; padding: 12px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                        <div style="font-size: 24px; font-weight: 700; color: #10b981;">${img_data.real_images_count}</div>
                        <div style="font-size: 11px; color: #64748b; margin-top: 4px;">Real Photos</div>
                    </div>
                </div>
            </div>
        `;
        
        // Suspicious Images
        if (img_data.suspicious_images && img_data.suspicious_images.length > 0) {
            html += `
                <div class="section" style="background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); border-left-color: #ef4444;">
                    <div class="section-title" style="color: #991b1b;">⚠️ Suspicious AI-Generated Images</div>
            `;
            
            img_data.suspicious_images.forEach((img, idx) => {
                const detection = img.ai_detection || {};
                html += `
                    <div style="background: white; padding: 12px; margin: 8px 0; border-radius: 8px; border-left: 3px solid #ef4444;">
                        <div style="font-weight: 600; color: #991b1b; margin-bottom: 6px;">Image ${img.index}: ${detection.verdict || 'AI-Generated'}</div>
                        <div style="font-size: 12px; color: #64748b; margin-bottom: 4px;">🎯 Confidence: <strong>${(detection.confidence || 0).toFixed(1)}%</strong></div>
                        <div style="font-size: 12px; color: #64748b; margin-bottom: 8px;">📐 Size: ${img.width}x${img.height}px</div>
                        <a href="${img.url}" target="_blank" style="display: inline-block; padding: 4px 8px; background: #3b82f6; color: white; border-radius: 4px; text-decoration: none; font-size: 11px; margin-right: 4px;">🔗 View Image</a>
                        ${img.reverse_search ? `
                            <div style="margin-top: 8px; font-size: 11px; color: #64748b;">
                                🔍 Verify with Reverse Search:
                                <a href="${img.reverse_search.search_engines['Google Images']}" target="_blank" style="color: #3b82f6; margin: 0 4px;">Google</a>
                                <a href="${img.reverse_search.search_engines['TinEye']}" target="_blank" style="color: #3b82f6; margin: 0 4px;">TinEye</a>
                                <a href="${img.reverse_search.search_engines['Yandex']}" target="_blank" style="color: #3b82f6; margin: 0 4px;">Yandex</a>
                            </div>
                        ` : ''}
                    </div>
                `;
            });
            
            html += `</div>`;
        }
        
        // All Images List
        if (img_data.all_results && img_data.all_results.length > 0) {
            html += `
                <div class="section">
                    <div class="section-title">📋 All Images (${img_data.all_results.length})</div>
            `;
            
            img_data.all_results.forEach((img, idx) => {
                const detection = img.ai_detection || {};
                const color = detection.is_ai_generated ? '#ef4444' : '#10b981';
                html += `
                    <div style="padding: 8px; margin: 4px 0; border-left: 3px solid ${color}; background: #f8fafc; border-radius: 4px;">
                        <span style="font-weight: 600; color: ${color};">${img.index}. ${detection.verdict || 'Unknown'}</span>
                        <span style="font-size: 11px; color: #64748b; margin-left: 8px;">(${(detection.confidence || 0).toFixed(1)}%)</span>
                        <span style="font-size: 11px; color: #64748b; margin-left: 8px;">${img.width}x${img.height}px</span>
                    </div>
                `;
            });
            
            html += `</div>`;
        }
        
    } else {
        html += `
            <div class="section">
                <div class="section-content" style="text-align: center; color: #64748b; padding: 24px;">
                    ${data.image_analysis && data.image_analysis.total_images === 0 
                        ? '📷 No images found on this page' 
                        : '🖼️ Image analysis requires HTML content. Try scanning the page again.'}
                </div>
            </div>
        `;
    }
    
    html += `</div>`;
    
    // Display
    resultsSection.innerHTML = html;
    
    // Show feedback section after analysis
    showFeedbackSection();
    
    // Setup clickable suspicious paragraphs
    document.querySelectorAll('.clickable-paragraph').forEach(item => {
        item.addEventListener('click', () => {
            const chunkIndex = parseInt(item.dataset.chunkIndex);
            console.log('Clicked suspicious paragraph:', chunkIndex);
            
            // Send message to content script to scroll to paragraph
            chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
                if (tabs[0]) {
                    chrome.tabs.sendMessage(tabs[0].id, {
                        action: 'scrollToParagraph',
                        chunkIndex: chunkIndex
                    });
                    
                    // Visual feedback
                    item.style.transform = 'scale(0.95)';
                    setTimeout(() => {
                        item.style.transform = 'scale(1)';
                    }, 200);
                }
            });
        });
        
        // Hover effect
        item.addEventListener('mouseenter', () => {
            item.style.transform = 'scale(1.02)';
        });
        item.addEventListener('mouseleave', () => {
            item.style.transform = 'scale(1)';
        });
    });
    
    // Setup tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.dataset.tab;
            
            // Update buttons
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Update content
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            document.getElementById(targetTab).classList.add('active');
        });
    });
}

// ============= UI HELPERS =============

function showLoading(message) {
    resultsSection.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <div class="loading-text">${message}</div>
        </div>
    `;
}

function showError(title, message) {
    resultsSection.innerHTML = `
        <div class="no-results">
            <h3 style="color: #ef4444;">❌ ${title}</h3>
            <p style="margin-top: 10px; font-size: 13px; color: #64748b;">
                ${message}
            </p>
        </div>
    `;
}

function showStatus(message, type = 'info') {
    const color = type === 'success' ? '#10b981' : type === 'warning' ? '#f59e0b' : '#3b82f6';
    const icon = type === 'success' ? '✅' : type === 'warning' ? '⚠️' : 'ℹ️';
    
    // Show brief status notification
    const statusDiv = document.createElement('div');
    statusDiv.style.cssText = `
        position: fixed;
        top: 10px;
        left: 50%;
        transform: translateX(-50%);
        background: ${color};
        color: white;
        padding: 10px 20px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        z-index: 10000;
        animation: slideDown 0.3s ease;
    `;
    statusDiv.textContent = `${icon} ${message}`;
    document.body.appendChild(statusDiv);
    
    setTimeout(() => {
        statusDiv.style.animation = 'slideUp 0.3s ease';
        setTimeout(() => statusDiv.remove(), 300);
    }, 3000);
}

// ============= REINFORCEMENT LEARNING FEEDBACK =============

function setupFeedbackListeners() {
    const feedbackSection = document.getElementById('feedbackSection');
    const feedbackCorrect = document.getElementById('feedbackCorrect');
    const feedbackIncorrect = document.getElementById('feedbackIncorrect');
    const feedbackAggressive = document.getElementById('feedbackAggressive');
    const feedbackLenient = document.getElementById('feedbackLenient');
    
    if (!feedbackCorrect || !feedbackIncorrect || !feedbackAggressive || !feedbackLenient) return;
    
    feedbackCorrect.addEventListener('click', () => sendFeedback('correct'));
    feedbackIncorrect.addEventListener('click', () => sendFeedback('incorrect'));
    feedbackAggressive.addEventListener('click', () => sendFeedback('too_aggressive'));
    feedbackLenient.addEventListener('click', () => sendFeedback('too_lenient'));
}

async function sendFeedback(feedbackType) {
    if (!lastAnalysis) {
        showStatus('No analysis to provide feedback for', 'warning');
        return;
    }
    
    try {
        console.log(`📝 Sending ${feedbackType} feedback...`);
        
        const feedbackData = {
            analysis_data: {
                misinformation_percentage: lastAnalysis.misinformation_percentage || 0,
                suspicious_items: lastAnalysis.suspicious_items || [],
                content_preview: lastAnalysis.title || '',
                url: lastAnalysis.url || '',
                verdict: lastAnalysis.verdict || 'UNKNOWN'
            },
            feedback: {
                feedback_type: feedbackType,
                timestamp: new Date().toISOString()
            }
        };
        
        const response = await fetch(`${SERVER_URL}/feedback`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(feedbackData),
            signal: AbortSignal.timeout(10000)
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('✅ Feedback processed:', result);
        
        // Show success message
        const feedbackSuccess = document.getElementById('feedbackSuccess');
        if (feedbackSuccess) {
            feedbackSuccess.style.display = 'block';
            setTimeout(() => {
                feedbackSuccess.style.display = 'none';
            }, 3000);
        }
        
        // Update RL stats display
        if (result.rl_statistics) {
            updateRLStatsDisplay(result.rl_statistics);
        }
        
        showStatus('Feedback recorded - Thank you!', 'success');
        
    } catch (error) {
        console.error('❌ Feedback error:', error);
        showStatus('Failed to send feedback', 'warning');
    }
}

async function fetchRLStats() {
    try {
        const response = await fetch(`${SERVER_URL}/rl-stats`, {
            method: 'GET',
            signal: AbortSignal.timeout(5000)
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success && result.statistics) {
            updateRLStatsDisplay(result.statistics);
        }
        
    } catch (error) {
        console.error('❌ Failed to fetch RL stats:', error);
    }
}

function updateRLStatsDisplay(stats) {
    const rlStatsDisplay = document.getElementById('rlStatsDisplay');
    const rlEpisodes = document.getElementById('rlEpisodes');
    const rlAccuracy = document.getElementById('rlAccuracy');
    const rlEpsilon = document.getElementById('rlEpsilon');
    
    if (!rlStatsDisplay || !rlEpisodes || !rlAccuracy || !rlEpsilon) return;
    
    // Show the stats display
    rlStatsDisplay.style.display = 'block';
    
    // Update values
    rlEpisodes.textContent = stats.total_episodes || 0;
    
    if (stats.average_accuracy !== undefined && stats.average_accuracy > 0) {
        rlAccuracy.textContent = `${(stats.average_accuracy * 100).toFixed(1)}%`;
    } else {
        rlAccuracy.textContent = 'Learning...';
    }
    
    if (stats.epsilon !== undefined) {
        rlEpsilon.textContent = `${(stats.epsilon * 100).toFixed(1)}%`;
    } else {
        rlEpsilon.textContent = '--';
    }
}

function showFeedbackSection() {
    const feedbackSection = document.getElementById('feedbackSection');
    if (feedbackSection) {
        feedbackSection.style.display = 'block';
    }
}

function hideFeedbackSection() {
    const feedbackSection = document.getElementById('feedbackSection');
    if (feedbackSection) {
        feedbackSection.style.display = 'none';
    }
}

// Initialize feedback listeners when page loads
document.addEventListener('DOMContentLoaded', () => {
    setupFeedbackListeners();
    fetchRLStats();  // Load initial RL stats
});

console.log('✅ LinkScout popup loaded - Smart Analysis. Simple Answers.');
