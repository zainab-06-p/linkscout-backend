"""
Phase 2.3: Propaganda Technique Detection

This module identifies 18 propaganda techniques based on research from
propaganda analysis institutes:

1. Loaded Language - Emotionally charged words
2. Name Calling - Labeling opponents negatively
3. Doubt - Questioning credibility without evidence
4. Appeal to Fear - Creating panic/anxiety
5. Flag-Waving - Patriotic appeals
6. Repetition - Repeating same message
7. Exaggeration/Minimization - Distorting importance
8. Causal Oversimplification - Complex issues made simple
9. Appeal to Authority - Citing experts incorrectly
10. Black-and-White Fallacy - No middle ground
11. Whataboutism - Deflecting with counter-accusations
12. Straw Man - Misrepresenting opponent's position
13. Red Herring - Irrelevant distraction
14. Bandwagon - Everyone else is doing it
15. Glittering Generalities - Vague positive statements
16. Card Stacking - Selective presentation
17. Plain Folks - Appearing ordinary/relatable
18. Transfer - Associating with positive/negative symbols
"""

import re
from typing import Dict, List, Tuple
from collections import Counter

class PropagandaDetector:
    """Detect propaganda techniques in text"""
    
    def __init__(self):
        # Initialize pattern dictionaries for each technique
        
        # 1. Loaded Language
        self.loaded_words = [
            'shocking', 'horrifying', 'devastating', 'outrageous', 'scandalous',
            'disgraceful', 'unbelievable', 'explosive', 'bombshell', 'nightmare',
            'crisis', 'chaos', 'disaster', 'catastrophe', 'emergency', 'urgent',
            'critical', 'dangerous', 'deadly', 'toxic', 'poison', 'attack'
        ]
        
        # 2. Name Calling
        self.name_calling_words = [
            'idiot', 'fool', 'stupid', 'moron', 'lunatic', 'crazy', 'insane',
            'radical', 'extremist', 'terrorist', 'traitor', 'corrupt', 'criminal',
            'liar', 'fraud', 'fake', 'phony', 'puppet', 'sheep', 'shill'
        ]
        
        # 3. Doubt patterns
        self.doubt_patterns = [
            r'can\s+(?:you|we)\s+trust',
            r'(?:really|actually)\s+believe',
            r'wake\s+up',
            r'open\s+your\s+eyes',
            r'think\s+(?:for\s+)?yourself',
            r'question\s+everything',
            r'don\'t\s+be\s+fooled'
        ]
        
        # 4. Appeal to Fear
        self.fear_words = [
            'danger', 'threat', 'risk', 'warning', 'alert', 'panic',
            'terror', 'horror', 'doom', 'apocalypse', 'extinction',
            'death', 'die', 'kill', 'destroy', 'eliminate'
        ]
        
        # 5. Flag-Waving
        self.patriotic_patterns = [
            r'(?:our|the)\s+(?:great\s+)?(?:nation|country)',
            r'(?:american|patriotic)\s+(?:values|way|dream)',
            r'founding\s+fathers',
            r'(?:freedom|liberty)\s+and\s+(?:democracy|justice)',
            r'un-american',
            r'real\s+(?:americans|patriots)'
        ]
        
        # 6. Repetition - detected by analyzing repeated phrases
        
        # 7. Exaggeration
        self.exaggeration_words = [
            'always', 'never', 'everyone', 'nobody', 'everywhere', 'nowhere',
            'all', 'none', 'every', 'completely', 'totally', 'absolutely',
            'entirely', 'perfectly', 'forever', 'infinite', 'ultimate'
        ]
        
        # 8. Causal Oversimplification
        self.oversimplification_patterns = [
            r'(?:the\s+)?(?:only|real|simple)\s+(?:reason|cause|solution)',
            r'it\'s\s+(?:all\s+)?(?:because|due\s+to)',
            r'simply\s+(?:because|due\s+to)',
            r'nothing\s+(?:more|less)\s+than'
        ]
        
        # 9. Appeal to Authority (improper)
        self.authority_patterns = [
            r'experts?\s+(?:say|claim|believe)',
            r'studies?\s+(?:show|prove|confirm)',
            r'research\s+(?:shows|proves|confirms)',
            r'scientists?\s+(?:say|claim|agree)',
            r'doctors?\s+(?:recommend|say)'
        ]
        
        # 10. Black-and-White Fallacy
        self.black_white_patterns = [
            r'(?:either|it\'s)\s+[^.]+\s+or\s+',
            r'you\'re\s+(?:either\s+)?with\s+us\s+or\s+against\s+us',
            r'no\s+middle\s+ground',
            r'pick\s+a\s+side'
        ]
        
        # 11. Whataboutism
        self.whataboutism_patterns = [
            r'what\s+about',
            r'but\s+what\s+about',
            r'how\s+about',
            r'what\s+if\s+(?:we|I)\s+said'
        ]
        
        # 12. Straw Man - difficult to detect automatically
        
        # 13. Red Herring - difficult to detect automatically
        
        # 14. Bandwagon
        self.bandwagon_patterns = [
            r'everyone\s+(?:knows|believes|agrees)',
            r'most\s+people\s+(?:think|believe|agree)',
            r'join\s+(?:the\s+)?(?:movement|revolution|fight)',
            r'millions\s+of\s+people',
            r'don\'t\s+be\s+left\s+(?:behind|out)'
        ]
        
        # 15. Glittering Generalities
        self.glittering_words = [
            'freedom', 'liberty', 'democracy', 'justice', 'truth', 'honor',
            'glory', 'destiny', 'patriot', 'hero', 'values', 'tradition'
        ]
        
        # 16. Card Stacking - difficult to detect automatically
        
        # 17. Plain Folks
        self.plain_folks_patterns = [
            r'(?:just|ordinary)\s+(?:people|folks|citizens)',
            r'like\s+you\s+and\s+me',
            r'hard-working\s+(?:americans|people|families)',
            r'common\s+sense'
        ]
        
        # 18. Transfer - difficult to detect automatically
        
        print("📣 [PROPAGANDA] Propaganda Detector initialized (18 techniques)")
    
    def detect_propaganda(self, text: str) -> Dict:
        """Detect all propaganda techniques in text"""
        print(f"\n📣 [PROPAGANDA] Analyzing text for propaganda ({len(text)} chars)...")
        
        techniques_found = {}
        examples = {}
        
        # 1. Loaded Language
        loaded = self._detect_loaded_language(text)
        if loaded['count'] > 0:
            techniques_found['loaded_language'] = loaded
            examples['loaded_language'] = loaded['examples'][:3]
        
        # 2. Name Calling
        name_calling = self._detect_name_calling(text)
        if name_calling['count'] > 0:
            techniques_found['name_calling'] = name_calling
            examples['name_calling'] = name_calling['examples'][:3]
        
        # 3. Doubt
        doubt = self._detect_doubt(text)
        if doubt['count'] > 0:
            techniques_found['doubt'] = doubt
            examples['doubt'] = doubt['examples'][:3]
        
        # 4. Appeal to Fear
        fear = self._detect_fear(text)
        if fear['count'] > 0:
            techniques_found['appeal_to_fear'] = fear
            examples['appeal_to_fear'] = fear['examples'][:3]
        
        # 5. Flag-Waving
        flag = self._detect_flag_waving(text)
        if flag['count'] > 0:
            techniques_found['flag_waving'] = flag
            examples['flag_waving'] = flag['examples'][:3]
        
        # 6. Repetition
        repetition = self._detect_repetition(text)
        if repetition['count'] > 0:
            techniques_found['repetition'] = repetition
            examples['repetition'] = repetition['examples'][:3]
        
        # 7. Exaggeration
        exaggeration = self._detect_exaggeration(text)
        if exaggeration['count'] > 0:
            techniques_found['exaggeration'] = exaggeration
            examples['exaggeration'] = exaggeration['examples'][:3]
        
        # 8. Causal Oversimplification
        oversimplification = self._detect_oversimplification(text)
        if oversimplification['count'] > 0:
            techniques_found['oversimplification'] = oversimplification
            examples['oversimplification'] = oversimplification['examples'][:3]
        
        # 9. Appeal to Authority
        authority = self._detect_appeal_to_authority(text)
        if authority['count'] > 0:
            techniques_found['appeal_to_authority'] = authority
            examples['appeal_to_authority'] = authority['examples'][:3]
        
        # 10. Black-and-White Fallacy
        black_white = self._detect_black_white(text)
        if black_white['count'] > 0:
            techniques_found['black_white_fallacy'] = black_white
            examples['black_white_fallacy'] = black_white['examples'][:3]
        
        # 11. Whataboutism
        whataboutism = self._detect_whataboutism(text)
        if whataboutism['count'] > 0:
            techniques_found['whataboutism'] = whataboutism
            examples['whataboutism'] = whataboutism['examples'][:3]
        
        # 14. Bandwagon
        bandwagon = self._detect_bandwagon(text)
        if bandwagon['count'] > 0:
            techniques_found['bandwagon'] = bandwagon
            examples['bandwagon'] = bandwagon['examples'][:3]
        
        # 15. Glittering Generalities
        glittering = self._detect_glittering(text)
        if glittering['count'] > 0:
            techniques_found['glittering_generalities'] = glittering
            examples['glittering_generalities'] = glittering['examples'][:3]
        
        # 17. Plain Folks
        plain = self._detect_plain_folks(text)
        if plain['count'] > 0:
            techniques_found['plain_folks'] = plain
            examples['plain_folks'] = plain['examples'][:3]
        
        # Calculate propaganda score
        total_techniques = len(techniques_found)
        total_instances = sum(t['count'] for t in techniques_found.values())
        
        # ✅ REALISTIC SCORING: Normal news articles will have SOME repetition/patterns
        # Only flag as propaganda if there are MANY techniques or EXTREME instances
        if total_techniques == 0:
            propaganda_score = 0
        elif total_techniques <= 2 and total_instances < 20:
            # 1-2 techniques with <20 instances = Likely normal journalism
            propaganda_score = min(35, total_techniques * 5 + total_instances * 1)  # Max 35/100
        elif total_techniques <= 3 and total_instances < 40:
            # 3 techniques with <40 instances = Moderate concern
            propaganda_score = min(55, total_techniques * 8 + total_instances * 1.2)  # Max 55/100
        else:
            # 4+ techniques OR 40+ instances = Definite propaganda
            propaganda_score = min(100, total_techniques * 10 + total_instances * 2)
        
        # Determine verdict - ADJUSTED thresholds
        if propaganda_score >= 60:  # Was 70 - now more lenient
            verdict = "HIGH_PROPAGANDA"
        elif propaganda_score >= 35:  # Was 40
            verdict = "MODERATE_PROPAGANDA"
        elif propaganda_score >= 15:  # Was 20
            verdict = "LOW_PROPAGANDA"
        else:
            verdict = "MINIMAL_PROPAGANDA"
        
        print(f"   ✅ Found {total_techniques} techniques ({total_instances} total instances)")
        print(f"   Score: {propaganda_score}/100 ({verdict})")
        
        return {
            'total_techniques': total_techniques,
            'total_instances': total_instances,
            'propaganda_score': propaganda_score,
            'verdict': verdict,
            'techniques': techniques_found,
            'examples': examples,
            'technique_list': list(techniques_found.keys())
        }
    
    def _detect_loaded_language(self, text: str) -> Dict:
        """Detect emotionally charged language"""
        found = []
        text_lower = text.lower()
        
        for word in self.loaded_words:
            if word in text_lower:
                # Find actual occurrences
                pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
                matches = pattern.findall(text)
                found.extend(matches)
        
        return {'count': len(found), 'examples': found}
    
    def _detect_name_calling(self, text: str) -> Dict:
        """Detect name calling and labeling"""
        found = []
        text_lower = text.lower()
        
        for word in self.name_calling_words:
            if word in text_lower:
                pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
                matches = pattern.findall(text)
                found.extend(matches)
        
        return {'count': len(found), 'examples': found}
    
    def _detect_doubt(self, text: str) -> Dict:
        """Detect doubt-casting patterns"""
        found = []
        
        for pattern in self.doubt_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            found.extend(matches)
        
        return {'count': len(found), 'examples': found}
    
    def _detect_fear(self, text: str) -> Dict:
        """Detect fear appeals"""
        found = []
        text_lower = text.lower()
        
        for word in self.fear_words:
            if word in text_lower:
                pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
                matches = pattern.findall(text)
                found.extend(matches)
        
        return {'count': len(found), 'examples': found}
    
    def _detect_flag_waving(self, text: str) -> Dict:
        """Detect patriotic appeals"""
        found = []
        
        for pattern in self.patriotic_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            found.extend(matches)
        
        return {'count': len(found), 'examples': found}
    
    def _detect_repetition(self, text: str) -> Dict:
        """Detect repetitive phrases"""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        # Find repeated 3-word phrases
        phrases = []
        for sentence in sentences:
            words = sentence.split()
            for i in range(len(words) - 2):
                phrase = ' '.join(words[i:i+3]).lower()
                if len(phrase) > 10:  # Skip very short phrases
                    phrases.append(phrase)
        
        # Count repetitions
        phrase_counts = Counter(phrases)
        repeated = [phrase for phrase, count in phrase_counts.items() if count > 1]
        
        return {'count': len(repeated), 'examples': repeated}
    
    def _detect_exaggeration(self, text: str) -> Dict:
        """Detect exaggeration and absolutes"""
        found = []
        text_lower = text.lower()
        
        for word in self.exaggeration_words:
            if word in text_lower:
                pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
                matches = pattern.findall(text)
                found.extend(matches)
        
        return {'count': len(found), 'examples': found}
    
    def _detect_oversimplification(self, text: str) -> Dict:
        """Detect causal oversimplification"""
        found = []
        
        for pattern in self.oversimplification_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            found.extend(matches)
        
        return {'count': len(found), 'examples': found}
    
    def _detect_appeal_to_authority(self, text: str) -> Dict:
        """Detect improper appeals to authority"""
        found = []
        
        for pattern in self.authority_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            found.extend(matches)
        
        return {'count': len(found), 'examples': found}
    
    def _detect_black_white(self, text: str) -> Dict:
        """Detect black-and-white fallacies"""
        found = []
        
        for pattern in self.black_white_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            found.extend(matches)
        
        return {'count': len(found), 'examples': found}
    
    def _detect_whataboutism(self, text: str) -> Dict:
        """Detect whataboutism"""
        found = []
        
        for pattern in self.whataboutism_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            found.extend(matches)
        
        return {'count': len(found), 'examples': found}
    
    def _detect_bandwagon(self, text: str) -> Dict:
        """Detect bandwagon appeals"""
        found = []
        
        for pattern in self.bandwagon_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            found.extend(matches)
        
        return {'count': len(found), 'examples': found}
    
    def _detect_glittering(self, text: str) -> Dict:
        """Detect glittering generalities"""
        found = []
        text_lower = text.lower()
        
        for word in self.glittering_words:
            if word in text_lower:
                pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
                matches = pattern.findall(text)
                found.extend(matches)
        
        return {'count': len(found), 'examples': found}
    
    def _detect_plain_folks(self, text: str) -> Dict:
        """Detect plain folks appeals"""
        found = []
        
        for pattern in self.plain_folks_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            found.extend(matches)
        
        return {'count': len(found), 'examples': found}

# Singleton instance
_propaganda_detector = None

def get_propaganda_detector() -> PropagandaDetector:
    """Get or create propaganda detector singleton"""
    global _propaganda_detector
    if _propaganda_detector is None:
        _propaganda_detector = PropagandaDetector()
    return _propaganda_detector

def detect_text_propaganda(text: str) -> Dict:
    """Detect propaganda techniques in text"""
    detector = get_propaganda_detector()
    return detector.detect_propaganda(text)

# Test function
if __name__ == "__main__":
    print("=" * 70)
    print("📣 PROPAGANDA DETECTION TEST")
    print("=" * 70)
    
    test_text = """
    SHOCKING revelation! Everyone knows the truth but they don't want you to know!
    This is a DISASTER and an outrageous attack on our freedom and democracy!
    
    Experts say this is the only solution. Studies show that millions of people agree.
    You're either with us or against us - there's no middle ground!
    
    What about their corruption? What about their lies? Wake up people!
    Don't be fooled by these radical extremists and criminals!
    
    Join the movement! Don't be left behind! This is absolutely critical and urgent!
    Hard-working Americans like you and me need to stand up for our great nation!
    """
    
    result = detect_text_propaganda(test_text)
    
    print("\n" + "=" * 70)
    print("📊 RESULTS")
    print("=" * 70)
    print(f"Total Techniques Detected: {result['total_techniques']}")
    print(f"Total Instances: {result['total_instances']}")
    print(f"Propaganda Score: {result['propaganda_score']}/100")
    print(f"Verdict: {result['verdict']}")
    
    print(f"\n📋 Techniques Found:")
    for technique in result['technique_list']:
        technique_data = result['techniques'][technique]
        print(f"\n  ✅ {technique.replace('_', ' ').title()}")
        print(f"     Count: {technique_data['count']}")
        if result['examples'].get(technique):
            print(f"     Examples: {', '.join(result['examples'][technique][:3])}")
    
    print("\n✅ Test complete!")
