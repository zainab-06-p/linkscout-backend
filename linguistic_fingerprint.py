"""
🔍 LINGUISTIC PATTERN FINGERPRINTING MODULE
Detects misinformation by analyzing HOW text is written, not just WHAT it says

Detects 5 manipulation patterns:
1. Emotional Manipulation - Excessive emotions, urgency, fear
2. Certainty Abuse - False certainty on complex topics
3. Source Evasion - Vague sources ("experts say", "studies show")
4. Conspiracy Markers - Conspiracy language patterns
5. Statistical Manipulation - Numbers without context

Author: AI Misinformation Detector
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class FingerprintResult:
    """Result of linguistic fingerprinting analysis"""
    fingerprint_score: float  # 0-100, higher = more suspicious
    emotional_manipulation: float
    certainty_abuse: float
    source_evasion: float
    conspiracy_markers: float
    statistical_manipulation: float
    examples: Dict[str, List[str]]
    verdict: str  # NORMAL, SUSPICIOUS, HIGHLY_SUSPICIOUS


class LinguisticFingerprint:
    """
    Analyzes text for linguistic patterns common in misinformation
    """
    
    # Pattern 1: Emotional Manipulation Keywords
    EMOTIONAL_KEYWORDS = {
        'high_intensity': [
            'SHOCKING', 'BREAKING', 'URGENT', 'CRISIS', 'DISASTER', 
            'CATASTROPHE', 'TERRIFYING', 'HORRIFYING', 'DEVASTATING',
            'EXPLOSIVE', 'BOMBSHELL', 'SCANDAL'
        ],
        'fear_words': [
            'danger', 'threat', 'deadly', 'fatal', 'toxic', 'poison',
            'kill', 'death', 'dying', 'harmful', 'dangerous', 'risk'
        ],
        'urgency_words': [
            'now', 'immediately', 'urgent', 'hurry', 'quick', 'fast',
            'before it\'s too late', 'act now', 'limited time', 'emergency'
        ],
        'outrage_words': [
            'outrageous', 'unbelievable', 'insane', 'crazy', 'ridiculous',
            'absurd', 'shocking', 'disgusting', 'appalling'
        ]
    }
    
    # Pattern 2: Certainty Abuse (when nuance is expected)
    CERTAINTY_MARKERS = [
        'absolutely', 'definitely', 'certainly', '100%', 'proven',
        'guaranteed', 'undeniable', 'indisputable', 'fact',
        'without a doubt', 'no question', 'obviously', 'clearly'
    ]
    
    # Pattern 3: Source Evasion
    SOURCE_EVASION_PATTERNS = [
        r'studies show',
        r'research shows',
        r'experts say',
        r'scientists claim',
        r'doctors warn',
        r'sources say',
        r'they say',
        r'people are saying',
        r'many believe',
        r'it is known',
        r'some say'
    ]
    
    # Pattern 4: Conspiracy Markers
    CONSPIRACY_PHRASES = [
        'they don\'t want you to know',
        'mainstream media won\'t tell you',
        'wake up',
        'open your eyes',
        'do your own research',
        'follow the money',
        'big pharma',
        'big tech',
        'the elite',
        'the establishment',
        'cover-up',
        'hidden truth',
        'secret agenda',
        'what they\'re hiding'
    ]
    
    # Pattern 5: Statistical Red Flags
    STAT_PATTERNS = [
        r'\d+%',  # Percentages
        r'\d+\s*times',  # "10 times more likely"
        r'\d+x',  # "5x higher"
        r'increased by \d+',
        r'decreased by \d+'
    ]
    
    def __init__(self):
        """Initialize the fingerprint analyzer"""
        print("🔍 [FINGERPRINT] Linguistic Pattern Analyzer initialized")
    
    def analyze(self, text: str) -> FingerprintResult:
        """
        Analyze text for linguistic manipulation patterns
        
        Args:
            text: Text to analyze
            
        Returns:
            FingerprintResult with scores and examples
        """
        if not text or len(text) < 50:
            return self._create_empty_result()
        
        # Analyze each pattern
        emotional_score, emotional_examples = self._detect_emotional_manipulation(text)
        certainty_score, certainty_examples = self._detect_certainty_abuse(text)
        source_score, source_examples = self._detect_source_evasion(text)
        conspiracy_score, conspiracy_examples = self._detect_conspiracy_markers(text)
        stat_score, stat_examples = self._detect_statistical_manipulation(text)
        
        # Calculate overall fingerprint score (weighted average)
        fingerprint_score = (
            emotional_score * 0.25 +
            certainty_score * 0.20 +
            source_score * 0.20 +
            conspiracy_score * 0.25 +
            stat_score * 0.10
        )
        
        # Determine verdict
        if fingerprint_score >= 70:
            verdict = "HIGHLY_SUSPICIOUS"
        elif fingerprint_score >= 50:
            verdict = "SUSPICIOUS"
        else:
            verdict = "NORMAL"
        
        print(f"🔍 [FINGERPRINT] Score: {fingerprint_score:.1f} ({verdict})")
        
        return FingerprintResult(
            fingerprint_score=round(fingerprint_score, 2),
            emotional_manipulation=round(emotional_score, 2),
            certainty_abuse=round(certainty_score, 2),
            source_evasion=round(source_score, 2),
            conspiracy_markers=round(conspiracy_score, 2),
            statistical_manipulation=round(stat_score, 2),
            examples={
                'emotional': emotional_examples[:5],
                'certainty': certainty_examples[:5],
                'source_evasion': source_examples[:5],
                'conspiracy': conspiracy_examples[:5],
                'statistical': stat_examples[:5]
            },
            verdict=verdict
        )
    
    def _detect_emotional_manipulation(self, text: str) -> Tuple[float, List[str]]:
        """Detect emotional manipulation tactics"""
        examples = []
        score = 0
        
        # Count exclamation marks
        exclamation_count = text.count('!')
        if exclamation_count > 5:
            score += min(30, exclamation_count * 2)
            examples.append(f"Excessive exclamation marks ({exclamation_count})")
        
        # Count all caps words
        words = text.split()
        caps_words = [w for w in words if len(w) > 3 and w.isupper()]
        if len(caps_words) > 3:
            score += min(30, len(caps_words) * 5)
            examples.extend([f"ALL CAPS: {w}" for w in caps_words[:3]])
        
        # Check for emotional keywords
        text_lower = text.lower()
        for category, keywords in self.EMOTIONAL_KEYWORDS.items():
            found = [kw for kw in keywords if kw.lower() in text_lower]
            if found:
                score += min(20, len(found) * 4)
                examples.extend([f"{category}: {kw}" for kw in found[:2]])
        
        return min(100, score), examples
    
    def _detect_certainty_abuse(self, text: str) -> Tuple[float, List[str]]:
        """Detect inappropriate certainty on complex topics"""
        examples = []
        score = 0
        
        text_lower = text.lower()
        
        for marker in self.CERTAINTY_MARKERS:
            if marker.lower() in text_lower:
                score += 8
                # Find the sentence containing this marker
                sentences = text.split('.')
                for sent in sentences:
                    if marker.lower() in sent.lower():
                        examples.append(f"Certainty marker: '{marker}' in '{sent.strip()[:100]}...'")
                        break
        
        return min(100, score), examples
    
    def _detect_source_evasion(self, text: str) -> Tuple[float, List[str]]:
        """Detect vague source references"""
        examples = []
        score = 0
        
        text_lower = text.lower()
        
        for pattern in self.SOURCE_EVASION_PATTERNS:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                score += 15
                # Get context around the match
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].strip()
                examples.append(f"Vague source: '{context}'")
        
        return min(100, score), examples
    
    def _detect_conspiracy_markers(self, text: str) -> Tuple[float, List[str]]:
        """Detect conspiracy theory language"""
        examples = []
        score = 0
        
        text_lower = text.lower()
        
        for phrase in self.CONSPIRACY_PHRASES:
            if phrase.lower() in text_lower:
                score += 20
                examples.append(f"Conspiracy phrase: '{phrase}'")
        
        return min(100, score), examples
    
    def _detect_statistical_manipulation(self, text: str) -> Tuple[float, List[str]]:
        """Detect suspicious use of statistics"""
        examples = []
        score = 0
        
        # Find all statistics
        stats = []
        for pattern in self.STAT_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            stats.extend([m.group() for m in matches])
        
        if len(stats) > 5:
            score += 20
            examples.append(f"High number of statistics ({len(stats)}) without sources")
        
        # Check if statistics appear without source citations
        # Look for patterns like "X% of people" without "according to [source]"
        percentage_pattern = r'(\d+)%\s+(?:of|are|were|have|had)'
        percentage_matches = re.finditer(percentage_pattern, text, re.IGNORECASE)
        
        for match in percentage_matches:
            # Check if there's a source citation nearby
            context_start = max(0, match.start() - 100)
            context_end = min(len(text), match.end() + 100)
            context = text[context_start:context_end].lower()
            
            has_source = any(word in context for word in ['according to', 'study', 'research', 'survey', 'report'])
            
            if not has_source:
                score += 15
                examples.append(f"Unsourced statistic: '{match.group()}'")
        
        return min(100, score), examples
    
    def _create_empty_result(self) -> FingerprintResult:
        """Create empty result for short/invalid text"""
        return FingerprintResult(
            fingerprint_score=0,
            emotional_manipulation=0,
            certainty_abuse=0,
            source_evasion=0,
            conspiracy_markers=0,
            statistical_manipulation=0,
            examples={},
            verdict="INSUFFICIENT_TEXT"
        )


# Singleton instance
_fingerprint_analyzer = None


def get_fingerprint_analyzer() -> LinguisticFingerprint:
    """Get or create the fingerprint analyzer singleton"""
    global _fingerprint_analyzer
    if _fingerprint_analyzer is None:
        _fingerprint_analyzer = LinguisticFingerprint()
    return _fingerprint_analyzer


def analyze_text_fingerprint(text: str) -> Dict:
    """
    Convenience function to analyze text fingerprint
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary with fingerprint analysis results
    """
    analyzer = get_fingerprint_analyzer()
    result = analyzer.analyze(text)
    
    return {
        'fingerprint_score': result.fingerprint_score,
        'verdict': result.verdict,
        'patterns': {
            'emotional_manipulation': result.emotional_manipulation,
            'certainty_abuse': result.certainty_abuse,
            'source_evasion': result.source_evasion,
            'conspiracy_markers': result.conspiracy_markers,
            'statistical_manipulation': result.statistical_manipulation
        },
        'examples': result.examples
    }


# Test function
if __name__ == "__main__":
    # Test with fake news example
    test_text = """
    SHOCKING! Scientists WARN: This DEADLY new virus is 100% PROVEN to cause harm! 
    Experts say that studies show the vaccine is absolutely dangerous. 
    Big Pharma doesn't want you to know the truth! Wake up people! 
    95% of people who took it had side effects!!! Do your own research!!!
    """
    
    analyzer = LinguisticFingerprint()
    result = analyzer.analyze(test_text)
    
    print("\n" + "="*60)
    print("LINGUISTIC FINGERPRINT TEST")
    print("="*60)
    print(f"Overall Score: {result.fingerprint_score}/100")
    print(f"Verdict: {result.verdict}")
    print(f"\nPattern Scores:")
    print(f"  Emotional Manipulation: {result.emotional_manipulation}/100")
    print(f"  Certainty Abuse: {result.certainty_abuse}/100")
    print(f"  Source Evasion: {result.source_evasion}/100")
    print(f"  Conspiracy Markers: {result.conspiracy_markers}/100")
    print(f"  Statistical Manipulation: {result.statistical_manipulation}/100")
    print(f"\nExamples Found:")
    for category, examples in result.examples.items():
        if examples:
            print(f"\n  {category.upper()}:")
            for ex in examples:
                print(f"    - {ex}")
    print("="*60)
