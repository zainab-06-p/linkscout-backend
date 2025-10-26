/**
 * LinkScout Combined Content Script
 * Smart Analysis. Simple Answers.
 * Combines highlighting, sidebar, and chunk analysis from both extensions
 */

// Configuration
const CONFIG = {
    API_ENDPOINT: 'http://localhost:5000/api/v1/analyze-chunks',
    MIN_TEXT_LENGTH: 100,
    REQUEST_TIMEOUT: 180000, // 3 minutes
    AUTO_SCAN_DELAY: 3000
};

// State
let isAnalyzing = false;
let analysisResults = null;
let sidebarOpen = false;
let highlightedElements = [];

// Initialize
console.log('🔍 LinkScout content script loaded');

// Listen for messages from popup/background
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('📨 Message received:', request.action);
    
    if (request.action === 'ping') {
        sendResponse({ success: true, ready: true });
        return true;
    }
    
    if (request.action === 'analyzeCurrentPage') {
        analyzeAndDisplay().then(sendResponse);
        return true;
    }
    
    if (request.action === 'highlightSuspicious') {
        if (analysisResults) {
            highlightSuspiciousContent(analysisResults);
            sendResponse({ success: true });
        } else {
            sendResponse({ success: false, error: 'No analysis results' });
        }
        return true;
    }
    
    if (request.action === 'clearHighlights') {
        clearAllHighlights();
        sendResponse({ success: true });
        return true;
    }
    
    if (request.action === 'showResults') {
        if (analysisResults) {
            openSidebar();
            sendResponse({ success: true });
        } else {
            sendResponse({ success: false, error: 'No results' });
        }
        return true;
    }
    
    if (request.action === 'getResults') {
        sendResponse({
            success: analysisResults !== null,
            result: analysisResults
        });
        return true;
    }
    
    if (request.action === 'scrollToParagraph') {
        const chunkIndex = request.chunkIndex;
        console.log('📍 Scrolling to paragraph:', chunkIndex);
        scrollToChunk(chunkIndex);
        sendResponse({ success: true });
        return true;
    }
});

// ============= MAIN ANALYSIS FUNCTION =============

async function analyzeAndDisplay() {
    if (isAnalyzing) {
        return { success: false, error: 'Analysis in progress' };
    }
    
    isAnalyzing = true;
    
    try {
        // Extract content
        const extracted = window.ContentExtractorV2 
            ? window.ContentExtractorV2.extractFullContent()
            : extractContentFallback();
        
        if (!extracted || extracted.paragraphs.length === 0) {
            throw new Error('No content found on page');
        }
        
        console.log(`📊 Analyzing ${extracted.paragraphs.length} paragraphs...`);
        
        // Show loading indicator
        showLoadingNotification(extracted.paragraphs.length);
        
        // Prepare payload
        const payload = {
            paragraphs: extracted.paragraphs.map(p => ({
                index: p.index,
                text: p.text,
                type: p.type
            })),
            title: extracted.title,
            url: window.location.href,
            source: window.location.hostname,
            html: document.documentElement.outerHTML  // ✅ ADD HTML FOR IMAGE ANALYSIS
        };
        
        // Send to server
        console.log('📡 Sending POST request to:', CONFIG.API_ENDPOINT);
        console.log('📦 Payload size:', JSON.stringify(payload).length, 'bytes');
        
        const response = await fetch(CONFIG.API_ENDPOINT, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        console.log('📨 Response status:', response.status, response.statusText);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Server error response:', errorText);
            throw new Error(`Server error: ${response.status} - ${errorText.substring(0, 100)}`);
        }
        
        const result = await response.json();
        
        // Store results
        analysisResults = {
            ...result,
            extractedContent: extracted
        };
        
        // Hide loading
        hideLoadingNotification();
        
        // Show completion notification
        showCompletionNotification(result.overall);
        
        // Automatically highlight suspicious content
        if (result.chunks) {
            highlightSuspiciousContent(result);
        }
        
        // Open sidebar with results
        openSidebar();
        
        console.log('✅ Analysis complete:', result.verdict);
        
        return { success: true, result: analysisResults };
        
    } catch (error) {
        console.error('❌ Analysis error:', error);
        console.error('   Error type:', error.name);
        console.error('   Error message:', error.message);
        console.error('   Error stack:', error.stack);
        hideLoadingNotification();
        showErrorNotification(error.message);
        return { success: false, error: error.message };
    } finally {
        isAnalyzing = false;
    }
}

// ============= CONTENT EXTRACTION =============

function extractContentFallback() {
    const paragraphs = [];
    const elements = document.querySelectorAll('p, h1, h2, h3, article');
    
    elements.forEach((el, index) => {
        const text = el.textContent.trim();
        if (text.length > CONFIG.MIN_TEXT_LENGTH) {
            paragraphs.push({
                index,
                text,
                type: el.tagName.toLowerCase(),
                element: el
            });
        }
    });
    
    const title = document.querySelector('title')?.textContent || 
                  document.querySelector('h1')?.textContent || 
                  'Untitled';
    
    return { title, paragraphs };
}

// ============= HIGHLIGHTING =============

function highlightSuspiciousContent(result) {
    clearAllHighlights();
    
    console.log('🎨 [HIGHLIGHT] Starting highlighting process...');
    console.log('🎨 [HIGHLIGHT] Result object:', result);
    
    if (!result) {
        console.error('❌ [HIGHLIGHT] No result object provided!');
        return;
    }
    
    if (!result.chunks) {
        console.error('❌ [HIGHLIGHT] No chunks property in result!');
        console.log('🎨 [HIGHLIGHT] Available properties:', Object.keys(result));
        return;
    }
    
    console.log(`🎨 [HIGHLIGHT] Total chunks received: ${result.chunks.length}`);
    
    // ✅ STRICTER: Only highlight genuinely suspicious paragraphs (60+)
    const suspiciousChunks = result.chunks.filter(c => c.suspicious_score >= 60);
    
    console.log(`🎨 [HIGHLIGHT] Chunks with score >= 60: ${suspiciousChunks.length}`);
    
    if (suspiciousChunks.length > 0) {
        console.log('🎨 [HIGHLIGHT] Suspicious chunks:', suspiciousChunks.map(c => ({
            index: c.index,
            score: c.suspicious_score,
            preview: c.text_preview?.substring(0, 50),
            fullTextLength: c.text?.length || 0
        })));
    }
    
    if (suspiciousChunks.length === 0) {
        console.log('✅ No suspicious content to highlight');
        return;
    }
    
    console.log(`🎨 Highlighting ${suspiciousChunks.length} suspicious items`);
    
    suspiciousChunks.forEach(chunk => {
        const text = chunk.text_preview || chunk.text;
        if (!text) {
            console.warn('⚠️ Chunk has no text:', chunk);
            return;
        }
        
        console.log(`🔍 Looking for chunk ${chunk.index}: "${text.substring(0, 80)}..."`);
        
        // Find elements containing this text
        const elements = findElementsContainingText(text);
        
        if (elements.length === 0) {
            console.warn(`❌ Could not find element for chunk ${chunk.index}`);
        }
        
        elements.forEach(element => {
            highlightElement(element, chunk.suspicious_score, chunk.index);
        });
    });
    
    // Show notification
    const notification = createNotification();
    notification.style.background = '#3b82f6';
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 20px;">🎨</span>
            <div>
                <div style="font-weight: 700;">${suspiciousChunks.length} Suspicious Paragraphs Highlighted</div>
                <div style="font-size: 11px; opacity: 0.9;">Click sidebar paragraphs to jump to them</div>
            </div>
        </div>
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 4000);
}

function findElementsContainingText(searchText) {
    // Use more of the text for better matching
    const searchLower = searchText.toLowerCase();
    const searchStart = searchLower.substring(0, 150);  // First 150 chars
    const searchEnd = searchLower.substring(Math.max(0, searchLower.length - 150));  // Last 150 chars
    
    console.log(`🔍 [MATCH] Searching for text (${searchText.length} chars)`);
    console.log(`🔍 [MATCH] Start: "${searchStart.substring(0, 50)}..."`);
    
    // Strategy 1: Find exact paragraph match
    const allParagraphs = Array.from(document.querySelectorAll('p, li, blockquote, td, div[class*="paragraph"]'));
    let bestMatch = null;
    let bestScore = -1;
    
    for (const para of allParagraphs) {
        // Skip LinkScout elements
        if (para.closest('#linkscout-sidebar, [id*="linkscout"]')) continue;
        
        const paraText = para.textContent.toLowerCase();
        
        // Check if contains search text (start OR end)
        const containsStart = paraText.includes(searchStart.substring(0, 80));
        const containsEnd = searchEnd.length > 80 && paraText.includes(searchEnd.substring(searchEnd.length - 80));
        
        if (containsStart || containsEnd) {
            // Score: closer length = better match
            const lengthRatio = Math.min(paraText.length, searchText.length) / Math.max(paraText.length, searchText.length);
            let score = lengthRatio * 1000;
            
            // Bonus for exact match
            if (Math.abs(paraText.length - searchText.length) < 50) {
                score += 500;
            }
            
            if (score > bestScore) {
                bestScore = score;
                bestMatch = para;
            }
        }
    }
    
    if (bestMatch) {
        console.log(`✅ Found best match: ${bestMatch.tagName}, length: ${bestMatch.textContent.length}, score: ${bestScore.toFixed(1)}`);
        return [bestMatch];
    }
    
    // Strategy 2: Try finding parent div (as fallback)
    const allDivs = Array.from(document.querySelectorAll('div[class*="content"], div[class*="article"], div[class*="text"], div[class*="paragraph"]'));
    for (const div of allDivs) {
        if (div.closest('#linkscout-sidebar, [id*="linkscout"]')) continue;
        
        const divText = div.textContent.toLowerCase();
        if (divText.includes(searchLower.substring(0, 100)) && divText.length < searchText.length * 2) {
            console.log(`✅ Found fallback div match: ${div.className}`);
            return [div];
        }
    }
    
    console.log('❌ No match found for text:', searchText.substring(0, 50));
    return [];
}

function highlightElement(element, score, chunkIndex) {
    if (!element || highlightedElements.includes(element)) return;
    
    // Skip sidebar elements
    if (element.id && element.id.includes('linkscout')) return;
    if (element.closest('#linkscout-sidebar')) return;
    
    // Determine color based on score (stricter thresholds)
    let bgColor, borderColor;
    if (score >= 70) {
        bgColor = 'rgba(239, 68, 68, 0.15)';
        borderColor = '#ef4444';
    } else if (score >= 60) {  // Changed from 40 to 60
        bgColor = 'rgba(245, 158, 11, 0.15)';
        borderColor = '#f59e0b';
    } else {
        bgColor = 'rgba(59, 130, 246, 0.15)';
        borderColor = '#3b82f6';
    }
    
    // Store original style
    const originalStyle = {
        background: element.style.background,
        borderLeft: element.style.borderLeft,
        paddingLeft: element.style.paddingLeft
    };
    element.setAttribute('data-linkscout-original-style', JSON.stringify(originalStyle));
    
    // Mark with chunk index if provided
    if (chunkIndex !== undefined) {
        element.setAttribute('data-linkscout-chunk', chunkIndex);
    }
    
    // Apply highlight
    element.style.background = bgColor;
    element.style.borderLeft = `4px solid ${borderColor}`;
    element.style.paddingLeft = '12px';
    element.style.transition = 'all 0.3s ease';
    
    // Add to highlighted list
    highlightedElements.push(element);
    
    // Add tooltip
    element.setAttribute('title', `LinkScout: ${score}% suspicious - Click sidebar paragraph to jump here`);
    element.classList.add('linkscout-highlighted');
}

function clearAllHighlights() {
    highlightedElements.forEach(element => {
        try {
            const originalStyle = element.getAttribute('data-linkscout-original-style');
            if (originalStyle) {
                const styles = JSON.parse(originalStyle);
                element.style.background = styles.background;
                element.style.borderLeft = styles.borderLeft;
                element.style.paddingLeft = styles.paddingLeft;
                element.removeAttribute('data-linkscout-original-style');
            }
            element.removeAttribute('title');
            element.classList.remove('linkscout-highlighted');
        } catch (e) {
            console.error('Error clearing highlight:', e);
        }
    });
    
    highlightedElements = [];
    console.log('✅ All highlights cleared');
}

// ============= SIDEBAR =============

function openSidebar() {
    let sidebar = document.getElementById('linkscout-sidebar');
    
    if (sidebar) {
        sidebar.style.display = 'block';
        updateSidebarContent();
    } else {
        createSidebar();
    }
    
    sidebarOpen = true;
}

function createSidebar() {
    const sidebar = document.createElement('div');
    sidebar.id = 'linkscout-sidebar';
    sidebar.style.cssText = `
        position: fixed;
        top: 0;
        right: 0;
        width: 400px;
        height: 100vh;
        background: white;
        box-shadow: -4px 0 12px rgba(0,0,0,0.15);
        z-index: 999999;
        overflow-y: auto;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        animation: slideIn 0.3s ease;
    `;
    
    sidebar.innerHTML = `
        <style>
            @keyframes slideIn {
                from { transform: translateX(100%); }
                to { transform: translateX(0); }
            }
            #linkscout-sidebar::-webkit-scrollbar {
                width: 6px;
            }
            #linkscout-sidebar::-webkit-scrollbar-track {
                background: #f8fafc;
            }
            #linkscout-sidebar::-webkit-scrollbar-thumb {
                background: #cbd5e1;
                border-radius: 3px;
            }
        </style>
        <div id="linkscout-sidebar-content"></div>
    `;
    
    document.body.appendChild(sidebar);
    updateSidebarContent();
}

function updateSidebarContent() {
    const content = document.getElementById('linkscout-sidebar-content');
    if (!content || !analysisResults) return;
    
    const result = analysisResults;
    const overall = result.overall || {};
    const percentage = overall.suspicious_score || 0;
    const pretrained = result.pretrained_models || {};
    const research = result.research || {};
    const linguistic = result.linguistic_fingerprint || {};
    const claims = result.claim_verification || {};
    const source = result.source_credibility || {};
    const propaganda = result.propaganda_analysis || {};
    const entities = result.entity_verification || {};
    const contradictions = result.contradiction_analysis || {};
    const network = result.network_analysis || {};
    
    // Determine colors
    let bgColor, textColor, verdict, icon;
    if (percentage > 70) {
        bgColor = '#FF3B30';
        textColor = '#FFFFFF';
        verdict = '🚨 FAKE NEWS';
        icon = '🚨';
    } else if (percentage > 40) {
        bgColor = '#FFCC00';
        textColor = '#000000';
        verdict = '⚠️ SUSPICIOUS';
        icon = '⚠️';
    } else {
        bgColor = '#34C759';
        textColor = '#FFFFFF';
        verdict = '✅ LOOKS SAFE';
        icon = '✅';
    }
    
    let html = `
        <div style="background: ${bgColor}; color: ${textColor}; padding: 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 32px;">${icon}</span>
                    <div>
                        <div style="font-size: 20px; font-weight: bold;">${verdict}</div>
                        <div style="font-size: 14px; opacity: 0.9;">Suspicious: ${percentage}%</div>
                    </div>
                </div>
                <button id="linkscout-sidebar-close" style="background: rgba(255,255,255,0.2); border: none; color: ${textColor}; font-size: 28px; cursor: pointer; border-radius: 50%; width: 40px; height: 40px; line-height: 1;">×</button>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold;">${overall.total_paragraphs || 0}</div>
                    <div style="font-size: 12px; opacity: 0.9;">Analyzed</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold;">${(overall.fake_paragraphs || 0) + (overall.suspicious_paragraphs || 0)}</div>
                    <div style="font-size: 12px; opacity: 0.9;">Flagged</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold;">${overall.credibility_score || (100 - percentage)}%</div>
                    <div style="font-size: 12px; opacity: 0.9;">Credible</div>
                </div>
            </div>
        </div>
        
        <div style="flex: 1; overflow-y: auto; padding: 20px;">
            
            <!-- ✅ COMBINED CREDIBILITY METER (Same as Details tab) -->
            ${result.combined_analysis ? `
            <div style="background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); padding: 18px; border-radius: 12px; margin-bottom: 20px; border-left: 5px solid ${result.combined_analysis.verdict_color}; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
                <h4 style="margin: 0 0 16px 0; font-size: 16px; color: ${result.combined_analysis.verdict_color}; font-weight: 700; letter-spacing: 0.3px;">🎯 OVERALL CREDIBILITY</h4>
                
                <!-- Risk Score Display -->
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span style="font-size: 13px; font-weight: 600; color: #64748b;">Risk Score</span>
                    <span style="font-size: 28px; font-weight: 700; color: ${result.combined_analysis.verdict_color};">${(result.combined_analysis.overall_score || 0).toFixed(0)}/100</span>
                </div>
                
                <!-- Meter Bar -->
                <div style="background: #e5e7eb; border-radius: 12px; height: 28px; overflow: hidden; position: relative; margin-bottom: 8px;">
                    <div style="background: linear-gradient(90deg, ${result.combined_analysis.verdict_color}, ${result.combined_analysis.verdict_color}dd); width: ${Math.min(result.combined_analysis.overall_score || 0, 100)}%; height: 100%; border-radius: 12px; transition: all 0.5s ease;"></div>
                    <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13px; color: ${(result.combined_analysis.overall_score || 0) > 50 ? 'white' : '#1f2937'};">
                        ${result.combined_analysis.verdict || 'UNKNOWN'}
                    </div>
                </div>
                
                <!-- Legend -->
                <div style="display: flex; justify-content: space-between; margin-bottom: 16px; font-size: 10px; color: #9ca3af;">
                    <span>0 - Highly Credible</span>
                    <span>100 - Not Credible</span>
                </div>
                
                <!-- Quick Stats -->
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
                    <div style="background: #fef2f2; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #fecaca;">
                        <div style="font-size: 20px; font-weight: 700; color: #ef4444;">${overall.fake_paragraphs || 0}</div>
                        <div style="font-size: 10px; color: #991b1b; margin-top: 2px;">High Risk</div>
                    </div>
                    <div style="background: #fef3c7; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #fde68a;">
                        <div style="font-size: 20px; font-weight: 700; color: #f59e0b;">${overall.suspicious_paragraphs || 0}</div>
                        <div style="font-size: 10px; color: #92400e; margin-top: 2px;">Medium Risk</div>
                    </div>
                </div>
            </div>
            ` : ''}
            
            <!-- ARTICLE CATEGORIES -->
            ${pretrained.categories && Array.isArray(pretrained.categories) && pretrained.categories.length > 0 ? `
            <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); padding: 18px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #f59e0b; box-shadow: 0 2px 8px rgba(245, 158, 11, 0.25);">
                <h4 style="margin: 0 0 14px 0; font-size: 15px; color: #78350f; font-weight: 700; letter-spacing: 0.3px;">🏷️ ARTICLE CATEGORIES</h4>
                <div style="font-size: 13px; color: #78350f; line-height: 2; background: rgba(255, 255, 255, 0.5); padding: 12px; border-radius: 6px;">
                    ${pretrained.categories.map(cat => `<span style="display: inline-block; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 6px 14px; border-radius: 15px; margin: 4px; font-size: 12px; font-weight: 600; box-shadow: 0 2px 4px rgba(245, 158, 11, 0.3);">${cat}</span>`).join(' ')}
                </div>
            </div>
            ` : ''}
            
            <!-- GROQ AI RESEARCH REPORT -->
            ${research.research_findings ? `
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 18px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #5a67d8; box-shadow: 0 2px 8px rgba(102, 126, 234, 0.25); color: white;">
                <h4 style="margin: 0 0 14px 0; font-size: 15px; font-weight: 700; letter-spacing: 0.3px;">🤖 GROQ AI RESEARCH REPORT</h4>
                <div style="font-size: 13px; line-height: 2; background: rgba(255, 255, 255, 0.15); padding: 12px; border-radius: 6px;">
                    ${research.research_findings.replace(/\*\*(.*?)\*\*/g, '<strong style="color: #fbbf24;">$1</strong>').replace(/\n/g, '<br/>')}
                </div>
            </div>
            ` : ''}
            
            ${research.detailed_analysis ? `
            <div style="background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%); padding: 18px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #db2777; box-shadow: 0 2px 8px rgba(236, 72, 153, 0.25); color: white;">
                <h4 style="margin: 0 0 14px 0; font-size: 15px; font-weight: 700; letter-spacing: 0.3px;">🔬 DETAILED ANALYSIS</h4>
                <div style="font-size: 13px; line-height: 2; background: rgba(255, 255, 255, 0.15); padding: 12px; border-radius: 6px;">
                    ${research.detailed_analysis.replace(/\*\*(.*?)\*\*/g, '<strong style="color: #fbbf24;">$1</strong>').replace(/\n/g, '<br/>')}
                </div>
            </div>
            ` : ''}
            
            ${research.final_conclusion ? `
            <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 18px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #047857; box-shadow: 0 2px 8px rgba(16, 185, 129, 0.25); color: white;">
                <h4 style="margin: 0 0 14px 0; font-size: 15px; font-weight: 700; letter-spacing: 0.3px;">✅ FINAL CONCLUSION</h4>
                <div style="font-size: 13px; line-height: 2; background: rgba(255, 255, 255, 0.15); padding: 12px; border-radius: 6px;">
                    ${research.final_conclusion.replace(/\*\*(.*?)\*\*/g, '<strong style="color: #fbbf24;">$1</strong>').replace(/\n/g, '<br/>')}
                </div>
            </div>
            ` : ''}
            
            <!-- NAMED ENTITIES -->
            ${pretrained.named_entities && Array.isArray(pretrained.named_entities) && pretrained.named_entities.length > 0 ? `
            <div style="background: linear-gradient(135deg, #F3E5F5 0%, #E1BEE7 100%); padding: 18px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #9C27B0; box-shadow: 0 2px 8px rgba(156, 39, 176, 0.15);">
                <h4 style="margin: 0 0 14px 0; font-size: 15px; color: #6A1B9A; font-weight: 700; letter-spacing: 0.3px;">👥 KEY ENTITIES</h4>
                <div style="font-size: 13px; color: #263238; line-height: 2.2; background: rgba(255, 255, 255, 0.7); padding: 12px; border-radius: 6px;">
                    ${pretrained.named_entities.map(entity => `<span style="display: inline-block; background: linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%); color: white; padding: 6px 13px; border-radius: 15px; margin: 4px; font-size: 12px; font-weight: 600; box-shadow: 0 2px 4px rgba(156, 39, 176, 0.3);">${entity}</span>`).join(' ')}
                </div>
            </div>
            ` : ''}
            
            <!-- GOOGLE SEARCH RESULTS -->
            ${research.google_results && research.google_results.length > 0 ? `
            <div style="background: linear-gradient(135deg, #FFF9C4 0%, #FFF59D 100%); padding: 18px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #FBC02D; box-shadow: 0 2px 8px rgba(251, 192, 45, 0.15);">
                <h4 style="margin: 0 0 14px 0; font-size: 15px; color: #F57F17; font-weight: 700; letter-spacing: 0.3px;">🔗 GOOGLE SEARCH RESULTS</h4>
                <div style="font-size: 13px; color: #263238; line-height: 1.8; background: rgba(255, 255, 255, 0.7); padding: 12px; border-radius: 6px;">
                    ${research.google_results.slice(0, 5).map((r, i) => `
                        <div style="margin-bottom: 8px;">
                            <strong style="color: #F57F17;">${i + 1}.</strong> <a href="${r.link}" target="_blank" style="color: #1565C0; text-decoration: none; font-weight: 600;">${r.title}</a><br/>
                            <span style="font-size: 11px; color: #666;">${r.snippet || ''}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
            ` : ''}
            
            <!-- SUSPICIOUS PARAGRAPHS -->
            ${result.chunks && result.chunks.filter(c => c.suspicious_score >= 60).length > 0 ? `
            <div style="margin-bottom: 20px;">
                <h3 style="margin: 0 0 16px 0; font-size: 18px; color: #333; font-weight: 700;">
                    🚨 Suspicious Paragraphs (${result.chunks.filter(c => c.suspicious_score >= 60).length})
                </h3>
                ${result.chunks.filter(c => c.suspicious_score >= 60).map(chunk => `
                    <div class="linkscout-sidebar-chunk" data-chunk-index="${chunk.index}" 
                         style="background: ${chunk.suspicious_score > 70 ? '#fee2e2' : '#fef3c7'}; 
                                border-left: 4px solid ${chunk.suspicious_score > 70 ? '#ef4444' : '#f59e0b'}; 
                                padding: 16px; margin-bottom: 16px; border-radius: 8px; cursor: pointer; 
                                transition: all 0.2s;" 
                         onmouseover="this.style.background='${chunk.suspicious_score > 70 ? '#fecaca' : '#fde68a'}'" 
                         onmouseout="this.style.background='${chunk.suspicious_score > 70 ? '#fee2e2' : '#fef3c7'}'">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <strong style="color: #333;">📍 Paragraph ${chunk.index + 1}</strong>
                            <span style="background: ${chunk.suspicious_score > 70 ? '#ef4444' : '#f59e0b'}; color: white; 
                                         padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: bold;">
                                ${chunk.suspicious_score}/100
                            </span>
                        </div>
                        <div style="color: #666; font-size: 14px; line-height: 1.5; margin-bottom: 12px; font-style: italic;">
                            "${chunk.text_preview || chunk.text || 'N/A'}"
                        </div>
                        ${chunk.why_flagged ? `
                            <div style="background: white; padding: 12px; border-radius: 6px; margin-bottom: 8px; 
                                        font-size: 13px; line-height: 1.6; color: #555;">
                                <strong style="color: #333;">🔍 Why Flagged:</strong><br/>
                                ${chunk.why_flagged.replace(/\n/g, '<br/>')}
                            </div>
                        ` : ''}
                        <div style="font-size: 12px; color: #2196F3; font-weight: 600; margin-top: 8px;">
                            👆 Click to jump to this paragraph on the page
                        </div>
                    </div>
                `).join('')}
            </div>
            ` : `
            <div style="background: #d1fae5; padding: 16px; border-radius: 8px; border-left: 4px solid #10b981; margin-bottom: 20px;">
                <p style="color: #065f46; margin: 0; font-weight: 600;">✅ All Clear</p>
                <p style="color: #047857; margin: 8px 0 0 0; font-size: 13px;">No suspicious content detected! All paragraphs appear credible.</p>
            </div>
            `}
            
            <div style="background: #f8fafc; padding: 12px; border-radius: 8px; text-align: center; font-size: 11px; color: #64748b;">
                Powered by LinkScout AI<br/>
                ${pretrained.fake_probability !== undefined ? '✓ 8 ML Models Active' : ''}<br/>
                ${research.research_findings ? '✓ Groq AI Active' : ''}
            </div>
        </div>
    `;
    
    content.innerHTML = html;
    
    // Add close button functionality
    setTimeout(() => {
        const closeBtn = document.getElementById('linkscout-sidebar-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                const sidebar = document.getElementById('linkscout-sidebar');
                if (sidebar) {
                    sidebar.style.display = 'none';
                    sidebarOpen = false;
                    // Clear highlights when closing sidebar
                    clearAllHighlights();
                }
            });
        }
        
        // Add click-to-scroll functionality for suspicious paragraphs
        document.querySelectorAll('.linkscout-sidebar-chunk').forEach(chunkDiv => {
            chunkDiv.addEventListener('click', () => {
                const chunkIndex = parseInt(chunkDiv.getAttribute('data-chunk-index'));
                scrollToChunk(chunkIndex);
            });
        });
    }, 100);
}

// ============= SCROLL TO CHUNK =============

function scrollToChunk(chunkIndex) {
    console.log(`📍 Scrolling to chunk ${chunkIndex}`);
    
    if (!analysisResults || !analysisResults.chunks) {
        console.error('No analysis results available');
        return;
    }
    
    const chunk = analysisResults.chunks.find(c => c.index === chunkIndex);
    if (!chunk) {
        console.error(`Chunk ${chunkIndex} not found`);
        return;
    }
    
    // Try to find the element by data attribute first (if already highlighted)
    let element = document.querySelector(`[data-linkscout-chunk="${chunkIndex}"]`);
    
    // If not found, search by text content
    if (!element) {
        const searchText = chunk.text || chunk.text_preview;
        if (!searchText) {
            console.error('No text to search for');
            return;
        }
        
        // Search for paragraph containing this text - use more specific selectors
        const allParagraphs = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, blockquote, li');
        
        for (let candidate of allParagraphs) {
            // Skip sidebar elements
            if (candidate.id && candidate.id.includes('linkscout')) continue;
            if (candidate.closest('#linkscout-sidebar')) continue;
            
            const candidateText = candidate.textContent.trim();
            
            // Skip very short elements
            if (candidateText.length < 30) continue;
            
            // Check if text matches (compare first 150 chars for better accuracy)
            const searchSnippet = searchText.substring(0, 150).trim();
            const candidateSnippet = candidateText.substring(0, 150).trim();
            
            // Use more precise matching
            if (candidateSnippet === searchSnippet || candidateText.includes(searchSnippet)) {
                element = candidate;
                console.log(`✅ Found matching element: <${element.tagName}> with text: "${candidateSnippet.substring(0, 50)}..."`);
                break;
            }
        }
    }
    
    if (element) {
        // Clear ALL previous highlights first
        clearAllHighlights();
        
        // Mark element with data attribute
        element.setAttribute('data-linkscout-chunk', chunkIndex);
        
        // Highlight ONLY this specific element
        highlightElement(element, chunk.suspicious_score, chunkIndex);
        
        // Scroll to element
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        // Flash animation - use a pulsing blue effect for the specific paragraph
        const flashAnimation = () => {
            let pulseCount = 0;
            const pulseInterval = setInterval(() => {
                if (pulseCount >= 3) {
                    clearInterval(pulseInterval);
                    return;
                }
                
                // Pulse effect
                element.style.boxShadow = '0 0 25px rgba(59, 130, 246, 0.8)';
                element.style.transform = 'scale(1.01)';
                
                setTimeout(() => {
                    element.style.boxShadow = 'none';
                    element.style.transform = 'scale(1)';
                }, 300);
                
                pulseCount++;
            }, 600);
        };
        
        setTimeout(flashAnimation, 300);
        
        console.log(`✅ Scrolled to and highlighted chunk ${chunkIndex}`);
    } else {
        console.error(`❌ Could not find element for chunk ${chunkIndex}`);
        console.log('Chunk text:', chunk.text_preview || chunk.text);
        alert(`Could not locate paragraph ${chunkIndex + 1} on the page. The content may have changed.`);
    }
}

// ============= NOTIFICATIONS =============

function showLoadingNotification(paragraphCount) {
    const notification = createNotification();
    notification.style.background = '#3b82f6';
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="width: 20px; height: 20px; border: 3px solid white; border-top-color: transparent; border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
            <span>Analyzing ${paragraphCount} paragraphs...</span>
        </div>
        <style>
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
        </style>
    `;
    document.body.appendChild(notification);
}

function showCompletionNotification(overall) {
    const notification = createNotification();
    const verdict = overall.verdict || 'unknown';
    const color = verdict === 'fake' ? '#ef4444' : verdict === 'suspicious' ? '#f59e0b' : '#10b981';
    const icon = verdict === 'fake' ? '🚨' : verdict === 'suspicious' ? '⚠️' : '✅';
    
    notification.style.background = color;
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 20px;">${icon}</span>
            <div>
                <div style="font-weight: 700;">Analysis Complete</div>
                <div style="font-size: 11px; opacity: 0.9;">${verdict.toUpperCase()}</div>
            </div>
        </div>
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => notification.remove(), 4000);
}

function showErrorNotification(message) {
    const notification = createNotification();
    notification.style.background = '#ef4444';
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 20px;">❌</span>
            <div>
                <div style="font-weight: 700;">Error</div>
                <div style="font-size: 11px; opacity: 0.9;">${message}</div>
            </div>
        </div>
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => notification.remove(), 4000);
}

function hideLoadingNotification() {
    const notification = document.getElementById('linkscout-notification');
    if (notification) notification.remove();
}

function createNotification() {
    const existing = document.getElementById('linkscout-notification');
    if (existing) existing.remove();
    
    const notification = document.createElement('div');
    notification.id = 'linkscout-notification';
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #3b82f6;
        color: white;
        padding: 14px 18px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        font-family: -apple-system, sans-serif;
        font-size: 13px;
        z-index: 1000000;
        animation: slideDown 0.3s ease;
    `;
    
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideDown {
            from { transform: translateY(-20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
    `;
    notification.appendChild(style);
    
    return notification;
}

console.log('✅ LinkScout content script ready - Smart Analysis. Simple Answers.');
