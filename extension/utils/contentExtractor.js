/**
 * Content Extractor - Enhanced intelligent extraction with ad blocking
 * Filters out advertisements, identifies page types, extracts multiple articles
 */

const ContentExtractor = {
  /**
   * Extract main content from current page
   */
  extractMainContent() {
    const content = {
      text: '',
      title: '',
      author: '',
      publishDate: '',
      source: window.location.hostname,
      pageType: this.detectPageType(),
      articles: [], // Multiple articles if detected
      confidence: 0,
      adBlockedCount: 0
    };

    // Extract title
    content.title = this.extractTitle();

    // Extract metadata
    const metadata = this.extractMetadata();
    content.author = metadata.author;
    content.publishDate = metadata.publishDate;

    // Extract main text (with ad filtering)
    const extractionResult = this.extractText();
    content.text = extractionResult.text;
    content.adBlockedCount = extractionResult.adsBlocked;
    
    // FALLBACK: If cleaning removed everything, try minimal cleaning
    if (!content.text || content.text.length < 100) {
      console.warn('⚠️ Ad filtering too aggressive, trying minimal cleaning...');
      
      // Try article element with minimal filtering
      const article = document.querySelector('[itemprop="articleBody"], article, main');
      if (article) {
        // Just remove scripts and styles, keep everything else
        const simpleClone = article.cloneNode(true);
        simpleClone.querySelectorAll('script, style, noscript').forEach(el => el.remove());
        const simpleText = simpleClone.textContent
          .replace(/\s+/g, ' ')
          .replace(/Advertisement/gi, '')
          .trim();
        
        if (simpleText.length > 100) {
          console.log(`✅ Minimal cleaning recovered ${simpleText.length} characters`);
          content.text = simpleText;
        }
      }
    }
    
    // Extract individual articles if multiple found
    content.articles = this.extractMultipleArticles();
    
    // Calculate extraction confidence
    content.confidence = this.calculateExtractionConfidence(content);

    console.log('Content Extraction Summary:', {
      pageType: content.pageType,
      textLength: content.text.length,
      articlesFound: content.articles.length,
      adsBlocked: content.adBlockedCount,
      confidence: content.confidence
    });

    return content;
  },

  /**
   * Detect specific page type (News, Blog, Social Media, etc.)
   */
  detectPageType() {
    const url = window.location.href.toLowerCase();
    const hostname = window.location.hostname.toLowerCase();

    // Social Media Platforms
    const socialMediaPatterns = {
      'facebook.com': 'social-facebook',
      'fb.com': 'social-facebook',
      'twitter.com': 'social-twitter',
      'x.com': 'social-twitter',
      'instagram.com': 'social-instagram',
      'linkedin.com': 'social-linkedin',
      'reddit.com': 'social-reddit',
      'tiktok.com': 'social-tiktok',
      'youtube.com': 'social-youtube',
      'pinterest.com': 'social-pinterest',
      'snapchat.com': 'social-snapchat',
      'whatsapp.com': 'social-whatsapp',
      'telegram.org': 'social-telegram',
      'discord.com': 'social-discord',
      'mastodon': 'social-mastodon'
    };

    for (const [domain, type] of Object.entries(socialMediaPatterns)) {
      if (hostname.includes(domain)) {
        console.log(`✓ Page Type: ${type}`);
        return type;
      }
    }

    // News Portals (Major domains)
    const newsPortals = [
      // US/International News
      'bbc.com', 'cnn.com', 'nytimes.com', 'theguardian.com', 'reuters.com',
      'apnews.com', 'bloomberg.com', 'wsj.com', 'washingtonpost.com',
      'forbes.com', 'time.com', 'newsweek.com', 'usatoday.com',
      'nbcnews.com', 'abcnews.go.com', 'cbsnews.com', 'foxnews.com',
      'aljazeera.com', 'economist.com', 'politico.com', 'thehill.com',
      'axios.com', 'vice.com', 'vox.com', 'buzzfeednews.com', 'huffpost.com',
      
      // Indian News
      'timesofindia.indiatimes.com', 'hindustantimes.com', 'indianexpress.com',
      'ndtv.com', 'thehindu.com', 'news18.com', 'dnaindia.com', 'india.com',
      'firstpost.com', 'thequint.com', 'scroll.in', 'thenewsminute.com',
      
      // Global News
      'dw.com', 'france24.com', 'rt.com', 'sputniknews.com',
      'scmp.com', 'japantimes.co.jp', 'straitstimes.com'
    ];

    for (const domain of newsPortals) {
      if (hostname.includes(domain)) {
        console.log('✓ Page Type: news-portal');
        return 'news-portal';
      }
    }

    // Blog Detection
    const blogIndicators = [
      'blog', 'wordpress', 'blogspot', 'medium.com', 'substack.com',
      'ghost.io', 'tumblr.com', 'blogger.com', 'wix.com/blog',
      'squarespace.com', 'weebly.com'
    ];

    for (const indicator of blogIndicators) {
      if (hostname.includes(indicator) || url.includes('/blog/')) {
        console.log('✓ Page Type: blog');
        return 'blog';
      }
    }

    // Check DOM for blog indicators
    if (document.querySelector('.blog, .post, article.entry, .blog-post')) {
      console.log('✓ Page Type: blog (DOM)');
      return 'blog';
    }

    // Check for article tag
    if (document.querySelector('article')) {
      console.log('✓ Page Type: article-page');
      return 'article-page';
    }

    console.log('⚠ Page Type: unknown');
    return 'unknown';
  },

  /**
   * Extract page title
   */
  extractTitle() {
    // Try Open Graph title
    const ogTitle = document.querySelector('meta[property="og:title"]');
    if (ogTitle) {
      return ogTitle.getAttribute('content');
    }

    // Try Twitter title
    const twitterTitle = document.querySelector('meta[name="twitter:title"]');
    if (twitterTitle) {
      return twitterTitle.getAttribute('content');
    }

    // Try article title
    const h1 = document.querySelector('article h1, .article h1, h1.title, h1.headline');
    if (h1) {
      return h1.textContent.trim();
    }

    // Fallback to page title
    return document.title;
  },

  /**
   * Extract metadata (author, date, etc.)
   */
  extractMetadata() {
    const metadata = {
      author: '',
      publishDate: ''
    };

    // Extract author
    const authorSelectors = [
      'meta[name="author"]',
      'meta[property="article:author"]',
      '[rel="author"]',
      '.author',
      '.byline',
      '.author-name',
      '[itemprop="author"]'
    ];

    for (let selector of authorSelectors) {
      const element = document.querySelector(selector);
      if (element) {
        metadata.author = element.getAttribute('content') || element.textContent.trim();
        if (metadata.author) break;
      }
    }

    // Extract publish date
    const dateSelectors = [
      'meta[property="article:published_time"]',
      'meta[name="publish-date"]',
      'time[datetime]',
      '.publish-date',
      '.date',
      '[itemprop="datePublished"]'
    ];

    for (let selector of dateSelectors) {
      const element = document.querySelector(selector);
      if (element) {
        metadata.publishDate = element.getAttribute('content') || 
                              element.getAttribute('datetime') || 
                              element.textContent.trim();
        if (metadata.publishDate) break;
      }
    }

    return metadata;
  },

  /**
   * Extract main text content with comprehensive ad blocking
   */
  extractText() {
    // Try common article selectors - EXPANDED LIST
    const contentSelectors = [
      // BBC SPECIFIC (HIGH PRIORITY)
      'article[data-component="text-block"]',  // BBC article blocks
      '[data-component="article-body"]',       // BBC article body
      '.article__body-content',                 // BBC body content
      '.ssrcss-pv1rh6-ArticleWrapper',         // BBC modern wrapper
      'main article',                           // BBC main article
      
      // Schema.org markup
      '[itemprop="articleBody"]',
      'div[itemprop="articleBody"]',
      
      // Article tags
      'article',
      '[role="article"]',
      
      // NDTV specific
      '.ins_storybody',      // Main story body
      '.sp-cn',              // Story container
      '#h_iframe',           // Story iframe
      '.fullstorydiv',       // Full story
      
      // Other Indian news sites
      '.article_block',      // India Today
      '.highlights',         // Times of India
      '.story_content',      // Hindustan Times
      '.article-text',       // The Hindu
      
      // Common news classes
      '.article-content',
      '.article-body',
      '.article__body',
      '.post-content',
      '.entry-content',
      '.story-body',
      '.story-content',
      '.content-body',
      
      // International news
      '.story-body__inner',  // BBC old
      '.article__content',   // Guardian
      '.paywall',            // NYT
      
      // Generic
      '.content',
      'main',
      '#main-content'
    ];

    let mainElement = null;
    let maxLength = 0;

    // Find element with most content
    for (let selector of contentSelectors) {
      try {
        const element = document.querySelector(selector);
        if (element) {
          const textLength = element.textContent.trim().length;
          if (textLength > maxLength && textLength > 100) {
            mainElement = element;
            maxLength = textLength;
            console.log(`✓ Found content with "${selector}": ${textLength} chars`);
          }
        }
      } catch (e) {
        // Skip invalid selectors
      }
    }

    // Fallback to body if no article found
    if (!mainElement || maxLength < 100) {
      console.log('⚠️ Using body as fallback');
      mainElement = document.body;
    }

    // Extract and clean text
    return this.cleanText(mainElement);
  },

  /**
   * Clean text - BALANCED AD FILTERING (not too aggressive)
   */
  cleanText(element) {
    const clone = element.cloneNode(true);
    let adsBlocked = 0;

    // === Remove ONLY obvious unwanted elements (reduced list) ===
    const unwantedSelectors = [
      // Scripts and styles - ALWAYS remove
      'script', 'style', 'noscript', 'iframe', 'embed', 'object',
      
      // Navigation - be selective
      'nav', 'header', 'footer', 'menu',
      
      // === ADS - Only obvious ad classes ===
      '.advertisement', '.ad-container', '.ad-banner', '.ad-slot',
      '[id*="google_ads"]', 'ins.adsbygoogle',
      '.taboola', '.outbrain', '.mgid',
      
      // Comments
      '.comments', '.comment-section', '.disqus',
      
      // Popups
      '.popup', '.modal', '.overlay'
    ];

    unwantedSelectors.forEach(selector => {
      try {
        const elements = clone.querySelectorAll(selector);
        adsBlocked += elements.length;
        elements.forEach(el => el.remove());
      } catch (e) {
        // Skip invalid selectors
      }
    });

    // Extract text from paragraphs and headings FIRST (preserves article content)
    const contentElements = clone.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, td, div[class*="content"], div[class*="article"], div[class*="story"]');
    let text = '';
    
    if (contentElements.length > 0) {
      contentElements.forEach(el => {
        const elText = el.textContent.trim();
        if (elText.length > 20) {  // Only include substantial text
          text += elText + ' ';
        }
      });
    }
    
    // Fallback: if no content found, use all text
    if (text.length < 100) {
      text = clone.textContent;
    }

    // Clean text with proper spacing
    text = text
      .replace(/\s+/g, ' ')  // Collapse multiple spaces
      .replace(/\n{3,}/g, '\n\n')  // Remove excessive newlines
      .replace(/Advertisement/gi, '')
      .replace(/Sponsored/gi, '')
      .replace(/ShareSave/gi, '')  // Remove social buttons
      .trim();

    console.log(`🛡️ Blocked ${adsBlocked} ad elements`);
    console.log(`📝 Extracted text length: ${text.length} characters`);
    
    if (text.length === 0) {
      console.warn('⚠️ Warning: cleanText() returned 0 characters after filtering!');
      console.warn('⚠️ Trying absolute fallback...');
      // ABSOLUTE FALLBACK: Just get all text, minimal cleaning
      text = element.textContent
        .replace(/\s+/g, ' ')
        .trim();
      console.log(`📝 Fallback extracted: ${text.length} characters`);
    }
    
    return { text, adsBlocked };
  },

  /**
   * Remove ads by attributes
   */
  removeAdElementsByAttributes(element) {
    const adKeywords = [
      'ad', 'ads', 'advert', 'sponsor', 'promo', 'banner',
      'commercial', 'marketing', 'affiliate'
    ];

    const allElements = element.querySelectorAll('*');
    let removed = 0;
    
    allElements.forEach(el => {
      const className = (el.className || '').toString().toLowerCase();
      const id = (el.id || '').toLowerCase();
      const dataAttrs = Array.from(el.attributes)
        .filter(attr => attr.name.startsWith('data-'))
        .map(attr => `${attr.name}=${attr.value}`.toLowerCase())
        .join(' ');
      
      const combined = `${className} ${id} ${dataAttrs}`;
      
      if (adKeywords.some(kw => combined.includes(kw))) {
        el.remove();
        removed++;
      }
    });

    return removed;
  },

  /**
   * Remove suspicious elements
   */
  removeSuspiciousElements(element) {
    let removed = 0;
    const containers = element.querySelectorAll('div, section');
    
    containers.forEach(container => {
      const text = container.textContent.trim();
      const links = container.querySelectorAll('a');
      
      if (text.length > 0) {
        const linkText = Array.from(links).reduce((sum, link) => 
          sum + link.textContent.length, 0);
        const linkDensity = linkText / text.length;
        
        if (linkDensity > 0.8 && text.length < 500) {
          container.remove();
          removed++;
        }
      }
    });

    return removed;
  },

  /**
   * Extract multiple articles
   */
  extractMultipleArticles() {
    const articles = [];
    const articleSelectors = [
      'article', '[itemtype*="Article"]', '.article',
      '.post', '.story', '.news-item', '[role="article"]'
    ];

    const found = new Set();

    for (const selector of articleSelectors) {
      const elements = document.querySelectorAll(selector);
      
      elements.forEach(element => {
        if (found.has(element)) return;
        
        const cleanResult = this.cleanText(element);
        const articleText = cleanResult.text;
        
        if (articleText.length < 200) return;
        
        articles.push({
          index: articles.length,
          text: articleText,
          title: this.extractArticleTitle(element),
          author: this.extractArticleAuthor(element),
          publishDate: this.extractArticleDate(element),
          url: this.extractArticleURL(element),
          wordCount: articleText.split(/\s+/).length,
          selector: selector
        });
        
        found.add(element);
        if (articles.length >= 10) return;
      });
      
      if (articles.length >= 10) break;
    }

    console.log(`📄 Found ${articles.length} articles`);
    return articles;
  },

  extractArticleTitle(element) {
    const selectors = ['h1', 'h2', 'h3', '.title', '.headline', '[itemprop="headline"]'];
    for (const sel of selectors) {
      const el = element.querySelector(sel);
      if (el && el.textContent.trim().length > 10) {
        return el.textContent.trim();
      }
    }
    return '';
  },

  extractArticleAuthor(element) {
    const selectors = ['[rel="author"]', '.author', '.byline', '[itemprop="author"]'];
    for (const sel of selectors) {
      const el = element.querySelector(sel);
      if (el) return el.textContent.trim().replace(/^by\s+/i, '');
    }
    return '';
  },

  extractArticleDate(element) {
    const selectors = ['time[datetime]', '.publish-date', '[itemprop="datePublished"]'];
    for (const sel of selectors) {
      const el = element.querySelector(sel);
      if (el) return el.getAttribute('datetime') || el.textContent.trim();
    }
    return '';
  },

  extractArticleURL(element) {
    const link = element.querySelector('a[href]');
    if (link) {
      const href = link.getAttribute('href');
      if (href && href.startsWith('http')) return href;
      if (href && !href.startsWith('#')) {
        try {
          return new URL(href, window.location.origin).href;
        } catch (e) {}
      }
    }
    return window.location.href;
  },

  /**
   * Calculate extraction confidence
   */
  calculateExtractionConfidence(content) {
    let confidence = 0;
    
    if (content.title && content.title.length > 10) confidence += 15;
    if (content.author) confidence += 10;
    if (content.publishDate) confidence += 10;
    if (content.text.length > 300) confidence += 15;
    if (content.text.length > 800) confidence += 10;
    if (content.text.length > 1500) confidence += 10;
    if (content.pageType !== 'unknown') confidence += 15;
    if (content.articles.length > 0) confidence += 10;
    if (content.adBlockedCount > 0) confidence += 10;
    
    return Math.min(confidence, 100);
  }
};

window.ContentExtractor = ContentExtractor;
