"""
Phase 3.4: Network Propagation Analysis (Simplified)

This module analyzes text patterns that indicate coordinated misinformation campaigns:
- Bot-like language patterns (repetitive, generic, copy-paste)
- Astroturfing indicators (fake grassroots campaigns)
- Coordinated messaging (identical phrases across content)
- Urgency/viral manipulation (designed to spread quickly)
- Social proof manipulation (false popularity claims)

Note: This is a simplified version that analyzes text patterns only.
Full version would integrate with social media APIs for network analysis.
"""

import re
from typing import Dict, List, Set
from collections import Counter
from dataclasses import dataclass

@dataclass
class NetworkAnalysisResult:
    """Results of network propagation analysis"""
    bot_score: float  # 0-100 likelihood of bot-generated content
    astroturfing_score: float  # 0-100 likelihood of fake grassroots campaign
    viral_manipulation_score: float  # 0-100 likelihood of viral manipulation
    coordination_score: float  # 0-100 likelihood of coordinated messaging
    overall_network_score: float  # 0-100 combined score
    verdict: str  # LIKELY_BOT, ASTROTURFING, VIRAL_MANIPULATION, ORGANIC, SUSPICIOUS
    red_flags: List[str]
    details: Dict

class NetworkAnalyzer:
    """Analyze text for signs of coordinated misinformation campaigns"""
    
    def __init__(self):
        # Bot-like patterns
        self.bot_patterns = [
            r'(click|visit|check out|see more|learn more)\s+(here|now|this|link)',
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            r'(follow|subscribe|like|share)\s+(?:me|us|now|today)',
            r'(limited time|act now|hurry|don\'t miss)',
            r'(dm|message)\s+(?:me|us)\s+for\s+(?:more|details|info)'
        ]
        
        # Astroturfing indicators
        self.astroturfing_phrases = [
            'as a concerned citizen', 'as an ordinary person', 'as a taxpayer',
            'we the people', 'grassroots movement', 'ordinary americans',
            'regular folks like us', 'common sense tells us', 'everyone is saying',
            'people are waking up', 'the silent majority', 'real patriots'
        ]
        
        # Viral manipulation phrases
        self.viral_phrases = [
            'share this before it\'s deleted', 'they don\'t want you to see this',
            'going viral', 'breaking news', 'everyone needs to see this',
            'share if you agree', 'repost', 'pass it on', 'spread the word',
            'tag someone who needs to see this', 'share this everywhere'
        ]
        
        # Coordinated messaging indicators
        self.coordination_phrases = [
            'talking points', 'narrative', 'script', 'agenda',
            'the same message', 'identical wording', 'coordinated effort'
        ]
        
        # Generic bot-like phrases
        self.generic_phrases = [
            'i am here to tell you', 'let me be clear', 'make no mistake',
            'the fact is', 'the truth is', 'believe me', 'trust me',
            'i can assure you', 'without a doubt', 'it\'s obvious that'
        ]
        
        # Social proof manipulation
        self.social_proof_patterns = [
            r'(\d+)\s+(?:thousand|million|billion)\s+(?:people|views|shares|likes)',
            r'(?:thousands|millions|billions)\s+of\s+people',
            r'viral\s+(?:video|post|article)',
            r'trending\s+(?:on|now)'
        ]
        
        print("🌐 [NETWORK] Network Analyzer initialized")
    
    def analyze_network_patterns(self, text: str) -> NetworkAnalysisResult:
        """Analyze text for network propagation patterns"""
        print(f"\n🌐 [NETWORK] Analyzing text for bot/astroturfing patterns ({len(text)} chars)...")
        
        text_lower = text.lower()
        red_flags = []
        
        # 1. Analyze bot-like patterns
        bot_score, bot_flags = self._analyze_bot_patterns(text_lower)
        red_flags.extend(bot_flags)
        
        # 2. Analyze astroturfing indicators
        astroturfing_score, astro_flags = self._analyze_astroturfing(text_lower)
        red_flags.extend(astro_flags)
        
        # 3. Analyze viral manipulation
        viral_score, viral_flags = self._analyze_viral_manipulation(text_lower)
        red_flags.extend(viral_flags)
        
        # 4. Analyze coordination indicators
        coordination_score, coord_flags = self._analyze_coordination(text_lower)
        red_flags.extend(coord_flags)
        
        # 5. Analyze text repetition (copy-paste indicator)
        repetition_score, rep_flags = self._analyze_repetition(text)
        red_flags.extend(rep_flags)
        
        # Calculate overall network score
        overall_score = (
            bot_score * 0.3 +
            astroturfing_score * 0.25 +
            viral_score * 0.25 +
            coordination_score * 0.1 +
            repetition_score * 0.1
        )
        
        # Determine verdict
        if bot_score >= 60:
            verdict = "LIKELY_BOT"
        elif astroturfing_score >= 60:
            verdict = "ASTROTURFING"
        elif viral_score >= 60:
            verdict = "VIRAL_MANIPULATION"
        elif overall_score >= 50:
            verdict = "SUSPICIOUS"
        else:
            verdict = "ORGANIC"
        
        print(f"   Bot Score: {bot_score:.1f}/100")
        print(f"   Astroturfing Score: {astroturfing_score:.1f}/100")
        print(f"   Viral Manipulation: {viral_score:.1f}/100")
        print(f"   Overall: {overall_score:.1f}/100 ({verdict})")
        
        return NetworkAnalysisResult(
            bot_score=bot_score,
            astroturfing_score=astroturfing_score,
            viral_manipulation_score=viral_score,
            coordination_score=coordination_score,
            overall_network_score=overall_score,
            verdict=verdict,
            red_flags=list(set(red_flags)),  # Remove duplicates
            details={
                'bot_indicators': bot_flags,
                'astroturfing_indicators': astro_flags,
                'viral_indicators': viral_flags,
                'coordination_indicators': coord_flags,
                'repetition_indicators': rep_flags
            }
        )
    
    def _analyze_bot_patterns(self, text: str) -> tuple:
        """Detect bot-like patterns"""
        score = 0
        flags = []
        
        # Check for bot patterns
        for pattern in self.bot_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                score += 15
                flags.append(f"bot_pattern: {matches[0] if isinstance(matches[0], str) else matches[0][0]}")
        
        # Check for generic phrases
        generic_count = 0
        for phrase in self.generic_phrases:
            if phrase in text:
                generic_count += 1
        
        if generic_count >= 3:
            score += 20
            flags.append(f"generic_phrases: {generic_count} found")
        
        # Check for excessive URLs (bots often include many links)
        url_count = len(re.findall(r'http[s]?://[^\s]+', text))
        if url_count > 3:
            score += 15
            flags.append(f"excessive_urls: {url_count} links")
        
        return min(100, score), flags
    
    def _analyze_astroturfing(self, text: str) -> tuple:
        """Detect astroturfing indicators"""
        score = 0
        flags = []
        
        # Check for astroturfing phrases
        for phrase in self.astroturfing_phrases:
            if phrase in text:
                score += 20
                flags.append(f"astroturfing: '{phrase}'")
        
        # Check for excessive "we/us/our" (false grassroots)
        we_count = len(re.findall(r'\b(?:we|us|our)\b', text))
        if we_count > 5:
            score += 15
            flags.append(f"excessive_collective: {we_count} instances")
        
        return min(100, score), flags
    
    def _analyze_viral_manipulation(self, text: str) -> tuple:
        """Detect viral manipulation tactics"""
        score = 0
        flags = []
        
        # Check for viral phrases
        for phrase in self.viral_phrases:
            if phrase in text:
                score += 25
                flags.append(f"viral_manipulation: '{phrase}'")
        
        # Check for social proof manipulation
        for pattern in self.social_proof_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                score += 15
                flags.append(f"social_proof_claim: {matches[0] if isinstance(matches[0], str) else 'numerical claim'}")
        
        # Check for urgency manipulation
        urgency_words = ['urgent', 'hurry', 'immediately', 'now', 'today', 'act fast', 'limited time']
        urgency_count = sum(1 for word in urgency_words if word in text)
        if urgency_count >= 3:
            score += 15
            flags.append(f"urgency_manipulation: {urgency_count} instances")
        
        return min(100, score), flags
    
    def _analyze_coordination(self, text: str) -> tuple:
        """Detect coordinated messaging indicators"""
        score = 0
        flags = []
        
        # Check for coordination phrases
        for phrase in self.coordination_phrases:
            if phrase in text:
                score += 20
                flags.append(f"coordination: '{phrase}'")
        
        # Check for hashtag patterns (coordinated campaigns use specific hashtags)
        hashtags = re.findall(r'#\w+', text)
        if len(hashtags) > 5:
            score += 15
            flags.append(f"excessive_hashtags: {len(hashtags)} found")
        
        return min(100, score), flags
    
    def _analyze_repetition(self, text: str) -> tuple:
        """Detect repetitive patterns (copy-paste)"""
        score = 0
        flags = []
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        # Check for repeated sentences
        sentence_counts = Counter(sentences)
        repeated = [sent for sent, count in sentence_counts.items() if count > 1]
        
        if repeated:
            score += 30
            flags.append(f"repeated_sentences: {len(repeated)} duplicates")
        
        # Check for repeated phrases (3+ words)
        words = text.lower().split()
        phrases = []
        for i in range(len(words) - 2):
            phrase = ' '.join(words[i:i+3])
            if len(phrase) > 15:  # Skip very short phrases
                phrases.append(phrase)
        
        phrase_counts = Counter(phrases)
        repeated_phrases = [p for p, count in phrase_counts.items() if count > 1]
        
        if len(repeated_phrases) > 3:
            score += 20
            flags.append(f"repeated_phrases: {len(repeated_phrases)} found")
        
        return min(100, score), flags

# Singleton instance
_network_analyzer = None

def get_network_analyzer() -> NetworkAnalyzer:
    """Get or create network analyzer singleton"""
    global _network_analyzer
    if _network_analyzer is None:
        _network_analyzer = NetworkAnalyzer()
    return _network_analyzer

def analyze_network_patterns(text: str) -> Dict:
    """Analyze text for network propagation patterns"""
    analyzer = get_network_analyzer()
    result = analyzer.analyze_network_patterns(text)
    
    return {
        'bot_score': result.bot_score,
        'astroturfing_score': result.astroturfing_score,
        'viral_manipulation_score': result.viral_manipulation_score,
        'coordination_score': result.coordination_score,
        'overall_network_score': result.overall_network_score,
        'verdict': result.verdict,
        'red_flags': result.red_flags,
        'details': result.details
    }

# Test function
if __name__ == "__main__":
    print("=" * 70)
    print("🌐 NETWORK ANALYSIS TEST")
    print("=" * 70)
    
    test_text = """
    As a concerned citizen and ordinary American, we the people need to act now!
    Share this before it's deleted! Everyone needs to see this! Going viral!
    
    Click here to learn more: http://example.com/fake-news
    Visit this link now: http://example.com/scam
    Follow me for more truth: http://example.com/bot
    
    This has 5 million views and trending on all platforms! Millions of people 
    are sharing this! The silent majority agrees with us!
    
    Share if you agree! Repost this everywhere! Tag someone who needs to see this!
    Pass it on! Spread the word! Don't miss this limited time opportunity!
    
    As ordinary folks like us, we must stand together. Real patriots know the truth.
    The grassroots movement is growing. Common sense tells us we're right.
    """
    
    result = analyze_network_patterns(test_text)
    
    print("\n" + "=" * 70)
    print("📊 RESULTS")
    print("=" * 70)
    print(f"Bot Score: {result['bot_score']:.1f}/100")
    print(f"Astroturfing Score: {result['astroturfing_score']:.1f}/100")
    print(f"Viral Manipulation Score: {result['viral_manipulation_score']:.1f}/100")
    print(f"Coordination Score: {result['coordination_score']:.1f}/100")
    print(f"Overall Network Score: {result['overall_network_score']:.1f}/100")
    print(f"Verdict: {result['verdict']}")
    
    if result['red_flags']:
        print(f"\n⚠️ Red Flags ({len(result['red_flags'])}):")
        for flag in result['red_flags'][:10]:  # Show first 10
            print(f"  - {flag}")
    
    print("\n✅ Test complete!")
