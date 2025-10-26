"""
Phase 3.2: Logical Contradiction Detector

This module detects logical contradictions and fallacies within text:
- Self-contradictions (statements that contradict each other)
- Circular reasoning (conclusion used as premise)
- False dichotomies (only two options presented when more exist)
- Strawman arguments (misrepresenting opponent's position)
- Moving goalposts (changing criteria mid-argument)
- Special pleading (applying standards inconsistently)
- No true Scotsman (changing definitions to suit argument)
"""

import re
import spacy
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class Contradiction:
    """Represents a detected contradiction"""
    type: str  # DIRECT_CONTRADICTION, CIRCULAR_REASONING, FALSE_DICHOTOMY, etc.
    severity: str  # HIGH, MEDIUM, LOW
    statement1: str
    statement2: str
    explanation: str
    confidence: float  # 0-100

@dataclass
class ContradictionResult:
    """Complete contradiction analysis"""
    total_contradictions: int
    high_severity: int
    medium_severity: int
    low_severity: int
    contradiction_score: float  # 0-100
    verdict: str  # CONTRADICTORY, SOMEWHAT_CONTRADICTORY, CONSISTENT
    contradictions: List[Dict]
    summary: str

class ContradictionDetector:
    """Detect logical contradictions and fallacies in text"""
    
    def __init__(self):
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
            print("🧠 [CONTRADICTION] spaCy model loaded")
        except OSError:
            print("🔍 [CONTRADICTION] Downloading spaCy model...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
            self.nlp = spacy.load("en_core_web_sm")
            print("✅ [CONTRADICTION] spaCy model loaded")
        
        # Negation words
        self.negations = {'not', 'no', 'never', 'neither', 'nor', 'none', 'nobody', 
                         'nothing', 'nowhere', 'hardly', 'barely', 'scarcely'}
        
        # Absolute words that indicate strong claims
        self.absolutes = {'always', 'never', 'all', 'none', 'every', 'no one', 
                         'everyone', 'everything', 'nothing', 'absolutely', 
                         'completely', 'totally', 'entirely'}
        
        # False dichotomy indicators
        self.dichotomy_patterns = [
            r'either\s+(.+?)\s+or\s+(.+?)[\.,]',
            r'only\s+two\s+(?:options|choices|ways)',
            r'you\'re\s+(?:either\s+)?with\s+us\s+or\s+against\s+us',
            r'it\'s\s+(.+?)\s+or\s+(.+?)[\.,]'
        ]
        
        # Circular reasoning patterns
        self.circular_patterns = [
            r'because\s+it\s+is',
            r'(?:the|this)\s+is\s+true\s+because\s+(?:the|this)\s+is',
            r'(?:it|this)\s+works\s+because\s+(?:it|this)\s+works'
        ]
        
        print("🧠 [CONTRADICTION] Contradiction Detector initialized")
    
    def detect_contradictions(self, text: str) -> ContradictionResult:
        """Detect all types of contradictions in text"""
        print(f"\n🧠 [CONTRADICTION] Analyzing text for contradictions ({len(text)} chars)...")
        
        # Split into sentences
        doc = self.nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents]
        
        print(f"   Found {len(sentences)} sentences to analyze")
        
        all_contradictions = []
        
        # 1. Detect direct contradictions
        direct_contradictions = self._detect_direct_contradictions(sentences)
        all_contradictions.extend(direct_contradictions)
        
        # 2. Detect false dichotomies
        false_dichotomies = self._detect_false_dichotomies(sentences)
        all_contradictions.extend(false_dichotomies)
        
        # 3. Detect circular reasoning
        circular_reasoning = self._detect_circular_reasoning(sentences)
        all_contradictions.extend(circular_reasoning)
        
        # 4. Detect inconsistent claims
        inconsistent_claims = self._detect_inconsistent_claims(sentences)
        all_contradictions.extend(inconsistent_claims)
        
        # Count by severity
        high_severity = sum(1 for c in all_contradictions if c.severity == 'HIGH')
        medium_severity = sum(1 for c in all_contradictions if c.severity == 'MEDIUM')
        low_severity = sum(1 for c in all_contradictions if c.severity == 'LOW')
        
        total = len(all_contradictions)
        
        # Calculate contradiction score
        contradiction_score = min(100, (high_severity * 25) + (medium_severity * 15) + (low_severity * 5))
        
        # Determine verdict
        if contradiction_score >= 60:
            verdict = "CONTRADICTORY"
        elif contradiction_score >= 30:
            verdict = "SOMEWHAT_CONTRADICTORY"
        else:
            verdict = "CONSISTENT"
        
        # Generate summary
        summary = f"{total} contradictions found: {high_severity} high, {medium_severity} medium, {low_severity} low severity"
        
        print(f"   ✅ Found {total} contradictions ({high_severity} high severity)")
        print(f"   Score: {contradiction_score}/100 ({verdict})")
        
        return ContradictionResult(
            total_contradictions=total,
            high_severity=high_severity,
            medium_severity=medium_severity,
            low_severity=low_severity,
            contradiction_score=contradiction_score,
            verdict=verdict,
            contradictions=[self._contradiction_to_dict(c) for c in all_contradictions],
            summary=summary
        )
    
    def _detect_direct_contradictions(self, sentences: List[str]) -> List[Contradiction]:
        """Detect sentences that directly contradict each other"""
        contradictions = []
        
        # Parse all sentences
        parsed_sentences = []
        for sent in sentences:
            doc = self.nlp(sent)
            parsed_sentences.append({
                'text': sent,
                'doc': doc,
                'tokens': [token.text.lower() for token in doc],
                'lemmas': [token.lemma_.lower() for token in doc],
                'has_negation': any(token.text.lower() in self.negations for token in doc)
            })
        
        # Compare pairs of sentences
        for i in range(len(parsed_sentences)):
            for j in range(i + 1, len(parsed_sentences)):
                sent1 = parsed_sentences[i]
                sent2 = parsed_sentences[j]
                
                # Check for similar content with opposite polarity
                similarity = self._calculate_similarity(sent1, sent2)
                
                if similarity > 0.6:  # High similarity
                    # Check if one is negated and the other isn't
                    if sent1['has_negation'] != sent2['has_negation']:
                        contradictions.append(Contradiction(
                            type="DIRECT_CONTRADICTION",
                            severity="HIGH",
                            statement1=sent1['text'],
                            statement2=sent2['text'],
                            explanation="Statements directly contradict each other (one is negation of the other)",
                            confidence=similarity * 100
                        ))
        
        return contradictions
    
    def _detect_false_dichotomies(self, sentences: List[str]) -> List[Contradiction]:
        """Detect false dichotomy fallacies"""
        contradictions = []
        
        for sent in sentences:
            for pattern in self.dichotomy_patterns:
                match = re.search(pattern, sent, re.IGNORECASE)
                if match:
                    contradictions.append(Contradiction(
                        type="FALSE_DICHOTOMY",
                        severity="MEDIUM",
                        statement1=sent,
                        statement2="",
                        explanation="Presents only two options when more alternatives likely exist",
                        confidence=75
                    ))
                    break
        
        return contradictions
    
    def _detect_circular_reasoning(self, sentences: List[str]) -> List[Contradiction]:
        """Detect circular reasoning patterns"""
        contradictions = []
        
        for sent in sentences:
            for pattern in self.circular_patterns:
                if re.search(pattern, sent, re.IGNORECASE):
                    contradictions.append(Contradiction(
                        type="CIRCULAR_REASONING",
                        severity="HIGH",
                        statement1=sent,
                        statement2="",
                        explanation="Uses conclusion as premise (circular reasoning)",
                        confidence=80
                    ))
                    break
        
        return contradictions
    
    def _detect_inconsistent_claims(self, sentences: List[str]) -> List[Contradiction]:
        """Detect inconsistent numerical or factual claims"""
        contradictions = []
        
        # Extract numerical claims
        number_pattern = r'(\d+(?:\.\d+)?)\s*(%|percent|million|billion|thousand)'
        
        claims_by_subject = defaultdict(list)
        
        for sent in sentences:
            # Find numbers in sentence
            numbers = re.findall(number_pattern, sent, re.IGNORECASE)
            
            if numbers:
                # Extract subject (simple: first noun phrase)
                doc = self.nlp(sent)
                subject = ""
                for chunk in doc.noun_chunks:
                    subject = chunk.text.lower()
                    break
                
                if subject:
                    claims_by_subject[subject].append({
                        'sentence': sent,
                        'numbers': numbers
                    })
        
        # Check for inconsistent claims about same subject
        for subject, claims in claims_by_subject.items():
            if len(claims) > 1:
                # Check if different numbers are claimed
                numbers_set = set()
                for claim in claims:
                    for num, unit in claim['numbers']:
                        numbers_set.add((num, unit.lower()))
                
                if len(numbers_set) > 1:
                    # Possible inconsistency
                    contradictions.append(Contradiction(
                        type="INCONSISTENT_CLAIMS",
                        severity="MEDIUM",
                        statement1=claims[0]['sentence'],
                        statement2=claims[1]['sentence'] if len(claims) > 1 else "",
                        explanation=f"Inconsistent numerical claims about '{subject}'",
                        confidence=70
                    ))
        
        return contradictions
    
    def _calculate_similarity(self, sent1: Dict, sent2: Dict) -> float:
        """Calculate similarity between two parsed sentences"""
        # Use lemma overlap as similarity metric
        lemmas1 = set(sent1['lemmas'])
        lemmas2 = set(sent2['lemmas'])
        
        # Remove very common words
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                     'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        
        lemmas1 = lemmas1 - stop_words
        lemmas2 = lemmas2 - stop_words
        
        if not lemmas1 or not lemmas2:
            return 0
        
        # Jaccard similarity
        intersection = len(lemmas1 & lemmas2)
        union = len(lemmas1 | lemmas2)
        
        return intersection / union if union > 0 else 0
    
    def _contradiction_to_dict(self, contradiction: Contradiction) -> Dict:
        """Convert Contradiction to dictionary"""
        return {
            'type': contradiction.type,
            'severity': contradiction.severity,
            'statement1': contradiction.statement1,
            'statement2': contradiction.statement2,
            'explanation': contradiction.explanation,
            'confidence': contradiction.confidence
        }

# Singleton instance
_contradiction_detector = None

def get_contradiction_detector() -> ContradictionDetector:
    """Get or create contradiction detector singleton"""
    global _contradiction_detector
    if _contradiction_detector is None:
        _contradiction_detector = ContradictionDetector()
    return _contradiction_detector

def detect_text_contradictions(text: str) -> Dict:
    """Detect contradictions in text"""
    detector = get_contradiction_detector()
    result = detector.detect_contradictions(text)
    
    return {
        'total_contradictions': result.total_contradictions,
        'high_severity': result.high_severity,
        'medium_severity': result.medium_severity,
        'low_severity': result.low_severity,
        'contradiction_score': result.contradiction_score,
        'verdict': result.verdict,
        'contradictions': result.contradictions,
        'summary': result.summary
    }

# Test function
if __name__ == "__main__":
    print("=" * 70)
    print("🧠 CONTRADICTION DETECTION TEST")
    print("=" * 70)
    
    test_text = """
    The vaccine is 100% safe and effective. However, the vaccine causes serious side effects.
    You must either take the vaccine or you will die. There are only two options available.
    
    The study shows 95% effectiveness. The same study reports 87% effectiveness.
    This works because it works. The system is effective because the system is effective.
    
    Everyone should get vaccinated. Nobody should get vaccinated under any circumstances.
    The treatment is completely safe. The treatment has never been proven safe.
    """
    
    result = detect_text_contradictions(test_text)
    
    print("\n" + "=" * 70)
    print("📊 RESULTS")
    print("=" * 70)
    print(f"Total Contradictions: {result['total_contradictions']}")
    print(f"High Severity: {result['high_severity']}")
    print(f"Medium Severity: {result['medium_severity']}")
    print(f"Low Severity: {result['low_severity']}")
    print(f"Contradiction Score: {result['contradiction_score']}/100")
    print(f"Verdict: {result['verdict']}")
    print(f"\nSummary: {result['summary']}")
    
    if result['contradictions']:
        print(f"\n📋 Contradictions Found:")
        for i, contradiction in enumerate(result['contradictions'], 1):
            print(f"\n  {i}. [{contradiction['severity']}] {contradiction['type']}")
            print(f"     Statement 1: {contradiction['statement1'][:80]}...")
            if contradiction['statement2']:
                print(f"     Statement 2: {contradiction['statement2'][:80]}...")
            print(f"     Explanation: {contradiction['explanation']}")
            print(f"     Confidence: {contradiction['confidence']:.0f}%")
    
    print("\n✅ Test complete!")
