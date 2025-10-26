/**
 * Content Extractor V2 - Enhanced Full Paragraph Extraction
 * Extracts ALL paragraphs from article with structure preservation
 */

const ContentExtractorV2 = {
  /**
   * Extract complete article content with all paragraphs
   */
  extractFullContent() {
    console.log('🔍 Starting enhanced content extraction...');
    
    const content = {
      title: '',
      subtitle: '',
      author: '',
      publishDate: '',
      source: window.location.hostname,
      url: window.location.href,
      pageType: this.detectPageType(),
      contentType: this.detectContentType(),
      paragraphs: [],  // Array of paragraph objects
      images: [],
      metadata: {},
      fullText: '',
      confidence: 0
    };

    // Extract metadata first
    content.metadata = this.extractMetadata();
    content.title = this.extractTitle();
    content.author = content.metadata.author;
    content.publishDate = content.metadata.publishDate;

    // Extract ALL paragraphs with structure
    const paragraphsData = this.extractAllParagraphs();
    content.paragraphs = paragraphsData.paragraphs;
    content.fullText = paragraphsData.fullText;
    content.images = this.extractImages();

    // Calculate extraction confidence
    content.confidence = this.calculateConfidence(content);

    console.log('✅ Extraction complete:', {
      title: content.title,
      paragraphs: content.paragraphs.length,
      characters: content.fullText.length,
      pageType: content.pageType,
      contentType: content.contentType,
      confidence: content.confidence
    });

    return content;
  },

  /**
   * Extract ALL paragraphs from the article
   * Returns array of paragraph objects with metadata
   */
  extractAllParagraphs() {
    console.log('📝 Extracting all paragraphs...');
    
    const paragraphs = [];
    let fullText = '';
    let paragraphIndex = 0;

    // Find the main article container
    const articleElement = this.findArticleContainer();
    
    if (!articleElement) {
      console.warn('⚠️ No article container found, using body');
      return this.fallbackExtraction();
    }

    console.log('✓ Found article container:', articleElement.tagName, articleElement.className);

    // Extract all paragraph elements
    const paragraphElements = articleElement.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, blockquote, figcaption');
    
    console.log(`📄 Found ${paragraphElements.length} paragraph elements`);

    paragraphElements.forEach((element, index) => {
      const text = this.cleanText(element.textContent);
      
      // Skip if too short (likely not content)
      if (text.length < 20) {
        return;
      }

      // Skip if it's a navigation/ad element
      if (this.isNonContentElement(element)) {
        return;
      }

      const paragraph = {
        index: paragraphIndex,
        type: element.tagName.toLowerCase(),
        text: text,
        length: text.length,
        element_id: element.id || null,
        element_class: element.className || null,
        xpath: this.getXPath(element),  // For precise location
        position: {
          top: element.offsetTop,
          left: element.offsetLeft
        }
      };

      paragraphs.push(paragraph);
      fullText += text + '\n\n';
      paragraphIndex++;
    });

    console.log(`✅ Extracted ${paragraphs.length} valid paragraphs`);

    return {
      paragraphs: paragraphs,
      fullText: fullText.trim()
    };
  },

  /**
   * Find the main article container element
   */
  findArticleContainer() {
    // Priority selectors for article content
    const selectors = [
      // Semantic HTML
      'article[role="main"]',
      'article[role="article"]',
      'main article',
      'article',
      '[role="article"]',
      '[role="main"]',
      'main',
      
      // Schema.org
      '[itemprop="articleBody"]',
      '[itemtype*="Article"]',
      
      // Common class patterns
      '.article-body',
      '.article-content',
      '.article__body',
      '.story-body',
      '.post-content',
      '.entry-content',
      '.post-body',
      '.content-body',
      
      // News-specific
      '.ins_storybody',  // NDTV
      '.story-body__inner',  // BBC
      '.article__content',  // Guardian
      '.article-text',  // Hindu
      '.single-post',  // PageSix, NY Post
      '.entry__content',  // PageSix
      '.single__content',  // PageSix
      '.post__content',  // Various news sites
      '.story__content'  // Various news sites
    ];

    for (const selector of selectors) {
      const element = document.querySelector(selector);
      if (element && element.textContent.trim().length > 100) {
        return element;
      }
    }

    // Fallback: Find largest text container
    return this.findLargestTextContainer();
  },

  /**
   * Find the element with the most paragraph content
   */
  findLargestTextContainer() {
    const candidates = document.querySelectorAll('div, section, article');
    let largest = null;
    let maxParagraphs = 0;

    candidates.forEach(element => {
      const paragraphs = element.querySelectorAll('p');
      const textLength = element.textContent.trim().length;
      
      if (paragraphs.length > maxParagraphs && textLength > 500) {
        maxParagraphs = paragraphs.length;
        largest = element;
      }
    });

    return largest;
  },

  /**
   * Check if element is likely non-content (nav, ads, etc.)
   */
  isNonContentElement(element) {
    const text = element.textContent.toLowerCase();
    const classList = element.className.toLowerCase();
    const id = element.id?.toLowerCase() || '';

    // Check for timestamps (e.g., "2 hours ago", "Published: Jan 10, 2025", "Updated: 3:45 PM")
    const timestampPatterns = [
      /\d{1,2}\s*(hours?|mins?|minutes?|seconds?|days?|weeks?|months?|years?)\s*ago/i,
      /published:?\s*\d/i,
      /updated:?\s*\d/i,
      /\d{1,2}:\d{2}\s*(am|pm)/i,
      /^\s*\d{1,2}\/\d{1,2}\/\d{2,4}\s*$/,  // Date format: 10/18/2025
      /^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2},?\s+\d{4}/i  // Jan 10, 2025
    ];
    
    if (timestampPatterns.some(pattern => pattern.test(text))) {
      return true;
    }

    // Check for navigation/UI text
    const navPatterns = [
      'skip to', 'menu', 'navigation', 'cookie', 'subscribe',
      'newsletter', 'advertisement', 'related articles', 'read more',
      'share this', 'follow us', 'sponsored', 'powered by', 'published',
      'updated', 'posted', 'last modified'
    ];

    if (navPatterns.some(pattern => text.includes(pattern))) {
      return true;
    }

    // Check classes/IDs
    const excludePatterns = [
      'nav', 'menu', 'footer', 'header', 'sidebar', 'ad', 'advertisement',
      'related', 'recommend', 'share', 'social', 'comment', 'cookie',
      'timestamp', 'date', 'time', 'publish', 'author', 'byline'
    ];

    if (excludePatterns.some(pattern => classList.includes(pattern) || id.includes(pattern))) {
      return true;
    }

    return false;
  },

  /**
   * Get XPath of element for precise location
   */
  getXPath(element) {
    if (element.id) {
      return `//*[@id="${element.id}"]`;
    }
    
    const parts = [];
    while (element && element.nodeType === Node.ELEMENT_NODE) {
      let index = 0;
      let sibling = element.previousSibling;
      
      while (sibling) {
        if (sibling.nodeType === Node.ELEMENT_NODE && sibling.nodeName === element.nodeName) {
          index++;
        }
        sibling = sibling.previousSibling;
      }
      
      const tagName = element.nodeName.toLowerCase();
      const pathIndex = index > 0 ? `[${index + 1}]` : '';
      parts.unshift(tagName + pathIndex);
      element = element.parentNode;
    }
    
    return parts.length ? '/' + parts.join('/') : '';
  },

  /**
   * Fallback extraction if no article container found
   */
  fallbackExtraction() {
    console.log('⚠️ Using fallback extraction - extracting ALL <p> tags from page');
    
    const paragraphs = [];
    const allParagraphs = document.querySelectorAll('p');
    let fullText = '';
    
    console.log(`📄 Found ${allParagraphs.length} total <p> tags on page`);
    
    allParagraphs.forEach((p, index) => {
      const text = this.cleanText(p.textContent);
      
      // ✅ VERY LENIENT: Accept even short paragraphs (15+ chars)
      if (text.length < 15) {
        return;
      }
      
      // ✅ Skip ONLY obvious non-content (but be lenient)
      if (this.isNonContentElement(p)) {
        console.log(`   ⏭️ Skipping: "${text.substring(0, 50)}..."`);
        return;
      }
      
      paragraphs.push({
        index: paragraphs.length,  // Use running index, not DOM index
        type: 'p',
        text: text,
        length: text.length,
        xpath: this.getXPath(p)
      });
      fullText += text + '\n\n';
    });
    
    console.log(`✅ Fallback extracted ${paragraphs.length} paragraphs`);

    return { paragraphs, fullText };
  },

  /**
   * Detect page type (news, blog, social media, etc.)
   */
  detectPageType() {
    const url = window.location.href.toLowerCase();
    const hostname = window.location.hostname.toLowerCase();

    // News portals
    const newsPortals = [
      'bbc.com', 'cnn.com', 'nytimes.com', 'theguardian.com', 'reuters.com',
      'ndtv.com', 'timesofindia.com', 'hindustantimes.com', 'thehindu.com'
    ];

    if (newsPortals.some(domain => hostname.includes(domain))) {
      return 'news-article';
    }

    // Check for article indicators
    if (document.querySelector('article') || document.querySelector('[itemtype*="Article"]')) {
      return 'article';
    }

    // Blog detection
    if (url.includes('blog') || hostname.includes('wordpress') || hostname.includes('blogger')) {
      return 'blog-post';
    }

    return 'webpage';
  },

  /**
   * Detect content type from metadata and structure
   */
  detectContentType() {
    // Check meta tags
    const ogType = document.querySelector('meta[property="og:type"]')?.content;
    const articleSection = document.querySelector('meta[property="article:section"]')?.content;
    
    if (ogType === 'article') {
      if (articleSection) {
        return {
          type: 'news-article',
          category: articleSection.toLowerCase(),
          confidence: 0.9
        };
      }
      return { type: 'article', confidence: 0.8 };
    }

    // Check for opinion/editorial indicators
    const title = document.title.toLowerCase();
    const url = window.location.href.toLowerCase();
    
    if (title.includes('opinion') || url.includes('opinion') || 
        title.includes('editorial') || url.includes('editorial')) {
      return { type: 'opinion-piece', confidence: 0.85 };
    }

    // Check for scientific paper
    if (document.querySelector('meta[name="citation_title"]')) {
      return { type: 'scientific-paper', confidence: 0.95 };
    }

    // Default
    return { type: 'general-content', confidence: 0.5 };
  },

  /**
   * Extract title from various sources
   */
  extractTitle() {
    // Try Open Graph
    const ogTitle = document.querySelector('meta[property="og:title"]');
    if (ogTitle) return ogTitle.content;

    // Try headline element
    const h1 = document.querySelector('article h1, .article h1, h1.title, h1.headline, main h1');
    if (h1) return h1.textContent.trim();

    // Fallback to page title
    return document.title || 'Untitled';
  },

  /**
   * Extract metadata (author, date, etc.)
   */
  extractMetadata() {
    const metadata = {
      author: '',
      publishDate: '',
      modifiedDate: '',
      section: '',
      tags: []
    };

    // Author
    const authorMeta = document.querySelector('meta[name="author"], meta[property="article:author"]');
    const authorElement = document.querySelector('[rel="author"], .author, .byline, [itemprop="author"]');
    metadata.author = authorMeta?.content || authorElement?.textContent.trim() || '';

    // Publish date
    const dateMeta = document.querySelector('meta[property="article:published_time"], meta[name="publish-date"]');
    const dateElement = document.querySelector('time[datetime], .publish-date, [itemprop="datePublished"]');
    metadata.publishDate = dateMeta?.content || dateElement?.getAttribute('datetime') || dateElement?.textContent.trim() || '';

    // Section/category
    const sectionMeta = document.querySelector('meta[property="article:section"]');
    metadata.section = sectionMeta?.content || '';

    // Tags
    const tagMeta = document.querySelectorAll('meta[property="article:tag"]');
    metadata.tags = Array.from(tagMeta).map(tag => tag.content);

    return metadata;
  },

  /**
   * Extract images from article
   */
  extractImages() {
    const images = [];
    const articleElement = this.findArticleContainer();
    
    if (!articleElement) return images;

    const imgElements = articleElement.querySelectorAll('img');
    
    imgElements.forEach((img, index) => {
      if (img.width > 100 && img.height > 100) {  // Skip small images (icons, etc.)
        images.push({
          index: index,
          src: img.src,
          alt: img.alt || '',
          caption: img.parentElement.querySelector('figcaption')?.textContent.trim() || ''
        });
      }
    });

    return images;
  },

  /**
   * Clean text content
   */
  cleanText(text) {
    return text
      .replace(/\s+/g, ' ')
      .replace(/\n{3,}/g, '\n\n')
      .trim();
  },

  /**
   * Calculate extraction confidence score
   */
  calculateConfidence(content) {
    let score = 0;

    // Has title
    if (content.title && content.title.length > 5) score += 20;

    // Has paragraphs
    if (content.paragraphs.length > 0) score += 20;
    if (content.paragraphs.length > 3) score += 10;
    if (content.paragraphs.length > 10) score += 10;

    // Has metadata
    if (content.author) score += 10;
    if (content.publishDate) score += 10;

    // Has sufficient text
    if (content.fullText.length > 500) score += 10;
    if (content.fullText.length > 2000) score += 10;

    return Math.min(score, 100);
  }
};

// Make it globally available
if (typeof window !== 'undefined') {
  window.ContentExtractorV2 = ContentExtractorV2;
}
