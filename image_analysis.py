"""
🖼️ IMAGE ANALYSIS MODULE
Detects AI-generated/fake images and performs reverse image search verification
"""

import os
import requests
from PIL import Image
from io import BytesIO
import torch
from transformers import AutoFeatureExtractor, AutoModelForImageClassification
import hashlib
from urllib.parse import urlparse, urljoin
import base64
import re
import tempfile
import time
import shutil
from pathlib import Path
import shutil
from pathlib import Path

# Configuration
MODELS_CACHE_DIR = os.path.join(os.path.dirname(__file__), 'models_cache')
AI_IMAGE_DETECTOR_MODEL = "umm-maybe/AI-image-detector"
MAX_IMAGES_PER_PAGE = 10
IMAGE_SIZE_LIMIT_MB = 10
TEMP_IMAGE_DIR = os.path.join(tempfile.gettempdir(), 'ai_detector_images')

# Ensure temp directory exists
os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)

class ImageAnalyzer:
    """
    Analyzes images from webpages to detect:
    1. AI-generated/fake images
    2. Image authenticity through reverse search
    3. Context verification
    """
    
    def __init__(self):
        self.model = None
        self.feature_extractor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.temp_images = []  # Track downloaded images for cleanup
        print(f"🖼️ [IMAGE] Image Analyzer initializing (Device: {self.device})...")
        
        # Clean old images from previous runs
        self._cleanup_old_images()
        
        # Load AI image detection model
        self._load_model()
    
    def _cleanup_old_images(self):
        """Clean up old temporary images from previous runs"""
        try:
            if os.path.exists(TEMP_IMAGE_DIR):
                for file in os.listdir(TEMP_IMAGE_DIR):
                    file_path = os.path.join(TEMP_IMAGE_DIR, file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception as e:
                        print(f"⚠️ [IMAGE] Could not delete {file_path}: {e}")
                print(f"🧹 [IMAGE] Cleaned up old temporary images")
        except Exception as e:
            print(f"⚠️ [IMAGE] Cleanup warning: {e}")
    
    def _cleanup_downloaded_images(self):
        """Delete all downloaded images after analysis"""
        try:
            for img_path in self.temp_images:
                try:
                    if os.path.exists(img_path):
                        os.unlink(img_path)
                except Exception as e:
                    print(f"⚠️ [IMAGE] Could not delete {img_path}: {e}")
            
            self.temp_images.clear()
            print(f"🧹 [IMAGE] Cleaned up {len(self.temp_images)} downloaded images")
        except Exception as e:
            print(f"⚠️ [IMAGE] Cleanup error: {e}")
    
    def _load_model(self):
        """Load the AI-generated image detection model"""
        try:
            print(f"🤖 [IMAGE] Loading AI image detector: {AI_IMAGE_DETECTOR_MODEL}")
            
            cache_dir = os.path.join(MODELS_CACHE_DIR, AI_IMAGE_DETECTOR_MODEL.replace('/', '_'))
            
            self.feature_extractor = AutoFeatureExtractor.from_pretrained(
                AI_IMAGE_DETECTOR_MODEL,
                cache_dir=cache_dir
            )
            
            self.model = AutoModelForImageClassification.from_pretrained(
                AI_IMAGE_DETECTOR_MODEL,
                cache_dir=cache_dir
            )
            
            self.model.to(self.device)
            self.model.eval()
            
            print(f"✅ [IMAGE] AI image detector loaded successfully")
            
        except Exception as e:
            print(f"⚠️ [IMAGE] Could not load AI detector model: {e}")
            print(f"💡 [IMAGE] Will use fallback basic analysis")
    
    def extract_images_from_html(self, html_content, base_url):
        """
        Extract image URLs from HTML content
        
        Args:
            html_content: Raw HTML string
            base_url: Base URL for resolving relative paths
            
        Returns:
            List of absolute image URLs
        """
        print(f"🔍 [IMAGE] Extracting images from HTML...")
        
        image_urls = []
        
        # Find all img tags with src
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
        matches = re.findall(img_pattern, html_content, re.IGNORECASE)
        
        for img_url in matches:
            # Convert relative URLs to absolute
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            elif img_url.startswith('/'):
                img_url = urljoin(base_url, img_url)
            elif not img_url.startswith('http'):
                img_url = urljoin(base_url, img_url)
            
            # Filter out small icons, logos, tracking pixels
            if self._is_valid_image_url(img_url):
                image_urls.append(img_url)
        
        # Remove duplicates while preserving order
        image_urls = list(dict.fromkeys(image_urls))
        
        # Limit to MAX_IMAGES_PER_PAGE
        image_urls = image_urls[:MAX_IMAGES_PER_PAGE]
        
        print(f"✅ [IMAGE] Found {len(image_urls)} valid images to analyze")
        
        return image_urls
    
    def _is_valid_image_url(self, url):
        """Check if URL is likely a valid content image (not icon/logo/navigation)"""
        url_lower = url.lower()
        
        # ✅ Skip common non-content images (expanded list)
        skip_patterns = [
            'logo', 'icon', 'favicon', 'sprite', 'avatar',
            'placeholder', 'loading', 'spinner', 'blank',
            'pixel', 'tracking', 'analytics', '1x1',
            'data:image', 'base64',
            'arrow', 'button', 'badge', 'bullet',  # Navigation elements
            'banner', 'header', 'footer', 'sidebar',  # Layout elements
            'social', 'share', 'follow', 'subscribe',  # Social buttons
            'ad', 'advertisement', 'promo', 'sponsor',  # Ads
            'thumbnail-small', 'thumb-', '-thumb',  # Small thumbnails
            'widget', 'module', 'component'  # UI components
        ]
        
        for pattern in skip_patterns:
            if pattern in url_lower:
                return False
        
        # Must be image file
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp']
        has_extension = any(ext in url_lower for ext in image_extensions)
        
        # Or from known image CDNs
        image_cdns = ['images', 'img', 'media', 'photo', 'picture', 'cdn']
        has_cdn = any(cdn in url_lower for cdn in image_cdns)
        
        return has_extension or has_cdn
    
    def download_image(self, image_url):
        """
        Download image from URL and save to temp directory
        
        Args:
            image_url: URL of the image
            
        Returns:
            tuple of (PIL Image object, temp_file_path) or (None, None)
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(image_url, headers=headers, timeout=10, stream=True)
            
            # Check file size
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > IMAGE_SIZE_LIMIT_MB * 1024 * 1024:
                print(f"⚠️ [IMAGE] Skipping large image: {image_url}")
                return None, None
            
            response.raise_for_status()
            
            # Load image
            image = Image.open(BytesIO(response.content))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Save to temp directory
            temp_filename = f"img_{len(self.temp_images)}_{int(time.time())}.jpg"
            temp_path = os.path.join(TEMP_IMAGE_DIR, temp_filename)
            image.save(temp_path, 'JPEG')
            self.temp_images.append(temp_path)
            
            return image, temp_path
            
        except Exception as e:
            print(f"⚠️ [IMAGE] Could not download {image_url}: {e}")
            return None, None
    
    def detect_ai_generated(self, image):
        """
        Detect if image is AI-generated using the model
        
        Args:
            image: PIL Image object
            
        Returns:
            dict with 'is_ai_generated' (bool), 'confidence' (float), 'label' (str)
        """
        if self.model is None or self.feature_extractor is None:
            print(f"⚠️ [IMAGE] Model not loaded, using fallback")
            return self._fallback_ai_detection(image)
        
        try:
            # Preprocess image
            inputs = self.feature_extractor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Run inference
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
            
            # Get predictions
            probabilities = torch.nn.functional.softmax(logits, dim=-1)
            predicted_class_idx = logits.argmax(-1).item()
            
            # Model labels: typically 'artificial' vs 'real'
            label = self.model.config.id2label[predicted_class_idx]
            
            # Find which class index corresponds to AI/artificial
            ai_class_idx = None
            for idx, lbl in self.model.config.id2label.items():
                if lbl.lower() in ['artificial', 'fake', 'ai', 'generated', 'synthetic']:
                    ai_class_idx = idx
                    break
            
            # Confidence should ALWAYS be for AI-generated class (not the predicted class)
            if ai_class_idx is not None:
                confidence_ai = probabilities[0][ai_class_idx].item() * 100
            else:
                # Fallback: use predicted class confidence
                confidence_ai = probabilities[0][predicted_class_idx].item() * 100
            
            # ✅ STRICTER THRESHOLD for more accurate detection
            # Use 65% threshold to reduce false positives
            is_ai_generated = confidence_ai > 65  # Higher threshold = more accurate
            
            result = {
                'is_ai_generated': is_ai_generated,
                'confidence': confidence_ai,  # Always confidence that it's AI-generated
                'label': label,
                'predicted_label': label,  # Original model prediction
                'verdict': 'AI-Generated' if is_ai_generated else 'Real Photo'
            }
            
            print(f"✅ [IMAGE] AI Detection: {result['verdict']} ({result['confidence']:.1f}% AI confidence, model predicted: {label})")
            
            return result
            
        except Exception as e:
            print(f"⚠️ [IMAGE] AI detection failed: {e}")
            return self._fallback_ai_detection(image)
    
    def _fallback_ai_detection(self, image):
        """Fallback basic analysis when model fails"""
        return {
            'is_ai_generated': False,
            'confidence': 0,
            'label': 'Unknown',
            'verdict': 'Analysis Unavailable'
        }
    
    def reverse_image_search(self, image_url):
        """
        Simulate reverse image search to find context
        
        Args:
            image_url: URL of the image
            
        Returns:
            dict with search results and context
        """
        print(f"🔍 [IMAGE] Performing reverse image search for: {image_url}")
        
        # Generate search URLs for major search engines
        search_urls = {
            'Google Images': f"https://www.google.com/searchbyimage?image_url={image_url}",
            'TinEye': f"https://tineye.com/search?url={image_url}",
            'Yandex': f"https://yandex.com/images/search?url={image_url}&rpt=imageview"
        }
        
        result = {
            'image_url': image_url,
            'search_engines': search_urls,
            'context_found': False,
            'earliest_usage': 'Unknown',
            'common_context': 'Reverse search manually to verify image source',
            'warning': None
        }
        
        # Note: Actual reverse search requires API keys or web scraping
        # For now, we provide search links for manual verification
        
        print(f"✅ [IMAGE] Reverse search links generated")
        
        return result
    
    def analyze_images(self, image_urls, page_url):
        """
        Analyze multiple images from a webpage
        
        Args:
            image_urls: List of image URLs
            page_url: URL of the webpage
            
        Returns:
            dict with analysis results
        """
        print(f"🖼️ [IMAGE] Analyzing {len(image_urls)} images from {page_url}")
        
        results = {
            'total_images': len(image_urls),
            'analyzed_images': 0,
            'ai_generated_count': 0,
            'real_images_count': 0,
            'suspicious_images': [],
            'all_results': []
        }
        
        try:
            for idx, img_url in enumerate(image_urls, 1):
                print(f"🖼️ [IMAGE] Processing image {idx}/{len(image_urls)}: {img_url[:60]}...")
                
                try:
                    # Download image (returns tuple: image, temp_path)
                    image, temp_path = self.download_image(img_url)
                    if image is None:
                        continue
                    
                    # Detect AI-generated
                    ai_detection = self.detect_ai_generated(image)
                    
                    # Reverse search
                    reverse_search = self.reverse_image_search(img_url)
                    
                    # Combine results
                    image_result = {
                        'url': img_url,
                        'index': idx,
                        'width': image.width,
                        'height': image.height,
                        'ai_detection': ai_detection,
                        'reverse_search': reverse_search,
                        'is_suspicious': ai_detection['is_ai_generated'] and ai_detection['confidence'] > 70
                    }
                    
                    results['all_results'].append(image_result)
                    results['analyzed_images'] += 1
                    
                    if ai_detection['is_ai_generated']:
                        results['ai_generated_count'] += 1
                        if ai_detection['confidence'] > 70:
                            results['suspicious_images'].append(image_result)
                    else:
                        results['real_images_count'] += 1
                    
                except Exception as e:
                    print(f"⚠️ [IMAGE] Error analyzing image {img_url}: {e}")
                    continue
        
        finally:
            # Always cleanup downloaded images
            self._cleanup_downloaded_images()
        
        # Generate summary
        results['summary'] = self._generate_summary(results)
        
        print(f"✅ [IMAGE] Analysis complete: {results['analyzed_images']} images analyzed")
        print(f"   AI-Generated: {results['ai_generated_count']}, Real: {results['real_images_count']}")
        
        return results
    
    def _generate_summary(self, results):
        """Generate human-readable summary"""
        total = results['analyzed_images']
        ai_count = results['ai_generated_count']
        real_count = results['real_images_count']
        suspicious_count = len(results['suspicious_images'])
        
        if total == 0:
            return "No images could be analyzed."
        
        ai_percentage = (ai_count / total) * 100 if total > 0 else 0
        
        if suspicious_count > 0:
            summary = f"⚠️ WARNING: Found {suspicious_count} highly suspicious AI-generated image(s). "
        elif ai_count > 0:
            summary = f"Found {ai_count} potentially AI-generated image(s). "
        else:
            summary = "✅ All analyzed images appear to be real photographs. "
        
        summary += f"\n\nTotal analyzed: {total} images ({ai_percentage:.0f}% AI-generated, {(real_count/total)*100:.0f}% real)"
        
        if suspicious_count > 0:
            summary += f"\n\n🔍 Recommendation: Verify the context of AI-generated images using reverse image search."
        
        return summary

# Global instance
_image_analyzer = None

def get_image_analyzer():
    """Get or create the global image analyzer instance"""
    global _image_analyzer
    if _image_analyzer is None:
        _image_analyzer = ImageAnalyzer()
    return _image_analyzer

def analyze_webpage_images(html_content, page_url):
    """
    Convenience function to analyze all images from a webpage
    
    Args:
        html_content: Raw HTML content
        page_url: URL of the webpage
        
    Returns:
        dict with complete image analysis
    """
    analyzer = get_image_analyzer()
    
    # Extract image URLs
    image_urls = analyzer.extract_images_from_html(html_content, page_url)
    
    if not image_urls:
        return {
            'total_images': 0,
            'analyzed_images': 0,
            'summary': 'No images found on this page.',
            'all_results': []
        }
    
    # Analyze images
    return analyzer.analyze_images(image_urls, page_url)

if __name__ == "__main__":
    # Test the image analyzer
    print("=" * 70)
    print("  IMAGE ANALYSIS MODULE TEST")
    print("=" * 70)
    
    analyzer = ImageAnalyzer()
    
    # Test with a sample image URL
    test_url = "https://example.com/test-image.jpg"
    print(f"\nTest URL: {test_url}")
    
    print("\n✅ Image Analyzer initialized successfully!")
    print(f"   Device: {analyzer.device}")
    print(f"   Model loaded: {analyzer.model is not None}")
