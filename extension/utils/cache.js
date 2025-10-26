/**
 * Cache Manager - Simple 2-item LRU cache for analysis results
 * Prevents redundant API calls for recently analyzed content
 */

const Cache = {
  // Cache storage (max 2 items)
  storage: new Map(),
  maxSize: 2,

  /**
   * Get item from cache
   * @param {string} key - Cache key (content hash)
   * @returns {object|null} - Cached result or null
   */
  get(key) {
    if (!this.storage.has(key)) {
      return null;
    }

    // Move to end (most recently used)
    const value = this.storage.get(key);
    this.storage.delete(key);
    this.storage.set(key, value);

    console.log('Cache hit:', key);
    return value;
  },

  /**
   * Set item in cache
   * @param {string} key - Cache key (content hash)
   * @param {object} value - Analysis result to cache
   */
  set(key, value) {
    // Remove oldest item if cache is full
    if (this.storage.size >= this.maxSize && !this.storage.has(key)) {
      const firstKey = this.storage.keys().next().value;
      this.storage.delete(firstKey);
      console.log('Cache evicted:', firstKey);
    }

    // Add new item
    this.storage.set(key, value);
    console.log('Cache set:', key);
  },

  /**
   * Clear entire cache
   */
  clear() {
    this.storage.clear();
    console.log('Cache cleared');
  },

  /**
   * Get cache size
   * @returns {number} - Current cache size
   */
  size() {
    return this.storage.size;
  },

  /**
   * Check if key exists in cache
   * @param {string} key - Cache key
   * @returns {boolean}
   */
  has(key) {
    return this.storage.has(key);
  }
};

// Make available globally
window.Cache = Cache;
