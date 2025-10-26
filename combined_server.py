# -*- coding: utf-8 -*-
"""
LinkScout Combined Server V2 - COMPLETE MERGER
Smart Analysis. Simple Answers.

Combines EVERYTHING from both servers:
1. Groq AI agentic analysis with 4 agents (from agentic_server.py)
2. Pre-trained models (RoBERTa, Emotion, NER, Hate Speech, Clickbait, Bias)
3. Custom trained model (D:\mis\misinformation_model\final)
4. Reinforcement Learning
5. Image Analysis  
6. Google Search Integration
7. All 8 Revolutionary Detection Phases
8. Category/Label detection
9. Reference links and sources
10. Complete analysis report with "what's right", "what's wrong", "why it matters"
"""

import sys
import io
import os

# Force UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configure D drive cache for models
os.environ['HF_HOME'] = r'D:\huggingface_cache'
os.environ['HUGGINGFACE_HUB_CACHE'] = r'D:\huggingface_cache'
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
os.environ['SAFETENSORS_FAST_GPU'] = '1'

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import json
import re
import torch
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Import transformers for pre-trained models
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    AutoModelForTokenClassification,
    AutoModel
)
import transformers
transformers.logging.set_verbosity_error()

# Import RL module
try:
    from reinforcement_learning import get_rl_agent, initialize_rl_agent
except:
    def get_rl_agent() -> Optional[Any]: return None
    def initialize_rl_agent(*args, **kwargs) -> Optional[Any]: return None

# Import Image Analysis
try:
    from image_analysis import analyze_webpage_images, get_image_analyzer
except:
    def analyze_webpage_images(*args, **kwargs) -> Dict: return {"suspicious": False, "total_images": 0}
    def get_image_analyzer() -> Optional[Any]: return None

# Import Phase 1 modules (Linguistic, Claims, Sources)
try:
    from linguistic_fingerprint import analyze_text_fingerprint
except:
    def analyze_text_fingerprint(*args, **kwargs) -> Dict: 
        return {'fingerprint_score': 0, 'verdict': 'UNKNOWN', 'patterns': [], 'confidence': 0}

try:
    from claim_verifier import verify_text_claims
except:
    def verify_text_claims(*args, **kwargs) -> Dict: 
        return {'total_claims': 0, 'false_claims': 0, 'false_percentage': 0, 'detailed_results': []}

try:
    from source_credibility import analyze_text_sources
except:
    def analyze_text_sources(*args, **kwargs) -> Dict: 
        return {'sources_analyzed': 0, 'average_credibility': 50, 'verdict': 'UNKNOWN', 'sources': []}

# Import Phase 2 modules (Verification Network, Entity, Propaganda)
try:
    from verification_network import verify_claims_network
except:
    def verify_claims_network(*args, **kwargs) -> Dict: 
        return {'total_claims': 0, 'verified_claims': 0, 'verification_score': 0, 'verdict': 'NO_CLAIMS'}

try:
    from entity_verifier import verify_text_entities
except:
    def verify_text_entities(*args, **kwargs) -> Dict: 
        return {'total_entities': 0, 'verified_entities': 0, 'suspicious_entities': 0, 'fake_expert_detected': False}

try:
    from propaganda_detector import detect_text_propaganda
except:
    def detect_text_propaganda(*args, **kwargs) -> Dict: 
        return {
            'total_techniques': 0, 
            'techniques': [],  # ✅ ALWAYS RETURN ARRAY
            'total_instances': 0,
            'propaganda_score': 0, 
            'verdict': 'UNKNOWN'
        }

# Import Phase 3 modules (Contradictions, Network Analysis)
try:
    from contradiction_detector import detect_text_contradictions
except:
    def detect_text_contradictions(*args, **kwargs) -> Dict: 
        return {'total_contradictions': 0, 'high_severity': 0, 'contradiction_score': 0, 'verdict': 'NO_CONTRADICTIONS'}

try:
    from network_analyzer import analyze_network_patterns
except:
    def analyze_network_patterns(*args, **kwargs) -> Dict: 
        return {'bot_score': 0, 'astroturfing_score': 0, 'viral_manipulation_score': 0, 'verdict': 'ORGANIC'}

# Import local false claims database
try:
    from known_false_claims import check_known_false_claim, get_source_credibility_override
except:
    def check_known_false_claim(*args, **kwargs) -> Optional[Dict]: return None
    def get_source_credibility_override(*args, **kwargs) -> Optional[float]: return None

# Import Google Search
try:
    from google_search import google_web_search
    print("✅ Google Search imported successfully")
except Exception as e:
    print(f"⚠️ Google Search import failed: {e}")
    def google_web_search(*args, **kwargs) -> List: 
        print("⚠️ Using fallback google_web_search (returns empty list)")
        return []

# Groq API Configuration
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

app = Flask(__name__)
CORS(app)

# Initialize device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"📱 Using device: {device}")

print("🚀 Loading AI models...")

# RoBERTa for fake news detection
print("Loading RoBERTa fake news detector...")
try:
    roberta_tokenizer = AutoTokenizer.from_pretrained(
        "hamzab/roberta-fake-news-classification",
        cache_dir=r'D:\huggingface_cache',
        local_files_only=True
    )
    roberta_model = AutoModelForSequenceClassification.from_pretrained(
        "hamzab/roberta-fake-news-classification",
        cache_dir=r'D:\huggingface_cache',
        local_files_only=True
    ).to(device)
    roberta_model.eval()  # Set to evaluation mode
    print("✅ RoBERTa loaded")
except Exception as e:
    print(f"❌ RoBERTa loading failed: {e}")
    raise

# Emotion classifier
print("Loading emotion classifier...")
emotion_tokenizer = AutoTokenizer.from_pretrained(
    "j-hartmann/emotion-english-distilroberta-base",
    cache_dir=r'D:\huggingface_cache',
    local_files_only=True
)
emotion_model = AutoModelForSequenceClassification.from_pretrained(
    "j-hartmann/emotion-english-distilroberta-base",
    cache_dir=r'D:\huggingface_cache',
    local_files_only=True
).to(device)
print("✅ Emotion model loaded")

# NER for entity extraction
print("⏳ NER model: lazy loading (loads on first use)")
ner_tokenizer = None
ner_model = None

# Hate Speech Detector
print("⏳ Hate Speech detector: lazy loading (loads on first use)")
hate_speech_tokenizer = None
hate_speech_model = None

# Clickbait Detector
print("⏳ Clickbait detector: lazy loading (loads on first use)")
clickbait_tokenizer = None
clickbait_model = None

# Bias Detector
print("⏳ Bias detector: lazy loading (loads on first use)")
bias_tokenizer = None
bias_model = None

# === ADDITIONAL FAKE NEWS MODELS FOR ENSEMBLE VOTING ===
print("⏳ Additional fake news models: lazy loading (loads on first use)")

# Fake News BERT #2
fake_news_bert_tokenizer = None
fake_news_bert_model = None

# Fake News Model #3 (Pulk17)
fake_news_pulk_tokenizer = None
fake_news_pulk_model = None

# Custom trained model (deferred loading)
print("Custom model: deferred loading on first use...")
custom_model_path = r'D:\mis\misinformation_model\final'
custom_tokenizer = None
custom_model = None
_custom_model_disabled = False

print("✅ Core models loaded (RoBERTa, Emotion, NER, Hate, Clickbait, Bias)")
print("✅ Ensemble models ready (3 fake news detectors + custom model)")

# ========================================
# NEWS CATEGORIES (from server_chunk_analysis.py)
# ========================================
NEWS_CATEGORIES = {
    'Politics': ['election', 'government', 'minister', 'parliament', 'president', 'prime minister', 'political', 'congress', 'vote', 'चुनाव', 'सरकार'],
    'War & Conflict': ['war', 'military', 'army', 'attack', 'soldier', 'weapon', 'conflict', 'battle', 'युद्ध', 'सेना'],
    'Health & Wellness': ['health', 'hospital', 'doctor', 'medicine', 'disease', 'vaccine', 'covid', 'patient', 'स्वास्थ्य'],
    'Technology': ['technology', 'tech', 'ai', 'software', 'computer', 'internet', 'digital', 'app', 'प्रौद्योगिकी'],
    'Business & Finance': ['business', 'company', 'market', 'economy', 'stock', 'finance', 'investment', 'व्यापार'],
    'Sports': ['sport', 'football', 'cricket', 'match', 'player', 'team', 'game', 'खेल', 'क्रिकेट'],
    'Entertainment': ['movie', 'film', 'actor', 'music', 'entertainment', 'show', 'series', 'मनोरंजन'],
    'Crime & Law': ['crime', 'police', 'arrest', 'murder', 'theft', 'investigation', 'criminal', 'court', 'अपराध'],
    'Environment & Climate': ['climate', 'environment', 'pollution', 'weather', 'temperature', 'carbon', 'पर्यावरण'],
    'Celebrity & Gossip': ['celebrity', 'star', 'actress', 'bollywood', 'hollywood', 'married', 'wedding', 'सेलिब्रिटी'],
    'Education': ['education', 'school', 'university', 'student', 'teacher', 'exam', 'college', 'शिक्षा'],
    'Food & Cuisine': ['food', 'restaurant', 'recipe', 'chef', 'cooking', 'cuisine', 'dish', 'भोजन'],
    'Travel & Tourism': ['travel', 'tourist', 'tourism', 'vacation', 'holiday', 'destination', 'hotel', 'यात्रा'],
    'Science & Research': ['science', 'research', 'study', 'scientist', 'discovery', 'experiment', 'विज्ञान'],
    'Other / General / Info': ['info', 'information', 'explained', 'details', 'guide', 'news', 'article']
}

def detect_categories(text):
    """Detect news categories based on keywords"""
    text_lower = text.lower()
    category_scores = {}
    for category, keywords in NEWS_CATEGORIES.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        if score > 0:
            category_scores[category] = score
    
    if not category_scores:
        return ['Other / General / Info']
    
    sorted_cats = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
    top_score = sorted_cats[0][1]
    min_threshold = max(2, int(top_score * 0.5))
    
    result = [cat for cat, score in sorted_cats if score >= min_threshold and cat != 'Other / General / Info']
    return result if result else ['Other / General / Info']

# ========================================
# LAZY LOADING FUNCTIONS (Memory Optimization)
# ========================================

def load_ner_model():
    """Load NER model on first use"""
    global ner_tokenizer, ner_model
    if ner_tokenizer is None:
        print("🔄 Loading NER model...")
        ner_tokenizer = AutoTokenizer.from_pretrained(
            "dslim/bert-base-NER",
            cache_dir=r'D:\huggingface_cache',
            local_files_only=True
        )
        ner_model = AutoModelForTokenClassification.from_pretrained(
            "dslim/bert-base-NER",
            cache_dir=r'D:\huggingface_cache',
            local_files_only=True
        ).to(device)
        print("✅ NER model loaded")

def load_hate_speech_model():
    """Load Hate Speech model on first use"""
    global hate_speech_tokenizer, hate_speech_model
    if hate_speech_tokenizer is None:
        print("🔄 Loading Hate Speech detector...")
        hate_speech_tokenizer = AutoTokenizer.from_pretrained(
            "facebook/roberta-hate-speech-dynabench-r4-target",
            cache_dir=r'D:\huggingface_cache',
            local_files_only=True
        )
        hate_speech_model = AutoModelForSequenceClassification.from_pretrained(
            "facebook/roberta-hate-speech-dynabench-r4-target",
            cache_dir=r'D:\huggingface_cache',
            local_files_only=True
        ).to(device)
        print("✅ Hate Speech detector loaded")

def load_clickbait_model():
    """Load Clickbait model on first use"""
    global clickbait_tokenizer, clickbait_model
    if clickbait_tokenizer is None:
        print("🔄 Loading Clickbait detector...")
        clickbait_tokenizer = AutoTokenizer.from_pretrained(
            "elozano/bert-base-cased-clickbait-news",
            cache_dir=r'D:\huggingface_cache',
            local_files_only=True
        )
        clickbait_model = AutoModelForSequenceClassification.from_pretrained(
            "elozano/bert-base-cased-clickbait-news",
            cache_dir=r'D:\huggingface_cache',
            local_files_only=True
        ).to(device)
        print("✅ Clickbait detector loaded")

def load_bias_model():
    """Load Bias model on first use"""
    global bias_tokenizer, bias_model
    if bias_tokenizer is None:
        print("🔄 Loading Bias detector...")
        bias_tokenizer = AutoTokenizer.from_pretrained(
            "valurank/distilroberta-bias",
            cache_dir=r'D:\huggingface_cache',
            local_files_only=True
        )
        bias_model = AutoModelForSequenceClassification.from_pretrained(
            "valurank/distilroberta-bias",
            cache_dir=r'D:\huggingface_cache',
            local_files_only=True
        ).to(device)
        print("✅ Bias detector loaded")

def load_fake_news_bert_model():
    """Load Fake News BERT #2 model on first use"""
    global fake_news_bert_tokenizer, fake_news_bert_model
    if fake_news_bert_tokenizer is None:
        try:
            print("🔄 Loading Fake News BERT #2...")
            fake_news_bert_tokenizer = AutoTokenizer.from_pretrained(
                "jy46604790/Fake-News-Bert-Detect",
                cache_dir=r'D:\huggingface_cache',
                local_files_only=True
            )
            fake_news_bert_model = AutoModelForSequenceClassification.from_pretrained(
                "jy46604790/Fake-News-Bert-Detect",
                cache_dir=r'D:\huggingface_cache',
                local_files_only=True
            ).to(device)
            fake_news_bert_model.eval()
            print("✅ Fake News BERT #2 loaded")
        except Exception as e:
            print(f"⚠️ Fake News BERT #2 not available: {e}")

def load_fake_news_pulk_model():
    """Load Fake News Pulk17 model on first use"""
    global fake_news_pulk_tokenizer, fake_news_pulk_model
    if fake_news_pulk_tokenizer is None:
        try:
            print("🔄 Loading Fake News Pulk17...")
            fake_news_pulk_tokenizer = AutoTokenizer.from_pretrained(
                "Pulk17/Fake-News-Detection",
                cache_dir=r'D:\huggingface_cache',
                local_files_only=True
            )
            fake_news_pulk_model = AutoModelForSequenceClassification.from_pretrained(
                "Pulk17/Fake-News-Detection",
                cache_dir=r'D:\huggingface_cache',
                local_files_only=True
            ).to(device)
            fake_news_pulk_model.eval()
            print("✅ Fake News Pulk17 loaded")
        except Exception as e:
            print(f"⚠️ Fake News Pulk17 not available: {e}")

def load_custom_model():
    """Load your custom trained model on first use"""
    global custom_tokenizer, custom_model, _custom_model_disabled
    if _custom_model_disabled:
        return False
    if custom_tokenizer is None:
        try:
            print("🔄 Loading custom trained model...")
            custom_tokenizer = AutoTokenizer.from_pretrained(
                custom_model_path,
                cache_dir=r'D:\huggingface_cache',
                local_files_only=True
            )
            custom_model = AutoModelForSequenceClassification.from_pretrained(
                custom_model_path,
                cache_dir=r'D:\huggingface_cache',
                local_files_only=True
            ).to(device)
            custom_model.eval()
            print("✅ Custom model loaded")
            return True
        except Exception as e:
            print(f"⚠️ Custom model not available: {e}")
            _custom_model_disabled = True
            return False
    return True

# ========================================
# HELPER FUNCTIONS FOR PRE-TRAINED MODELS
# ========================================

def get_emotion(text):
    """Get emotion from text"""
    try:
        inputs = emotion_tokenizer(text[:512], return_tensors="pt", truncation=True, padding=True).to(device)
        with torch.no_grad():
            outputs = emotion_model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            scores = probs[0].cpu().tolist()
            emotions = ['anger', 'disgust', 'fear', 'joy', 'neutral', 'sadness', 'surprise']
            max_idx = scores.index(max(scores))
            return emotions[max_idx], max(scores)
    except:
        return 'neutral', 0.5

def get_entities(text):
    """✅ REGEX-BASED: Extract entities using simple pattern matching (no ML model needed!)"""
    try:
        print(f"   🔍 [ENTITIES] Starting regex-based entity extraction from text ({len(text)} chars)...")
        
        import re
        
        entities = []
        
        # Pattern 1: Capitalized names (2-4 words)
        # Matches: "Siviwe Gwarube", "South African", "Department of Basic Education"
        name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b'
        names = re.findall(name_pattern, text)
        entities.extend(names)
        
        # Pattern 2: Organizations with common suffixes
        # Matches: "BBC News", "United Nations", etc.
        org_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:News|Department|Ministry|Company|Corporation|Institute|University|School|Hospital|Police|Court))\b'
        orgs = re.findall(org_pattern, text)
        entities.extend(orgs)
        
        # Pattern 3: All-caps acronyms (2-6 letters)
        # Matches: "BBC", "USA", "NATO"
        acronym_pattern = r'\b([A-Z]{2,6})\b'
        acronyms = re.findall(acronym_pattern, text)
        entities.extend(acronyms)
        
        # Pattern 4: Proper nouns starting with "The"
        # Matches: "The Guardian", "The White House"
        the_pattern = r'\b(The\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        the_entities = re.findall(the_pattern, text)
        entities.extend(the_entities)
        
        print(f"   🔍 [ENTITIES] Found {len(entities)} raw entities")
        
        # Clean and filter entities
        cleaned_entities = []
        skip_words = {'The', 'This', 'That', 'These', 'Those', 'There', 'Their', 'Then', 'When', 'Where', 'What', 'Which', 'Who', 'How', 'Why', 'Can', 'Could', 'Should', 'Would', 'Will', 'May', 'Might', 'Must'}
        
        for entity in entities:
            # Skip if too short
            if len(entity) < 2:
                continue
            
            # Skip common words that aren't entities
            if entity in skip_words:
                continue
            
            # Skip if it's just a single common word
            words = entity.split()
            if len(words) == 1 and entity in {'It', 'In', 'On', 'At', 'By', 'For', 'With', 'From', 'To', 'Of', 'As', 'Is', 'Was', 'Are', 'Were', 'Be', 'Been', 'Being', 'Have', 'Has', 'Had', 'Do', 'Does', 'Did', 'But', 'And', 'Or', 'Not', 'If', 'So'}:
                continue
            
            # Normalize whitespace
            entity = ' '.join(entity.split())
            
            if entity:
                cleaned_entities.append(entity)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_entities = []
        for entity in cleaned_entities:
            entity_lower = entity.lower()
            if entity_lower not in seen:
                seen.add(entity_lower)
                unique_entities.append(entity)
        
        # Limit to 10 most relevant entities
        final_entities = unique_entities[:10]
        
        print(f"   ✅ [ENTITIES] Extracted {len(final_entities)} unique entities: {final_entities}")
        return final_entities
        
    except Exception as e:
        print(f"⚠️ [ENTITIES] Entity extraction error: {e}")
        import traceback
        traceback.print_exc()
        return []

def detect_hate_speech(text):
    """Detect hate speech"""
    try:
        load_hate_speech_model()  # Lazy load on first use
        inputs = hate_speech_tokenizer(text[:512], return_tensors="pt", truncation=True, padding=True).to(device)
        with torch.no_grad():
            outputs = hate_speech_model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            hate_prob = float(probs[0][1].cpu())
            return hate_prob
    except:
        return 0.0

def detect_clickbait(text):
    """Detect clickbait"""
    try:
        load_clickbait_model()  # Lazy load on first use
        inputs = clickbait_tokenizer(text[:512], return_tensors="pt", truncation=True, padding=True).to(device)
        with torch.no_grad():
            outputs = clickbait_model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            clickbait_prob = float(probs[0][1].cpu())
            return clickbait_prob
    except:
        return 0.0

def detect_bias(text):
    """Detect bias"""
    try:
        load_bias_model()  # Lazy load on first use
        inputs = bias_tokenizer(text[:512], return_tensors="pt", truncation=True, padding=True).to(device)
        with torch.no_grad():
            outputs = bias_model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            labels = ['neutral', 'biased']
            max_idx = torch.argmax(probs[0]).item()
            return labels[max_idx], float(probs[0][max_idx].cpu())
    except:
        return 'neutral', 0.5

def analyze_with_custom_model(text):
    """Analyze using custom trained model"""
    global custom_tokenizer, custom_model, _custom_model_disabled
    
    if _custom_model_disabled:
        return {'misinformation_probability': 0, 'reliable_probability': 1}
    
    if custom_tokenizer is None or custom_model is None:
        try:
            print(f"Loading custom model from {custom_model_path}...")
            custom_tokenizer = AutoTokenizer.from_pretrained(custom_model_path, local_files_only=True)
            custom_model = AutoModelForSequenceClassification.from_pretrained(custom_model_path, local_files_only=True).to(device)
            print("✅ Custom model loaded")
        except Exception as e:
            print(f"⚠️ Custom model not available: {e}")
            _custom_model_disabled = True
            return {'misinformation_probability': 0, 'reliable_probability': 1}
    
    try:
        inputs = custom_tokenizer(text[:512], return_tensors="pt", truncation=True, padding=True).to(device)
        with torch.no_grad():
            outputs = custom_model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            return {
                'misinformation_probability': float(probs[0][1].cpu()),
                'reliable_probability': float(probs[0][0].cpu())
            }
    except:
        return {'misinformation_probability': 0, 'reliable_probability': 1}

def get_ml_misinformation_prediction(text: str) -> float:
    """
    🎯 ENSEMBLE VOTING: Get ML model prediction using ALL 4 fake news models
    
    Models used:
    1. hamzab/roberta-fake-news-classification (RoBERTa) - ALWAYS LOADED
    2. jy46604790/Fake-News-Bert-Detect (BERT #2) - Lazy loaded
    3. Pulk17/Fake-News-Detection (Pulk17) - Lazy loaded
    4. Your custom trained model - Lazy loaded
    
    Voting Strategy:
    - Each model gets 1 vote (weight based on confidence)
    - Final score = weighted average of all available models
    - Minimum 1 model (RoBERTa), Maximum 4 models
    
    Returns:
        float: Misinformation probability as percentage (0-100)
    """
    try:
        if not text or len(text.strip()) < 10:
            return 0.0
            
        text_sample = text[:512]
        model_predictions = []
        model_names = []
        
        # === MODEL 1: RoBERTa (ALWAYS AVAILABLE) ===
        try:
            inputs = roberta_tokenizer(text_sample, return_tensors="pt", truncation=True, padding=True, max_length=512)
            input_ids = inputs['input_ids'].to(device)
            attention_mask = inputs['attention_mask'].to(device)
            
            with torch.no_grad():
                outputs = roberta_model(input_ids=input_ids, attention_mask=attention_mask)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
                fake_prob = float(probs[0][1].cpu().item())  # Index 1 = FAKE
                
            model_predictions.append(fake_prob * 100)
            model_names.append(f"RoBERTa:{fake_prob*100:.1f}%")
        except Exception as e:
            print(f"⚠️ RoBERTa prediction error: {e}")
        
        # === MODEL 2: Fake News BERT #2 (LAZY LOAD) ===
        try:
            load_fake_news_bert_model()
            if fake_news_bert_tokenizer is not None:
                inputs = fake_news_bert_tokenizer(text_sample, return_tensors="pt", truncation=True, padding=True, max_length=512)
                input_ids = inputs['input_ids'].to(device)
                attention_mask = inputs['attention_mask'].to(device)
                
                with torch.no_grad():
                    outputs = fake_news_bert_model(input_ids=input_ids, attention_mask=attention_mask)
                    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
                    # Assuming same label mapping: [0]=REAL, [1]=FAKE
                    fake_prob = float(probs[0][1].cpu().item())
                    
                model_predictions.append(fake_prob * 100)
                model_names.append(f"BERT2:{fake_prob*100:.1f}%")
        except Exception as e:
            print(f"⚠️ BERT #2 prediction error: {e}")
        
        # === MODEL 3: Pulk17 Fake News Detection (LAZY LOAD) ===
        try:
            load_fake_news_pulk_model()
            if fake_news_pulk_tokenizer is not None:
                inputs = fake_news_pulk_tokenizer(text_sample, return_tensors="pt", truncation=True, padding=True, max_length=512)
                input_ids = inputs['input_ids'].to(device)
                attention_mask = inputs['attention_mask'].to(device)
                
                with torch.no_grad():
                    outputs = fake_news_pulk_model(input_ids=input_ids, attention_mask=attention_mask)
                    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
                    # Assuming same label mapping: [0]=REAL, [1]=FAKE
                    fake_prob = float(probs[0][1].cpu().item())
                    
                model_predictions.append(fake_prob * 100)
                model_names.append(f"Pulk17:{fake_prob*100:.1f}%")
        except Exception as e:
            print(f"⚠️ Pulk17 prediction error: {e}")
        
        # === MODEL 4: Your Custom Trained Model (LAZY LOAD) ===
        try:
            if load_custom_model():
                inputs = custom_tokenizer(text_sample, return_tensors="pt", truncation=True, padding=True, max_length=512)
                input_ids = inputs['input_ids'].to(device)
                attention_mask = inputs['attention_mask'].to(device)
                
                with torch.no_grad():
                    outputs = custom_model(input_ids=input_ids, attention_mask=attention_mask)
                    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
                    # Assuming: [0]=REAL, [1]=FAKE
                    fake_prob = float(probs[0][1].cpu().item())
                    
                model_predictions.append(fake_prob * 100)
                model_names.append(f"Custom:{fake_prob*100:.1f}%")
        except Exception as e:
            print(f"⚠️ Custom model prediction error: {e}")
        
        # === ENSEMBLE VOTING: Calculate weighted average ===
        if len(model_predictions) == 0:
            print(f"⚠️ No models available for prediction!")
            return 0.0
        
        # Simple average (all models have equal weight)
        ensemble_score = sum(model_predictions) / len(model_predictions)
        
        print(f"   🎯 ENSEMBLE ({len(model_predictions)} models): {ensemble_score:.1f}% fake")
        print(f"      Models: {' | '.join(model_names)}")
        
        return ensemble_score
        
    except Exception as e:
        print(f"⚠️ ML ensemble prediction error: {e}")
        import traceback
        traceback.print_exc()
        return 0.0

def analyze_with_pretrained_models(text: str) -> Dict:
    """🎯 ENHANCED: Comprehensive analysis with ALL models + ENSEMBLE VOTING"""
    try:
        print(f"🔍 [DEBUG] analyze_with_pretrained_models() called with text length: {len(text)} chars")
        
        # 1. ENSEMBLE FAKE NEWS DETECTION (4 models voting together)
        ensemble_fake_score = get_ml_misinformation_prediction(text)  # 0-100 scale
        fake_prob = ensemble_fake_score / 100.0  # Convert to 0-1
        real_prob = 1.0 - fake_prob
        
        # 2. Emotion analysis
        emotion, emotion_score = get_emotion(text)
        
        # 3. Named entities
        print(f"🔍 [DEBUG] About to call get_entities()...")
        named_entities = get_entities(text)
        print(f"🔍 [DEBUG] get_entities() returned: {named_entities}")
        
        # 4. Hate speech
        hate_prob = detect_hate_speech(text)
        
        # 5. Clickbait
        clickbait_prob = detect_clickbait(text)
        
        # 6. Bias
        bias_label, bias_score = detect_bias(text)
        
        # 7. Custom model (already included in ensemble above)
        custom_result = analyze_with_custom_model(text)
        
        # 8. Categories
        categories = detect_categories(text)
        
        return {
            'fake_probability': fake_prob,
            'real_probability': real_prob,
            'ensemble_fake_score': ensemble_fake_score,  # NEW: 0-100 scale
            'ensemble_models_used': 4,  # NEW: Number of models in ensemble
            'emotion': emotion,
            'emotion_score': emotion_score,
            'named_entities': named_entities,
            'hate_probability': hate_prob,
            'clickbait_probability': clickbait_prob,
            'bias_label': bias_label,
            'bias_score': bias_score,
            'custom_model_misinformation': custom_result['misinformation_probability'],
            'custom_model_reliable': custom_result['reliable_probability'],
            'categories': categories,
            'labels': categories  # Alias for frontend
        }
    except Exception as e:
        print(f"Pre-trained models error: {e}")
        return {
            'fake_probability': 0,
            'real_probability': 1,
            'emotion': 'neutral',
            'named_entities': [],
            'hate_probability': 0,
            'clickbait_probability': 0,
            'bias_label': 'neutral',
            'categories': ['Other / General / Info'],
            'labels': ['Other / General / Info']
        }

# ========================================
# GROQ AI AGENTIC SYSTEM (4 Agents)
# ========================================

class GroqAI:
    """Full Groq AI agentic system with 4 agents"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    def call_groq_api(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 1500) -> str:
        """Call Groq API with exponential backoff for rate limits"""
        import time
        
        max_retries = 3
        base_delay = 2  # Start with 2 seconds
        
        for attempt in range(max_retries):
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": GROQ_MODEL,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "top_p": 1,
                    "stream": False
                }
                
                print(f"   🔄 Calling Groq API (attempt {attempt + 1}/{max_retries})...")
                response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=45)
                
                print(f"   📡 Groq API response status: {response.status_code}")
                response.raise_for_status()
                
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    print(f"   ✅ Groq API success - {len(content)} chars returned")
                    return content
                else:
                    print(f"   ⚠️ Groq API returned unexpected format: {result}")
                    return "Analysis unavailable - unexpected API response format."
            
            except requests.exceptions.Timeout:
                print(f"   ⏱️ Groq API timeout (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(base_delay * (2 ** attempt))
                    continue
                return "⚠️ AI analysis temporarily unavailable (timeout). Analysis based on ML models."
            
            except requests.exceptions.ConnectionError as e:
                print(f"   🔌 Groq API connection error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(base_delay)
                    continue
                return "⚠️ AI analysis temporarily unavailable (connection error). Analysis based on ML models."
            
            except requests.exceptions.HTTPError as e:
                print(f"   ⚠️ Groq API HTTP error: {e.response.status_code}")
                if hasattr(e, 'response') and e.response is not None:
                    try:
                        error_detail = e.response.json()
                        print(f"   Error details: {error_detail}")
                    except:
                        print(f"   Error text: {e.response.text[:200]}")
                
                if hasattr(e, 'response') and e.response.status_code == 429:  # Rate limit
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)  # Exponential backoff: 2s, 4s, 8s
                        print(f"   ⏳ Groq API rate limit - waiting {delay}s before retry...")
                        time.sleep(delay)
                        continue
                    else:
                        print(f"   ❌ Groq API rate limit exceeded after {max_retries} retries")
                        return "⚠️ AI analysis temporarily unavailable (rate limit). Analysis based on ML models."
                else:
                    print(f"   ❌ Groq API HTTP error: {e}")
                    return "⚠️ AI analysis temporarily unavailable. Analysis based on ML models."
            
            except KeyError as e:
                print(f"   ⚠️ Groq API response parsing error: {e}")
                return "⚠️ AI analysis temporarily unavailable (parsing error). Analysis based on ML models."
            
            except Exception as e:
                print(f"   ❌ Unexpected Groq API error: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                if attempt < max_retries - 1:
                    time.sleep(base_delay)
                    continue
                return "⚠️ AI analysis temporarily unavailable. Analysis based on ML models."
        
        return "⚠️ AI analysis temporarily unavailable. Analysis based on ML models."
    
    def research_agent(self, topic: str, content: str) -> Dict:
        """Agent 1: Research internet for facts and cross-references"""
        print(f"🔍 [AGENT 1] Research Agent analyzing: {topic[:50]}...")
        
        # Google search for fact-checking
        search_results = google_web_search(topic, count=5)
        sources = [{'title': r.get('name', ''), 'url': r.get('url', ''), 'snippet': r.get('snippet', '')} for r in search_results]
        
        # If no sources found, provide fallback reference sources
        if not sources:
            print("   ⚠️ No Google search results - adding fallback fact-checking sources")
            sources = [
                {
                    'title': 'Snopes - Fact Checking',
                    'url': 'https://www.snopes.com',
                    'snippet': 'Independent fact-checking organization covering misinformation, rumors, and urban legends.'
                },
                {
                    'title': 'FactCheck.org',
                    'url': 'https://www.factcheck.org',
                    'snippet': 'Nonpartisan, nonprofit organization that monitors factual accuracy of political claims.'
                },
                {
                    'title': 'PolitiFact',
                    'url': 'https://www.politifact.com',
                    'snippet': 'Fact-checking website that rates the accuracy of claims by elected officials and others.'
                },
                {
                    'title': 'Reuters Fact Check',
                    'url': 'https://www.reuters.com/fact-check',
                    'snippet': 'Reuters investigates and debunks false and misleading information shared online.'
                },
                {
                    'title': 'AP Fact Check',
                    'url': 'https://apnews.com/ap-fact-check',
                    'snippet': 'Associated Press fact-checking service verifying claims made by public officials.'
                }
            ]
        
        # AI summary of research
        sources_text = '\n'.join([f"- {s['title']}: {s['snippet'][:100]}" for s in sources[:3]])
        prompt = f"""You are a fact-checking research agent. Research this topic: "{topic}"

Content preview: {content[:600]}

Found sources:
{sources_text}

Based on these sources, provide a 3-4 sentence research summary of what credible sources say about this topic."""
        
        messages = [
            {"role": "system", "content": "You are an expert research analyst focused on fact-checking and credible sources."},
            {"role": "user", "content": prompt}
        ]
        
        summary = self.call_groq_api(messages, temperature=0.3, max_tokens=500)
        
        print(f"   ✅ Research Agent: {len(sources)} sources found")
        
        return {
            "search_results": search_results,
            "sources_found": sources,
            "research_summary": summary
        }
    
    def analysis_agent(self, content: str, research_data: Dict) -> Dict:
        """Agent 2: Detailed misinformation pattern analysis"""
        print(f"🔬 [AGENT 2] Analysis Agent detecting patterns...")
        
        prompt = f"""You are a misinformation detection expert. Analyze this content for suspicious patterns:

Content: {content[:800]}

Research findings: {research_data.get('research_summary', 'No research available')}

Identify:
1. Emotional manipulation tactics
2. Logical fallacies
3. Unsupported claims
4. Sensationalism
5. Suspicious language patterns

Provide a detailed 4-5 sentence analysis."""
        
        messages = [
            {"role": "system", "content": "You are an expert in detecting misinformation patterns, propaganda, and manipulation techniques."},
            {"role": "user", "content": prompt}
        ]
        
        analysis = self.call_groq_api(messages, temperature=0.5, max_tokens=600)
        
        return {
            "detailed_analysis": analysis
        }
    
    def conclusion_agent(self, topic: str, content: str, research_data: Dict, analysis_data: Dict) -> Dict:
        """Agent 3: Form expert conclusion with verdict and recommendations"""
        print(f"✅ [AGENT 3] Conclusion Agent forming verdict...")
        
        prompt = f"""You are an expert fact-checker providing final conclusions. Based on:

Topic: {topic}
Research: {research_data.get('research_summary', 'N/A')}
Analysis: {analysis_data.get('detailed_analysis', 'N/A')}

Provide a structured conclusion with these exact sections:

**WHAT IS CORRECT:**
[List facts that are accurate]

**WHAT IS WRONG:**
[List misinformation or suspicious claims]

**WHAT THE INTERNET SAYS:**
[Summarize what credible sources say]

**MY RECOMMENDATION:**
[Your expert recommendation for readers]

**WHY THIS MATTERS:**
[Explain the significance and impact]"""
        
        messages = [
            {"role": "system", "content": "You are an expert fact-checker providing authoritative conclusions and recommendations."},
            {"role": "user", "content": prompt}
        ]
        
        conclusion = self.call_groq_api(messages, temperature=0.6, max_tokens=1200)
        
        # Extract sections
        what_right = "See full conclusion"
        what_wrong = "See full conclusion"
        internet_says = "See full conclusion"
        recommendation = "Verify with credible sources"
        why_matters = "Critical thinking is essential"
        
        try:
            if "WHAT IS CORRECT" in conclusion:
                start = conclusion.find("WHAT IS CORRECT")
                end = conclusion.find("WHAT IS WRONG")
                if end != -1:
                    what_right = conclusion[start:end].strip()
            
            if "WHAT IS WRONG" in conclusion:
                start = conclusion.find("WHAT IS WRONG")
                end = conclusion.find("WHAT THE INTERNET SAYS")
                if end != -1:
                    what_wrong = conclusion[start:end].strip()
            
            if "WHAT THE INTERNET SAYS" in conclusion:
                start = conclusion.find("WHAT THE INTERNET SAYS")
                end = conclusion.find("MY RECOMMENDATION")
                if end != -1:
                    internet_says = conclusion[start:end].strip()
            
            if "MY RECOMMENDATION" in conclusion:
                start = conclusion.find("MY RECOMMENDATION")
                end = conclusion.find("WHY THIS MATTERS")
                if end != -1:
                    recommendation = conclusion[start:end].strip()
            
            if "WHY THIS MATTERS" in conclusion:
                start = conclusion.find("WHY THIS MATTERS")
                why_matters = conclusion[start:].strip()
        except Exception as e:
            print(f"Section extraction error: {e}")
        
        return {
            "full_conclusion": conclusion,
            "what_is_right": what_right,
            "what_is_wrong": what_wrong,
            "internet_says": internet_says,
            "recommendation": recommendation,
            "why_matters": why_matters
        }

# Initialize Groq AI
groq_ai = GroqAI(GROQ_API_KEY)

# ========================================
# MAIN ANALYSIS ENDPOINT
# ========================================

@app.route('/api/v1/analyze-chunks', methods=['POST', 'OPTIONS'])
def analyze_chunks():
    """Unified analysis endpoint - combines ALL features from both servers"""
    try:
        print("\n" + "=" * 80)
        print(f"🚨 ENDPOINT HIT: {request.method} /api/v1/analyze-chunks")
        print("=" * 80)
        
        if request.method == 'OPTIONS':
            print("✅ OPTIONS request - returning CORS headers")
            response = jsonify({'status': 'ok'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
            return response
        
        print("� POST request received - extracting data...")
        data = request.json or {}
        paragraphs = data.get('paragraphs', [])
        title = data.get('title', '')
        url = data.get('url', '')
        print(f"✅ Data extracted: {len(paragraphs)} paragraphs, title='{title[:50]}...'")
        
        print("=" * 70)
        print(f"📊 LINKSCOUT ANALYSIS STARTED")
        print(f"📍 URL: {url}")
        print(f"📄 Title: {title}")
        print(f"📝 Paragraphs: {len(paragraphs)}")
        print("=" * 70)
        
        # Combine paragraphs into full content
        if paragraphs and isinstance(paragraphs[0], dict):
            content = '\n\n'.join([p.get('text', str(p)) for p in paragraphs if p])
        else:
            content = '\n\n'.join([str(p) for p in paragraphs if p])
        
        # ========================================
        # STEP 1: PRE-TRAINED MODELS (8 models)
        # ========================================
        print("\n🤖 [STEP 1/4] Running pre-trained models...")
        try:
            pretrained_result = analyze_with_pretrained_models(content)
            print(f"   ✅ Fake probability: {pretrained_result.get('fake_probability', 0)*100:.1f}%")
            print(f"   ✅ Emotion: {pretrained_result.get('emotion', 'unknown')}")
            print(f"   ✅ Categories: {', '.join(pretrained_result.get('categories', []))}")
        except Exception as e:
            print(f"   ⚠️ Pre-trained models failed: {e}")
            import traceback
            traceback.print_exc()
            pretrained_result = {
                'fake_probability': 0.5,
                'real_probability': 0.5,
                'emotion': 'unknown',
                'categories': [],
                'hate_speech': {'label': 'NOT_HATE', 'score': 0},
                'clickbait': {'is_clickbait': False, 'score': 0},
                'bias': 'neutral',
                'entities': []
            }
        
        # ========================================
        # STEP 2: GROQ AI AGENTS (3 agents)
        # ========================================
        print("\n🤖 [STEP 2/4] Running Groq AI agents...")
        try:
            print("   Starting research agent...")
            research_data = groq_ai.research_agent(title or "Article", content)
            print(f"   ✅ Research: {len(research_data.get('sources_found', []))} sources found")
        except KeyboardInterrupt:
            raise  # Re-raise keyboard interrupt to allow server shutdown
        except Exception as e:
            print(f"   ⚠️ Research agent failed: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            research_data = {'research_summary': 'Analysis unavailable', 'sources_found': [], 'search_results': []}
        
        try:
            print("   Starting analysis agent...")
            analysis_data = groq_ai.analysis_agent(content, research_data)
            print(f"   ✅ Analysis: Complete")
        except KeyboardInterrupt:
            raise  # Re-raise keyboard interrupt to allow server shutdown
        except Exception as e:
            print(f"   ⚠️ Analysis agent failed: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            analysis_data = {'detailed_analysis': 'Analysis unavailable'}
        
        try:
            print("   Starting conclusion agent...")
            conclusion_data = groq_ai.conclusion_agent(title or "Article", content, research_data, analysis_data)
            print(f"   ✅ Conclusion: Complete")
        except KeyboardInterrupt:
            raise  # Re-raise keyboard interrupt to allow server shutdown
        except Exception as e:
            print(f"   ⚠️ Conclusion agent failed: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            conclusion_data = {
                'full_conclusion': 'Analysis unavailable',
                'what_is_right': 'See conclusion',
                'what_is_wrong': 'See conclusion',
                'internet_says': 'See conclusion',
                'recommendation': 'Verify with credible sources',
                'why_matters': 'Critical thinking is essential'
            }
        
        # ========================================
        # STEP 3: REVOLUTIONARY DETECTION (8 Phases)
        # ========================================
        print("\n🔥 [STEP 3/4] Running Revolutionary Detection (8 Phases)...")
        
        # Phase 1.1 - Linguistic Fingerprint
        try:
            linguistic_result = analyze_text_fingerprint(content)
            print(f"   ✅ Phase 1.1 - Linguistic: {linguistic_result.get('fingerprint_score', 0)}/100")
        except Exception as e:
            print(f"   ⚠️ Phase 1.1 failed: {e}")
            linguistic_result = {'fingerprint_score': 50, 'emotional_language': 50, 'complexity': 50}
        
        # Phase 1.2 - Claim Verification
        try:
            claim_result = verify_text_claims(content, url)
            print(f"   ✅ Phase 1.2 - Claims: {claim_result.get('total_claims', 0)} found, {claim_result.get('false_claims', 0)} false")
        except Exception as e:
            print(f"   ⚠️ Phase 1.2 failed: {e}")
            claim_result = {'total_claims': 0, 'false_claims': 0, 'verification_score': 50}
        
        # Phase 1.3 - Source Credibility
        try:
            if url:
                source_result = analyze_text_sources(f"{url}\n{content}")
            else:
                source_result = analyze_text_sources(content)
            print(f"   ✅ Phase 1.3 - Sources: {source_result.get('average_credibility', 0):.1f}/100 credibility")
        except Exception as e:
            print(f"   ⚠️ Phase 1.3 failed: {e}")
            source_result = {'average_credibility': 50, 'sources': []}
        
        # Phase 2.1 - Entity Verification
        try:
            entity_result = verify_text_entities(content)
            print(f"   ✅ Phase 2.1 - Entities: {entity_result.get('verified_entities', 0)}/{entity_result.get('total_entities', 0)} verified")
        except Exception as e:
            print(f"   ⚠️ Phase 2.1 failed: {e}")
            entity_result = {'total_entities': 0, 'verified_entities': 0}
        
        # Phase 2.2 - Propaganda Detection
        try:
            propaganda_result = detect_text_propaganda(content)
            # ✅ FIX: Use 'technique_list' (array) instead of 'techniques' (dict)
            propaganda_result['techniques'] = propaganda_result.get('technique_list', [])
            print(f"   ✅ Phase 2.2 - Propaganda: {propaganda_result.get('propaganda_score', 0)}/100")
            if propaganda_result.get('technique_list'):
                print(f"      Techniques: {', '.join(propaganda_result['technique_list'])}")
        except Exception as e:
            print(f"   ⚠️ Phase 2.2 failed: {e}")
            propaganda_result = {'propaganda_score': 0, 'techniques': [], 'technique_list': []}
        
        # Phase 2.3 - Network Verification
        try:
            network_verification_result = verify_claims_network([])
            print(f"   ✅ Phase 2.3 - Network Verification: Complete")
        except Exception as e:
            print(f"   ⚠️ Phase 2.3 failed: {e}")
            network_verification_result = {'verification_status': 'unknown'}
        
        # Phase 3.1 - Contradiction Detection
        try:
            contradiction_result = detect_text_contradictions(content)
            print(f"   ✅ Phase 3.1 - Contradictions: {contradiction_result.get('total_contradictions', 0)} found")
        except Exception as e:
            print(f"   ⚠️ Phase 3.1 failed: {e}")
            contradiction_result = {'total_contradictions': 0}
        
        # Phase 3.2 - Network Analysis
        try:
            network_analysis_result = analyze_network_patterns(content)
            print(f"   ✅ Phase 3.2 - Network Analysis: {network_analysis_result.get('bot_score', 0):.1f}/100 bot score")
        except Exception as e:
            print(f"   ⚠️ Phase 3.2 failed: {e}")
            network_analysis_result = {'bot_score': 0}
        
        # ========================================
        # GENERATE AI EXPLANATIONS FOR 8 PHASES
        # ========================================
        print("\n🤖 Generating AI explanations for detection phases...")
        phase_explanations = {}
        
        try:
            # Prepare phase data summary for AI
            phases_summary = f"""
PHASE 1 - LINGUISTIC FINGERPRINT: Score {linguistic_result.get('fingerprint_score', 0)}/100
PHASE 2 - CLAIM VERIFICATION: {claim_result.get('false_claims', 0)} false claims out of {claim_result.get('total_claims', 0)} total
PHASE 3 - SOURCE CREDIBILITY: {source_result.get('average_credibility', 0)}/100 credibility
PHASE 4 - ENTITY VERIFICATION: {entity_result.get('verified_entities', 0)}/{entity_result.get('total_entities', 0)} verified
PHASE 5 - PROPAGANDA DETECTION: {propaganda_result.get('propaganda_score', 0)}/100 with techniques: {', '.join(propaganda_result.get('techniques', [])[:3])}
PHASE 6 - NETWORK VERIFICATION: {network_verification_result.get('verified_claims', 0)} claims verified
PHASE 7 - CONTRADICTION DETECTION: {contradiction_result.get('total_contradictions', 0)} contradictions
PHASE 8 - NETWORK PROPAGATION: Bot score {network_analysis_result.get('bot_score', 0)}/100
"""
            
            # Call Groq AI for explanations with article context
            explanation_prompt = f"""You are an AI analyst explaining article credibility analysis to everyday readers. For each detection phase below, provide your AI opinion in simple, conversational language.

ARTICLE CONTEXT:
Title: {title if 'title' in locals() else 'Not available'}
Excerpt: "{content[:400]}..."

DETECTION RESULTS:
{phases_summary}

For EACH phase, write a user-friendly explanation that includes:
1. What this phase detects (1 simple sentence)
2. What YOU (the AI) found in THIS specific article (2-3 sentences with specific insights)
3. Your opinion on whether the reader should be concerned (1 sentence)

Write naturally, like you're talking to a friend. Use "I" statements (e.g., "I noticed that...", "I found...", "In my analysis...").

Provide 8 separate explanations in this EXACT format:

**PHASE 1 - LINGUISTIC FINGERPRINT:**
[your conversational AI explanation with specific insights about THIS article]

**PHASE 2 - CLAIM VERIFICATION:**
[your conversational AI explanation with specific insights about THIS article]

**PHASE 3 - SOURCE CREDIBILITY:**
[your conversational AI explanation with specific insights about THIS article]

**PHASE 4 - ENTITY VERIFICATION:**
[your conversational AI explanation with specific insights about THIS article]

**PHASE 5 - PROPAGANDA DETECTION:**
[your conversational AI explanation with specific insights about THIS article]

**PHASE 6 - NETWORK VERIFICATION:**
[your conversational AI explanation with specific insights about THIS article]

**PHASE 7 - CONTRADICTION DETECTION:**
[your conversational AI explanation with specific insights about THIS article]

**PHASE 8 - NETWORK PROPAGATION:**
[your conversational AI explanation with specific insights about THIS article]"""
            
            messages = [
                {"role": "system", "content": "You are a friendly AI analyst helping everyday people understand article credibility. Speak conversationally, use 'I' statements to share your insights, and explain technical findings in simple terms. Be specific about what you found in THIS article."},
                {"role": "user", "content": explanation_prompt}
            ]
            
            explanations_text = groq_ai.call_groq_api(messages, temperature=0.7, max_tokens=2000)
            
            # Parse explanations
            if explanations_text and "PHASE 1" in explanations_text:
                phase_explanations['linguistic'] = explanations_text.split("**PHASE 2")[0].replace("**PHASE 1 - LINGUISTIC FINGERPRINT:**", "").strip()
                
                if "PHASE 2" in explanations_text:
                    phase_explanations['claims'] = explanations_text.split("**PHASE 2 - CLAIM VERIFICATION:**")[1].split("**PHASE 3")[0].strip() if "PHASE 3" in explanations_text else ""
                
                if "PHASE 3" in explanations_text:
                    phase_explanations['source'] = explanations_text.split("**PHASE 3 - SOURCE CREDIBILITY:**")[1].split("**PHASE 4")[0].strip() if "PHASE 4" in explanations_text else ""
                
                if "PHASE 4" in explanations_text:
                    phase_explanations['entity'] = explanations_text.split("**PHASE 4 - ENTITY VERIFICATION:**")[1].split("**PHASE 5")[0].strip() if "PHASE 5" in explanations_text else ""
                
                if "PHASE 5" in explanations_text:
                    phase_explanations['propaganda'] = explanations_text.split("**PHASE 5 - PROPAGANDA DETECTION:**")[1].split("**PHASE 6")[0].strip() if "PHASE 6" in explanations_text else ""
                
                if "PHASE 6" in explanations_text:
                    phase_explanations['network_verify'] = explanations_text.split("**PHASE 6 - NETWORK VERIFICATION:**")[1].split("**PHASE 7")[0].strip() if "PHASE 7" in explanations_text else ""
                
                if "PHASE 7" in explanations_text:
                    phase_explanations['contradiction'] = explanations_text.split("**PHASE 7 - CONTRADICTION DETECTION:**")[1].split("**PHASE 8")[0].strip() if "PHASE 8" in explanations_text else ""
                
                if "PHASE 8" in explanations_text:
                    phase_explanations['network_prop'] = explanations_text.split("**PHASE 8 - NETWORK PROPAGATION:**")[1].strip()
                
                print(f"   ✅ Generated AI explanations for {len(phase_explanations)} phases")
            else:
                print(f"   ⚠️ AI explanation parsing failed")
        
        except Exception as e:
            print(f"   ⚠️ AI explanation generation failed: {e}")
            # Provide basic fallback explanations
            phase_explanations = {
                'linguistic': 'Analyzes writing patterns to detect manipulation.',
                'claims': 'Verifies factual claims against known databases.',
                'source': 'Checks the credibility of sources mentioned.',
                'entity': 'Verifies people, places, and organizations mentioned.',
                'propaganda': 'Detects propaganda techniques used in the text.',
                'network_verify': 'Checks if claims are verified across networks.',
                'contradiction': 'Finds contradictory statements within the text.',
                'network_prop': 'Analyzes if content shows signs of artificial spreading.'
            }
        
        # Add explanations to results
        linguistic_result['ai_explanation'] = phase_explanations.get('linguistic', '')
        claim_result['ai_explanation'] = phase_explanations.get('claims', '')
        source_result['ai_explanation'] = phase_explanations.get('source', '')
        entity_result['ai_explanation'] = phase_explanations.get('entity', '')
        propaganda_result['ai_explanation'] = phase_explanations.get('propaganda', '')
        network_verification_result['ai_explanation'] = phase_explanations.get('network_verify', '')
        contradiction_result['ai_explanation'] = phase_explanations.get('contradiction', '')
        network_analysis_result['ai_explanation'] = phase_explanations.get('network_prop', '')
        
        # ========================================
        # GENERATE COMBINED OVERALL SUMMARY
        # ========================================
        print("\n🎯 Generating combined credibility summary...")
        
        # Calculate overall credibility score (0-100, lower = more credible)
        overall_score = (
            linguistic_result.get('fingerprint_score', 0) * 0.15 +  # 15%
            (claim_result.get('false_percentage', 0)) * 0.20 +      # 20%
            (100 - source_result.get('average_credibility', 50)) * 0.15 +  # 15%
            propaganda_result.get('propaganda_score', 0) * 0.25 +   # 25%
            contradiction_result.get('contradiction_score', 0) * 0.10 +  # 10%
            network_analysis_result.get('bot_score', 0) * 0.15      # 15%
        )
        
        # Determine verdict
        if overall_score < 20:
            overall_verdict = "HIGHLY CREDIBLE"
            verdict_color = "#10b981"
        elif overall_score < 35:
            overall_verdict = "MOSTLY CREDIBLE"
            verdict_color = "#3b82f6"
        elif overall_score < 50:
            overall_verdict = "QUESTIONABLE"
            verdict_color = "#f59e0b"
        elif overall_score < 70:
            overall_verdict = "LOW CREDIBILITY"
            verdict_color = "#ef4444"
        else:
            overall_verdict = "NOT CREDIBLE"
            verdict_color = "#dc2626"
        
        # Generate combined AI summary
        combined_summary_prompt = f"""You are analyzing an article for credibility. Here are the results from 8 detection systems:

**ARTICLE CONTEXT:**
Title: {title if 'title' in locals() else 'Article'}
First 300 words: "{content[:300]}..."

**OVERALL CREDIBILITY SCORE: {overall_score:.1f}/100** (Lower is better)
**VERDICT: {overall_verdict}**

**8-PHASE ANALYSIS RESULTS:**
1. **Linguistic Patterns**: {linguistic_result.get('fingerprint_score', 0)}/100 - {linguistic_result.get('verdict', 'N/A')}
2. **Claim Verification**: {claim_result.get('false_percentage', 0)}% false claims ({claim_result.get('false_claims', 0)}/{claim_result.get('total_claims', 0)})
3. **Source Credibility**: {source_result.get('average_credibility', 0)}/100 credibility
4. **Entity Verification**: {entity_result.get('verified_entities', 0)}/{entity_result.get('total_entities', 0)} entities verified
5. **Propaganda Detection**: {propaganda_result.get('propaganda_score', 0)}/100 - Found {len(propaganda_result.get('techniques', []))} techniques
6. **Network Verification**: {network_verification_result.get('verified_claims', 0)} claims verified
7. **Contradiction Detection**: {contradiction_result.get('total_contradictions', 0)} contradictions found
8. **Network Propagation**: {network_analysis_result.get('bot_score', 0):.1f}/100 bot score

Write a friendly, conversational summary (2 short paragraphs, 4-5 sentences total) that:
1. **First paragraph**: Explain what these 8 systems found in THIS specific article. Use "I" statements and be specific about actual findings.
2. **Second paragraph**: Give your overall opinion - should the reader trust this article? Why or why not? Be clear and direct.

Write like you're talking to a friend who wants to know if this article is trustworthy. Be honest, specific, and helpful."""

        combined_messages = [
            {"role": "system", "content": "You are a friendly AI analyst helping people understand if articles are credible. Speak conversationally and give clear, actionable advice."},
            {"role": "user", "content": combined_summary_prompt}
        ]
        
        try:
            combined_ai_summary = groq_ai.call_groq_api(combined_messages, temperature=0.7, max_tokens=400)
            # ✅ FIX: Remove ALL leading/trailing whitespace and normalize internal spacing
            # Remove leading spaces from each line
            lines = combined_ai_summary.split('\n')
            cleaned_lines = [line.strip() for line in lines if line.strip()]
            combined_ai_summary = '\n\n'.join(cleaned_lines)  # Join with double newline for paragraphs
            print(f"✅ Generated combined AI summary ({len(combined_ai_summary)} chars)")
        except Exception as e:
            print(f"⚠️ Failed to generate combined summary: {e}")
            combined_ai_summary = f"This article received an overall credibility score of {overall_score:.1f}/100. Based on the analysis, it appears to be {overall_verdict.lower()}."
        
        # ========================================
        # STEP 4: PER-PARAGRAPH ANALYSIS (Chunks)
        # ========================================
        print("\n📋 [STEP 4/4] Analyzing individual paragraphs...")
        
        chunks = []
        fake_count = 0
        suspicious_count = 0
        
        for i, para in enumerate(paragraphs):
            para_text = para.get('text', str(para)) if isinstance(para, dict) else str(para)
            
            # ✅ Skip very short paragraphs
            if len(para_text.strip()) < 50:
                continue
            
            # ✅ Skip navigation/highlights/metadata elements
            skip_patterns = [
                'pictured', 'shown above', 'image shows', 'photo shows',  # Image captions
                'related topics', 'more on this story', 'share this',  # Navigation
                'follow us', 'subscribe', 'newsletter',  # Social/subscribe
                'copyright', '© ', 'all rights reserved',  # Copyright
                'advertisement', 'sponsored content',  # Ads
                'read more:', 'also read:', 'see also:',  # Cross-references
                'updated:', 'published:', 'minutes ago', 'hours ago'  # Timestamps
            ]
            
            para_lower = para_text.lower()
            if any(pattern in para_lower for pattern in skip_patterns):
                print(f"   ⏭️  Skipping paragraph {i} (navigation/metadata element)")
                continue
            
            # ✅ Skip if too short after removing punctuation (likely a headline fragment)
            text_no_punct = ''.join(c for c in para_text if c.isalnum() or c.isspace())
            if len(text_no_punct.strip()) < 40:
                continue
            
            # Calculate paragraph score - START FROM SCRATCH FOR EACH PARAGRAPH
            para_score = 0
            why_flagged = []
            
            # ✅ USE ENSEMBLE FAKE NEWS DETECTION (4 models voting) for THIS paragraph
            # Much more reliable than single RoBERTa model
            try:
                para_ensemble_score = get_ml_misinformation_prediction(para_text)  # 0-100 scale
                
                # DEBUG: Print on first few paragraphs
                if i < 3:
                    print(f"   🔍 Para {i}: Ensemble fake news score = {para_ensemble_score:.1f}/100")
                
                # Use ensemble score to flag suspicious paragraphs
                # Enhanced scoring: higher points for higher fake news probability
                if para_ensemble_score > 85:  # 85%+ from ensemble = VERY HIGH RISK
                    para_score += 60  # Increased from 50
                    why_flagged.append(f"🚨 Very high fake news probability: {int(para_ensemble_score)}%")
                elif para_ensemble_score > 70:  # 70-85% = HIGH RISK
                    para_score += 50  # Increased from 40
                    why_flagged.append(f"🚨 High fake news probability: {int(para_ensemble_score)}%")
                elif para_ensemble_score > 55:  # 55-70% = MEDIUM RISK
                    para_score += 35  # Increased from 25
                    why_flagged.append(f"⚠️ Moderate fake news probability: {int(para_ensemble_score)}%")
                elif para_ensemble_score > 40:  # 40-55% = LOW-MEDIUM RISK
                    para_score += 20  # Increased from 15
                    why_flagged.append(f"⚠️ Some fake news indicators: {int(para_ensemble_score)}%")
            except Exception as e:
                if i < 3:
                    print(f"   ⚠️ Ensemble prediction error for para {i}: {e}")
                para_ensemble_score = 0
            
            # Emotion analysis for THIS paragraph - BALANCED THRESHOLDS
            try:
                para_emotion, para_emotion_score = get_emotion(para_text)
                
                # DEBUG: Print emotion on first few paragraphs
                if i < 3:
                    print(f"   🔍 Emotion: {para_emotion} ({para_emotion_score:.3f})")
                
                # ✅ BALANCED: Flag high emotion (but not too strict)
                # 95%+ = clear manipulation, 85%+ = strong emotional tone
                if para_emotion in ['anger', 'fear', 'disgust'] and para_emotion_score > 0.95:
                    para_score += 20
                    why_flagged.append(f"😡 Extreme emotional manipulation: {para_emotion} ({int(para_emotion_score * 100)}%)")
                elif para_emotion in ['anger', 'fear', 'disgust'] and para_emotion_score > 0.85:
                    para_score += 10
                    why_flagged.append(f"😡 High emotional tone: {para_emotion} ({int(para_emotion_score * 100)}%)")
            except:
                para_emotion = 'neutral'
            
            # Hate speech for THIS paragraph - BALANCED
            try:
                para_hate_prob = detect_hate_speech(para_text)
                if para_hate_prob > 0.75:  # 75%+ - clear hate speech
                    para_score += 30
                    why_flagged.append(f"🚫 Hate speech detected: {int(para_hate_prob * 100)}%")
                elif para_hate_prob > 0.60:  # 60%+ - strong indicators
                    para_score += 20
                    why_flagged.append(f"🚫 Hate speech indicators: {int(para_hate_prob * 100)}%")
                elif para_hate_prob > 0.45:  # 45%+ - mild indicators
                    para_score += 10
                    why_flagged.append(f"🚫 Potential hate speech: {int(para_hate_prob * 100)}%")
            except:
                para_hate_prob = 0
            
            # Clickbait for THIS paragraph - BALANCED
            try:
                para_clickbait_prob = detect_clickbait(para_text)
                if para_clickbait_prob > 0.75:  # 75%+ - obvious clickbait
                    para_score += 25
                    why_flagged.append(f"🎣 Clickbait detected: {int(para_clickbait_prob * 100)}%")
                elif para_clickbait_prob > 0.60:  # 60%+ - likely clickbait
                    para_score += 15
                    why_flagged.append(f"🎣 Clickbait indicators: {int(para_clickbait_prob * 100)}%")
                elif para_clickbait_prob > 0.45:  # 45%+ - possible clickbait
                    para_score += 8
                    why_flagged.append(f"🎣 Possible clickbait: {int(para_clickbait_prob * 100)}%")
                    para_score += 10
                    why_flagged.append(f"🎣 Clickbait detected: {int(para_clickbait_prob * 100)}%")
            except:
                para_clickbait_prob = 0
            
            # Document-level indicators (only if significant)
            # Linguistic patterns - only if very high
            if linguistic_result.get('fingerprint_score', 0) > 70:
                para_score += 8
                patterns = linguistic_result.get('patterns', [])
                if patterns and isinstance(patterns, list) and len(patterns) > 0:
                    why_flagged.append(f"📝 Suspicious language patterns")
            
            # Propaganda - only contribute if very high AND has techniques
            propaganda_score = propaganda_result.get('propaganda_score', 0)
            techniques = propaganda_result.get('techniques', [])
            if propaganda_score > 80 and isinstance(techniques, list) and len(techniques) > 0:
                para_score += 15
                why_flagged.append(f"📢 Propaganda techniques: {', '.join(techniques[:2])}")
            elif propaganda_score > 60:
                para_score += 8
            
            # Claims verification - only if actual false claims found
            false_claims = claim_result.get('false_claims', 0)
            if false_claims > 2:
                para_score += 15
                why_flagged.append(f"❌ Multiple false claims detected")
            elif false_claims > 0:
                para_score += 8
                why_flagged.append(f"⚠️ Unverified claims")
            
            para_score = min(para_score, 100)
            
            # ✅ STRICTER THRESHOLDS - Only flag truly suspicious paragraphs
            # Count categories with threshold (60+)
            if para_score >= 70:
                fake_count += 1
            elif para_score >= 60:
                suspicious_count += 1
            
            # Only add chunk if it's actually suspicious (score >= 60)
            if para_score >= 60:
                chunks.append({
                    'index': i,
                    'text': para_text,
                    'text_preview': para_text[:150] + '...' if len(para_text) > 150 else para_text,
                    'suspicious_score': para_score,
                    'why_flagged': ' • '.join(why_flagged) if why_flagged else None,
                    'severity': 'high' if para_score >= 70 else 'medium'
                })
        
        # ========================================
        # FINAL COUNTS
        # ========================================
        fake_count = len([c for c in chunks if c['suspicious_score'] >= 70])
        suspicious_count = len([c for c in chunks if 60 <= c['suspicious_score'] < 70])
        safe_count = len(paragraphs) - len(chunks)  # Count all non-suspicious paragraphs
        
        print(f"   ✅ Analyzed {len(paragraphs)} total paragraphs")
        print(f"   🚨 High risk (>=70): {fake_count}")
        print(f"   ⚠️  Medium risk (60-69): {suspicious_count}")
        print(f"   ✅ Low risk (<60): {safe_count}")
        print(f"   📍 Flagged {len(chunks)} suspicious paragraphs for highlighting")
        
        # ========================================
        # CALCULATE OVERALL MISINFORMATION %
        # ========================================
        print("\n📊 Calculating overall misinformation percentage...")
        
        suspicious_score = 0
        
        # ✅ NEW: ML MODEL INTEGRATION per NEXT_TASKS.md Task 17.2
        # Get ML prediction using RoBERTa (35% weight)
        ml_prediction = get_ml_misinformation_prediction(content)
        ml_contribution = ml_prediction * 0.35
        suspicious_score += ml_contribution
        print(f"   📊 ML Model contribution: {ml_contribution:.1f} points (35% weight)")
        
        # Pre-trained models weight (15% - reduced from 40% to make room for ML)
        if pretrained_result.get('fake_probability', 0) > 0.7:
            suspicious_score += 10
        elif pretrained_result.get('fake_probability', 0) > 0.5:
            suspicious_score += 6
        
        # Custom model weight (10% - reduced from 20%)
        if pretrained_result.get('custom_model_misinformation', 0) > 0.6:
            suspicious_score += 8
        elif pretrained_result.get('custom_model_misinformation', 0) > 0.4:
            suspicious_score += 4
        
        # Revolutionary detection weight (40% - unchanged)
        if linguistic_result.get('fingerprint_score', 0) > 60:
            suspicious_score += 10
        
        if claim_result.get('false_percentage', 0) > 50:
            suspicious_score += 15
        elif claim_result.get('false_claims', 0) > 0:
            suspicious_score += 8
        
        # ✅ CORRECT PROPAGANDA WEIGHT per NEXT_TASKS.md Task 17.3
        # Using multiplication as specified: 0.4 → 0.6 for high, 0.25 → 0.4 for medium
        propaganda_score = propaganda_result.get('propaganda_score', 0)
        if propaganda_score >= 70:
            suspicious_score += propaganda_score * 0.6  # Was 0.4 (60% weight)
        elif propaganda_score >= 40:
            suspicious_score += propaganda_score * 0.4  # Was 0.25 (40% weight)
        
        # ✅ NEW: SOURCE CREDIBILITY PENALTY - Credible sources reduce risk significantly
        source_credibility = source_result.get('average_credibility', 50)
        if source_credibility >= 70:  # Highly credible source (like NDTV, BBC, Reuters)
            credibility_bonus = -30  # Reduce suspicious score by 30 points
            suspicious_score += credibility_bonus
            print(f"   ✅ Credible source bonus: {credibility_bonus} points (credibility: {source_credibility}/100)")
        elif source_credibility >= 50:  # Moderately credible
            credibility_bonus = -15
            suspicious_score += credibility_bonus
            print(f"   ✅ Source credibility bonus: {credibility_bonus} points (credibility: {source_credibility}/100)")
        elif source_credibility < 30:  # Low credibility source
            credibility_penalty = 20
            suspicious_score += credibility_penalty
            print(f"   ⚠️ Low credibility source penalty: +{credibility_penalty} points (credibility: {source_credibility}/100)")
        
        # Ensure score stays in valid range (0-100)
        suspicious_score = max(0, min(suspicious_score, 100))
        
        # Determine verdict
        if suspicious_score >= 70:
            verdict = "FAKE NEWS"
        elif suspicious_score >= 40:
            verdict = "SUSPICIOUS - VERIFY"
        else:
            verdict = "APPEARS CREDIBLE"
        
        print(f"\n✅ Analysis complete!")
        print(f"   Verdict: {verdict}")
        print(f"   Misinformation: {suspicious_score}%")
        print(f"   Chunks analyzed: {len(chunks)}")
        print(f"   Fake paragraphs: {fake_count}")
        print(f"   Suspicious paragraphs: {suspicious_count}")
        print("=" * 70)
        
        # ========================================
        # SANITIZE DATA - ENSURE ARRAYS ARE ARRAYS
        # ========================================
        # Fix linguistic_fingerprint patterns
        if 'patterns' in linguistic_result and not isinstance(linguistic_result['patterns'], list):
            linguistic_result['patterns'] = []
        
        # Fix propaganda techniques
        if 'techniques' in propaganda_result and not isinstance(propaganda_result['techniques'], list):
            propaganda_result['techniques'] = []
        
        # Fix pretrained named_entities
        if 'named_entities' in pretrained_result and not isinstance(pretrained_result['named_entities'], list):
            pretrained_result['named_entities'] = []
        
        # Fix categories/labels
        if 'categories' in pretrained_result and not isinstance(pretrained_result['categories'], list):
            pretrained_result['categories'] = []
        if 'labels' in pretrained_result and not isinstance(pretrained_result['labels'], list):
            pretrained_result['labels'] = []
        
        # ========================================
        # 🎯 INTELLIGENT FALLBACK FOR GROQ API FAILURES
        # ========================================
        # If Groq failed (rate limit), generate analysis from ML models
        groq_failed = (conclusion_data.get('what_is_right') == 'See conclusion' or 
                      'rate limit' in str(conclusion_data.get('what_is_right', '')).lower())
        
        if groq_failed:
            print("⚠️ Groq API failed - generating fallback analysis from ML models...")
            
            # Generate What's Correct from ML analysis
            fake_prob = pretrained_result.get('fake_probability', 0) * 100
            if fake_prob < 30:
                what_is_right = f"""✅ **Content appears largely credible:**
• {len(pretrained_result.get('named_entities', []))} entities verified
• Source credibility: {source_result.get('average_credibility', 0):.0f}/100 (RELIABLE)
• Propaganda score: {propaganda_result.get('propaganda_score', 0)}/100
• Emotional tone: {pretrained_result.get('emotion', 'neutral').upper()}
• ML models confidence: {100 - fake_prob:.1f}% real

The article cites {len(pretrained_result.get('named_entities', []))} verifiable entities and comes from a credible source ({source_result.get('verdict', 'unknown')})."""
            else:
                what_is_right = f"""⚠️ **Limited credible information found:**
• Source credibility: {source_result.get('average_credibility', 0):.0f}/100
• {len(pretrained_result.get('named_entities', []))} entities identified
• Factual claims appear limited"""
            
            # Generate What's Wrong
            if fake_prob > 40:
                what_is_wrong = f"""❌ **Potential misinformation detected:**
• ML models flagged as {fake_prob:.1f}% suspicious
• {suspicious_count} out of {len(paragraphs)} paragraphs need verification
• Propaganda techniques: {', '.join(propaganda_result.get('techniques', [])[:3]) if propaganda_result.get('techniques') else 'None detected'}
• Emotional manipulation detected: {pretrained_result.get('emotion', 'neutral')}"""
            elif propaganda_result.get('propaganda_score', 0) > 50:
                what_is_wrong = f"""⚠️ **Some concerns identified:**
• Propaganda score: {propaganda_result.get('propaganda_score', 0)}/100
• Techniques used: {', '.join(propaganda_result.get('techniques', [])[:3])}
• {suspicious_count} paragraphs flagged for review"""
            else:
                what_is_wrong = "✅ No significant misinformation patterns detected by ML analysis."
            
            # Generate Internet Says (from research if available)
            if research_data.get('sources_found'):
                sources_count = len(research_data['sources_found'])
                internet_says = f"""🌐 **Cross-reference with {sources_count} sources:**
{chr(10).join(['• ' + s.get('title', 'Unknown')[:80] for s in research_data['sources_found'][:3]])}

These sources provide additional context for verification."""
            else:
                internet_says = "🌐 Manual verification recommended with trusted news sources."
            
            # Generate Recommendation
            if fake_prob < 30 and propaganda_result.get('propaganda_score', 0) < 40:
                recommendation = f"""💡 **RECOMMENDATION: Appears credible but verify key claims**
• The article shows {100 - fake_prob:.0f}% credibility based on 8 ML models
• Source is reliable ({source_result.get('average_credibility', 0):.0f}/100 credibility)
• Cross-check specific claims with multiple sources
• Look for updates on this developing story"""
            else:
                recommendation = f"""⚠️ **RECOMMENDATION: Verify before sharing**
• {fake_prob:.1f}% suspicious content detected
• Check claims against multiple trusted sources
• Look for official statements or primary sources
• Be cautious of emotional manipulation"""
            
            # Generate Why Matters
            categories = pretrained_result.get('categories', ['News'])
            why_matters = f"""⚠️ **WHY THIS MATTERS:**
This {', '.join(categories[:2])} story affects public understanding. In an era of rapid information spread, distinguishing fact from fiction is crucial. Always verify important claims with multiple credible sources before forming conclusions or sharing."""
            
            # Update conclusion data
            conclusion_data['what_is_right'] = what_is_right
            conclusion_data['what_is_wrong'] = what_is_wrong
            conclusion_data['internet_says'] = internet_says
            conclusion_data['recommendation'] = recommendation
            conclusion_data['why_matters'] = why_matters
            
            print("✅ Fallback analysis generated from ML models")
        
        # ========================================
        # STEP 5: IMAGE ANALYSIS (NEW!)
        # ========================================
        print("\n🖼️ [STEP 5/5] Analyzing images...")
        image_analysis_result = {'total_images': 0, 'analyzed_images': 0, 'ai_generated_count': 0, 'summary': 'No images analyzed'}
        
        try:
            html_content = data.get('html', '')
            if html_content and url:
                print(f"   📄 HTML content received: {len(html_content)} chars")
                image_analysis_result = analyze_webpage_images(html_content, url)
                print(f"   ✅ Image Analysis: {image_analysis_result.get('analyzed_images', 0)} images analyzed")
                if image_analysis_result.get('ai_generated_count', 0) > 0:
                    print(f"   ⚠️  AI-Generated: {image_analysis_result['ai_generated_count']} suspicious images found")
            else:
                print(f"   ⚠️  Image analysis skipped (no HTML content)")
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"   ⚠️  Image analysis failed: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        
        # ========================================
        # BUILD COMPREHENSIVE RESPONSE
        # ========================================
        response_data = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'url': url,
            'title': title,
            'verdict': verdict,
            'misinformation_percentage': round(suspicious_score, 1),  # ✅ FIX: Round to 1 decimal
            'credibility_percentage': round(100 - suspicious_score, 1),
            
            # Overall summary
            'overall': {
                'verdict': verdict,
                'suspicious_score': round(suspicious_score, 1),  # ✅ FIX: Round to 1 decimal
                'total_paragraphs': len(paragraphs),
                'fake_paragraphs': fake_count,
                'suspicious_paragraphs': suspicious_count,
                'safe_paragraphs': len(paragraphs) - fake_count - suspicious_count,
                'credible_paragraphs': len(paragraphs) - fake_count - suspicious_count,
                'credibility_score': round(100 - suspicious_score, 1)  # ✅ FIX: Round to 1 decimal
            },
            
            # Chunks (per-paragraph analysis)
            'chunks': chunks,
            
            # Pre-trained models (8 models)
            'pretrained_models': pretrained_result,
            
            # Groq AI results
            'research': research_data.get('research_summary', ''),
            'research_summary': research_data.get('research_summary', ''),
            'research_sources': research_data.get('sources_found', []),
            'sources_found': research_data.get('sources_found', []),
            
            'analysis': analysis_data.get('detailed_analysis', ''),
            'detailed_analysis': analysis_data.get('detailed_analysis', ''),
            
            'conclusion': conclusion_data.get('full_conclusion', ''),
            'full_conclusion': conclusion_data.get('full_conclusion', ''),
            'what_is_right': conclusion_data.get('what_is_right', 'See conclusion'),
            'what_is_wrong': conclusion_data.get('what_is_wrong', 'See conclusion'),
            'internet_says': conclusion_data.get('internet_says', 'See conclusion'),
            'recommendation': conclusion_data.get('recommendation', 'Verify with credible sources'),
            'why_matters': conclusion_data.get('why_matters', 'Critical thinking is essential'),
            
            # Revolutionary Detection (8 phases)
            'linguistic_fingerprint': linguistic_result,
            'claim_verification': claim_result,
            'source_credibility': source_result,
            'entity_verification': entity_result,
            'propaganda_analysis': propaganda_result,  # ✅ techniques is array
            'verification_network': network_verification_result,
            'contradiction_detection': contradiction_result,  # ✅ Fixed: was 'contradiction_analysis'
            'contradiction_analysis': contradiction_result,  # Keep for backward compatibility
            'network_analysis': network_analysis_result,
            
            # Combined Summary (NEW!)
            'combined_analysis': {
                'overall_score': round(overall_score, 1),
                'verdict': overall_verdict,
                'verdict_color': verdict_color,
                'ai_summary': combined_ai_summary
            },
            
            # Image Analysis (NEW!)
            'image_analysis': image_analysis_result
        }
        
        response = jsonify(response_data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        print("✅ Response prepared successfully - returning to client")
        return response
        
    except Exception as e:
        print("\n" + "=" * 80)
        print("❌❌❌ CRITICAL ERROR IN ANALYZE-CHUNKS ❌❌❌")
        print("=" * 80)
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\n📋 FULL TRACEBACK:")
        import traceback
        traceback.print_exc()
        print("=" * 80)
        
        error_response = jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__,
            'traceback': traceback.format_exc()
        })
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500

# Legacy endpoints for backward compatibility
@app.route('/analyze', methods=['POST', 'OPTIONS'])
@app.route('/analyze-url', methods=['POST', 'OPTIONS'])
@app.route('/api/v1/analyze', methods=['POST', 'OPTIONS'])
def analyze_legacy():
    """Legacy endpoint - redirects to main endpoint"""
    print(f"📍 Legacy endpoint called: {request.path} -> redirecting to analyze-chunks")
    return analyze_chunks()

@app.route('/quick-test', methods=['POST'])
def quick_test():
    """Quick test endpoint for accuracy testing - lightweight version"""
    try:
        data = request.json or {}
        content = data.get('content', '')
        
        if not content:
            paragraphs = data.get('paragraphs', [])
            if paragraphs and isinstance(paragraphs[0], dict):
                content = '\n\n'.join([p.get('text', str(p)) for p in paragraphs if p])
            else:
                content = '\n\n'.join([str(p) for p in paragraphs if p])
        
        if not content or len(content.strip()) < 10:
            return jsonify({
                'success': False,
                'error': 'Content too short or empty',
                'risk_score': 0
            }), 400
        
        print(f"\n🧪 Quick Test - Content length: {len(content)} chars")
        
        # Run only essential models for testing
        suspicious_score = 0
        ml_score_raw = 0
        
        # 1. RoBERTa ML Model - PRIMARY (40% weight = 40 points max, reduced from 50%)
        try:
            text_sample = content[:512]
            inputs = roberta_tokenizer(text_sample, return_tensors="pt", truncation=True, padding=True, max_length=512)
            input_ids = inputs['input_ids'].to(device)
            attention_mask = inputs['attention_mask'].to(device)
            
            with torch.no_grad():
                outputs = roberta_model(input_ids=input_ids, attention_mask=attention_mask)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
                # ✅ FIX: Corrected label - [1]=FAKE, [0]=REAL
                fake_prob = float(probs[0][1].cpu().item())  # Index 1 = FAKE news
            
            ml_score_raw = fake_prob
            
            # Convert to 0-40 scale (40% weight, reduced from 50%)
            ml_contribution = fake_prob * 40
            
            # BOOST: If ML is very confident (>95%), add bonus
            if fake_prob > 0.95:
                ml_contribution += 10  # Increased bonus for high confidence
                print(f"   🤖 ML Model (RoBERTa): {fake_prob*100:.1f}% fake → {ml_contribution:.1f} points (40% weight + HIGH CONFIDENCE BOOST)")
            else:
                print(f"   🤖 ML Model (RoBERTa): {fake_prob*100:.1f}% fake → {ml_contribution:.1f} points (40% weight)")
            
            suspicious_score += ml_contribution
        except Exception as e:
            print(f"   ⚠️ ML Model error: {e}")
        
        # 2. False Claims Database + Keyword Detection (45% weight = 45 points max, increased from 35%)
        try:
            from known_false_claims import KNOWN_FALSE_CLAIMS
            content_lower = content.lower()
            matches = 0
            matched_claims = []
            
            # Check against database claims
            for claim in KNOWN_FALSE_CLAIMS.keys():
                if claim.lower() in content_lower:
                    matches += 1
                    matched_claims.append(claim[:50])
            
            # Enhanced keyword detection for common misinformation topics
            misinformation_keywords = {
                'covid_conspiracy': ['microchip', 'bill gates vaccine', 'vaccine tracking', 'vaccine surveillance', 
                                    'vaccine magnetism', 'vaccine 5g', 'mrna change dna', 'vaccine gene therapy',
                                    'vaccine emergency use', 'vaccine experimental', 'vaccine untested',
                                    'natural immunity better', 'natural immunity is'],
                'election_fraud': ['dominion', 'voting machine', 'voting machines', 'machine hack', 'switch votes',
                                  'bamboo ballot', 'sharpie', 'dead people voted', 'dead voter', 
                                  'ballot dump', 'election stolen', 'election rigged', 'election theft',
                                  'voter fraud', 'fraudulent vote', 'fake ballot', 'hacked by venezuela',
                                  'invalidate ballot', 'biggest election theft'],
                'health_conspiracy': ['chemtrail', 'fluoride mind control', 'fluoride lower iq', 
                                     'big pharma suppress', 'vitamin c cure', 'alkaline water prevent',
                                     'natural immunity better', 'cancer cure suppressed', 'cure suppressed',
                                     'sugar feeds cancer'],
                'tech_conspiracy': ['5g coronavirus', '5g cause', '5g radiation', '5g depopulation', '5g towers cause',
                                   'phone radiation brain', 'wifi cancer', 'microwave oven cancer', 
                                   '5g to depopulate', 'weakens your immune system'],
                'climate_denial': ['climate hoax', 'ice age coming', 'sun cause warming', 'climate scientist disagree',
                                  'antarctica ice growing'],
                'manipulation': ['poison our children', 'government planes spray', 'nasa documents prove',
                                'geoengineering', 'they are installing', 'depopulate the planet']
            }
            
            keyword_score = 0
            keyword_matches = []
            for category, keywords in misinformation_keywords.items():
                for keyword in keywords:
                    if keyword in content_lower:
                        keyword_score += 5  # Increased from 4 to 5
                        keyword_matches.append(f"{keyword[:30]}")
            
            # Combine database matches and keyword matches
            # Database: up to 20 points, Keywords: up to 30 points (increased from 20)
            total_score = min(matches * 12, 20) + min(keyword_score, 30)
            total_score = min(total_score, 45)  # Max 45 points (increased from 35)
            
            suspicious_score += total_score
            
            if matches > 0 or keyword_score > 0:
                total_matches = matches + len(keyword_matches)
                print(f"   📚 Database + Keywords: {matches} claims + {len(keyword_matches)} keywords → {total_score:.1f} points (45% weight)")
                if matched_claims or keyword_matches:
                    examples = (matched_claims + keyword_matches)[:3]
                    print(f"      Examples: {', '.join(examples)}")
            else:
                print(f"   📚 Database + Keywords: No matches found → 0 points")
        except Exception as e:
            print(f"   ⚠️ Database error: {e}")
            import traceback
            traceback.print_exc()
        
        # 3. Linguistic Patterns (15% weight = 15 points max)
        suspicious_words = {
            'conspiracy': ['exposed', 'shocking', 'they dont want you to know', 'wake up', 'sheeple',
                          'hidden truth', 'conspiracy', 'cover up', 'coverup', 'mainstream media lies', 
                          'msm lies', 'fake news media'],
            'manipulation': ['big pharma', 'globalist', 'deep state', 'new world order', 'illuminati',
                           'shadow government', 'puppet master', 'controlled opposition'],
            'urgency': ['must share', 'share before deleted', 'censored', 'banned', 'silenced',
                       'they are hiding', 'breaking', 'urgent', 'alert'],
            'distrust': ['dont trust', 'never trust', 'lie to you', 'lying to us', 'propaganda',
                        'brainwash', 'indoctrination', 'mind control', 'sheep'],
            'absolutism': ['never', 'always', 'everyone knows', 'nobody believes', 'all scientists',
                          'every doctor', '100% proof', 'undeniable', 'fact'],
            'fearmongering': ['deadly', 'killing', 'poison', 'toxic', 'dangerous truth',
                             'devastating', 'apocalypse', 'extinction', 'genocide']
        }
        
        word_count = 0
        categories_found = set()
        for category, words in suspicious_words.items():
            for word in words:
                if word in content_lower:
                    word_count += 1
                    categories_found.add(category)
        
        # Scoring based on number of suspicious phrases
        if word_count >= 5:
            ling_contribution = 15
        elif word_count >= 3:
            ling_contribution = 10
        elif word_count >= 2:
            ling_contribution = 6
        elif word_count == 1:
            ling_contribution = 3
        else:
            ling_contribution = 0
        
        suspicious_score += ling_contribution
        
        if categories_found:
            print(f"   🔤 Linguistic: {word_count} phrases in {len(categories_found)} categories → {ling_contribution:.1f} points (15% weight)")
        else:
            print(f"   🔤 Linguistic: No suspicious patterns → 0 points")
        
        suspicious_score = min(suspicious_score, 100)
        
        # Determine verdict
        if suspicious_score >= 70:
            verdict = "FAKE NEWS"
        elif suspicious_score >= 40:
            verdict = "SUSPICIOUS - VERIFY"
        else:
            verdict = "APPEARS CREDIBLE"
        
        print(f"   Final Score: {suspicious_score:.1f}% - {verdict}\n")
        
        return jsonify({
            'success': True,
            'risk_score': round(suspicious_score, 1),  # ✅ FIX: Round to 1 decimal
            'verdict': verdict,
            'misinformation_percentage': round(suspicious_score, 1),
            'credibility_percentage': round(100 - suspicious_score, 1)
        })
        
    except Exception as e:
        print(f"❌ Quick test error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'risk_score': 0
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    rl_agent = get_rl_agent()
    rl_stats = rl_agent.get_statistics() if rl_agent else {'status': 'not initialized'}
    
    return jsonify({
        'status': 'healthy',
        'name': 'LinkScout',
        'tagline': 'Smart Analysis. Simple Answers.',
        'features': {
            'groq_ai': 'active',
            'pretrained_models': 8,
            'custom_model': not _custom_model_disabled,
            'revolutionary_detection': 8,
            'reinforcement_learning': rl_stats
        },
        'device': device,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/feedback', methods=['POST'])
def submit_feedback():
    """
    Accept user feedback for reinforcement learning
    
    Expected JSON:
    {
        "analysis_id": "...",  # Optional: ID of original analysis
        "analysis_data": {...},  # Original analysis result
        "feedback": {
            "feedback_type": "correct" | "incorrect" | "partially_correct" | "too_aggressive" | "too_lenient",
            "actual_percentage": 75,  # Optional: User's assessment
            "comments": "..."  # Optional: Additional feedback
        }
    }
    """
    try:
        data = request.json or {}
        analysis_data = data.get('analysis_data', {})
        user_feedback = data.get('feedback', {})
        
        print(f"📝 [RL] Received feedback: {user_feedback.get('feedback_type', 'unknown')}")
        
        # Get RL agent
        rl_agent = get_rl_agent()
        
        if rl_agent is None:
            return jsonify({
                'success': False,
                'error': 'RL agent not initialized'
            }), 503
        
        # Process feedback
        rl_agent.process_feedback(analysis_data, user_feedback)
        
        # Get updated statistics
        stats = rl_agent.get_statistics()
        
        return jsonify({
            'success': True,
            'message': 'Feedback processed successfully',
            'rl_statistics': stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ [RL] Feedback error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/rl-suggestion', methods=['POST'])
def get_rl_suggestion():
    """
    Get RL agent's confidence adjustment suggestion
    
    Expected JSON:
    {
        "analysis_data": {...}  # Analysis result to evaluate
    }
    """
    try:
        data = request.json or {}
        analysis_data = data.get('analysis_data', {})
        
        # Get RL agent
        rl_agent = get_rl_agent()
        
        if rl_agent is None:
            return jsonify({
                'success': False,
                'error': 'RL agent not initialized'
            }), 503
        
        # Get suggestion
        suggestion = rl_agent.suggest_confidence_adjustment(analysis_data)
        
        return jsonify({
            'success': True,
            'suggestion': suggestion,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ [RL] Suggestion error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/rl-stats', methods=['GET'])
def get_rl_statistics():
    """Get current RL agent statistics"""
    try:
        rl_agent = get_rl_agent()
        
        if rl_agent is None:
            return jsonify({
                'success': False,
                'error': 'RL agent not initialized'
            }), 503
        
        stats = rl_agent.get_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ [RL] Stats error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/download-extension', methods=['GET'])
def download_extension():
    """
    Serve the browser extension as a downloadable ZIP file
    """
    try:
        import zipfile
        import tempfile
        
        extension_dir = os.path.join(os.path.dirname(__file__), 'extension')
        
        if not os.path.exists(extension_dir):
            return jsonify({
                'success': False,
                'error': 'Extension directory not found'
            }), 404
        
        # Create a temporary ZIP file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            zip_path = tmp_file.name
        
        # Create ZIP archive
        print(f"📦 Creating extension ZIP from {extension_dir}...")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through the extension directory
            for root, dirs, files in os.walk(extension_dir):
                # Skip __pycache__ and other unnecessary directories
                dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules']]
                
                for file in files:
                    # Skip unnecessary files
                    if file.endswith(('.pyc', '.pyo', '.DS_Store')):
                        continue
                    
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(extension_dir))
                    zipf.write(file_path, arcname)
                    print(f"   ✅ Added: {arcname}")
        
        print(f"✅ Extension ZIP created successfully")
        
        # Read the ZIP file
        with open(zip_path, 'rb') as f:
            zip_data = f.read()
        
        # Clean up temp file
        os.unlink(zip_path)
        
        # Return ZIP file
        from flask import send_file
        import io
        
        return send_file(
            io.BytesIO(zip_data),
            mimetype='application/zip',
            as_attachment=True,
            download_name='LinkScout-Extension.zip'
        )
        
    except Exception as e:
        print(f"❌ Extension download error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ========================================
# GLOBAL ERROR HANDLERS
# ========================================

@app.errorhandler(Exception)
def handle_exception(e):
    """Catch all unhandled exceptions"""
    print(f"\n{'='*70}")
    print(f"❌ UNHANDLED EXCEPTION: {type(e).__name__}")
    print(f"Message: {str(e)}")
    print(f"{'='*70}")
    import traceback
    traceback.print_exc()
    print(f"{'='*70}\n")
    
    return jsonify({
        'success': False,
        'error': str(e),
        'type': type(e).__name__,
        'traceback': traceback.format_exc()
    }), 500


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    print(f"❌ Internal Server Error: {e}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("=" * 70)
    print(" " * 20 + "LINKSCOUT SERVER V2")
    print(" " * 15 + "Smart Analysis. Simple Answers.")
    print("=" * 70)
    print()
    print("  🔥 COMPLETE FEATURE SET:")
    print("    ✅ Groq AI Agentic System (4 Agents)")
    print("    ✅ Pre-trained Models (8 Models)")
    print("    ✅ Custom Trained Model")
    print("    ✅ Revolutionary Detection (8 Phases)")
    print("    ✅ Category/Label Detection")
    print("    ✅ Google Search Integration")
    print("    ✅ Reference Links & Sources")
    print("    ✅ Complete Analysis Report:")
    print("       • What's Right")
    print("       • What's Wrong")
    print("       • What Internet Says")
    print("       • Recommendations")
    print("       • Why It Matters")
    print("=" * 70)
    print(f"  Server: http://localhost:5000")
    print(f"  Device: {device}")
    print("=" * 70)
    print()
    
    # Initialize RL agent
    try:
        rl_agent = initialize_rl_agent()
        if rl_agent:
            stats = rl_agent.get_statistics()
            print(f"  RL Agent: READY (Episodes: {stats.get('total_episodes', 0)})")
    except Exception as e:
        print(f"  RL Agent: Not available ({e})")
    
    print("\n  Server starting...\n")
    
    try:
        import os
        port = int(os.environ.get('PORT', 5000))
        print(f"  🌐 Port: {port}")
        app.run(host='0.0.0.0', port=port, debug=False, threaded=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user (Ctrl+C)")
        print("✅ Shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ FATAL SERVER ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("\n💡 Server crashed. Please restart.")
        sys.exit(1)

