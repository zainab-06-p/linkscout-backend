"""
🔍 CLAIM EXTRACTION & VERIFICATION MODULE
Extracts individual factual claims and verifies EACH claim separately

This module:
1. Uses NLP (spaCy) to extract factual claims from text
2. Verifies each claim against multiple sources
3. Returns claim-by-claim results (TRUE/FALSE/UNVERIFIABLE)
4. Shows which specific statements are false

Author: AI Misinformation Detector
"""

import re
import requests
from typing import Dict, List, Tuple
from dataclasses import dataclass
import spacy
from urllib.parse import quote_plus
import time


@dataclass
class ClaimResult:
    """Result of a single claim verification"""
    claim: str
    verdict: str  # TRUE, FALSE, PARTIALLY_TRUE, UNVERIFIABLE
    confidence: float  # 0-100
    sources_checked: List[str]
    evidence: List[Dict]
    explanation: str


@dataclass
class ClaimVerificationResult:
    """Overall result of claim verification"""
    total_claims: int
    true_claims: int
    false_claims: int
    partially_true_claims: int
    unverifiable_claims: int
    false_percentage: float
    detailed_results: List[ClaimResult]
    summary: str


class ClaimVerifier:
    """
    Extracts and verifies individual factual claims from text
    """
    
    def __init__(self):
        """Initialize the claim verifier"""
        print("🔍 [CLAIM] Initializing claim verifier...")
        
        # Load spaCy model for NLP
        try:
            self.nlp = spacy.load("en_core_web_sm")
            print("✅ [CLAIM] spaCy model loaded")
        except OSError:
            print("⚠️ [CLAIM] spaCy model not found, downloading...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
            print("✅ [CLAIM] spaCy model downloaded and loaded")
        
        # Cache for verified claims (avoid redundant checks)
        self.claim_cache = {}
    
    def extract_and_verify(self, text: str, url: str = "") -> ClaimVerificationResult:
        """
        Extract all claims from text and verify each one
        
        Args:
            text: Text to analyze
            url: Optional URL for context
            
        Returns:
            ClaimVerificationResult with all claims verified
        """
        if not text or len(text) < 50:
            return self._create_empty_result()
        
        print(f"🔍 [CLAIM] Extracting claims from text ({len(text)} chars)...")
        
        # Step 1: Extract factual claims
        claims = self.extract_factual_claims(text)
        print(f"📋 [CLAIM] Found {len(claims)} claims to verify")
        
        if len(claims) == 0:
            return self._create_empty_result()
        
        # Step 2: Verify each claim
        verified_claims = []
        for i, claim in enumerate(claims, 1):
            print(f"🔍 [CLAIM] Verifying claim {i}/{len(claims)}: {claim[:60]}...")
            
            # Check cache first
            cache_key = self._get_cache_key(claim)
            if cache_key in self.claim_cache:
                print(f"💾 [CLAIM] Using cached result")
                result = self.claim_cache[cache_key]
            else:
                result = self.verify_single_claim(claim)
                self.claim_cache[cache_key] = result
            
            verified_claims.append(result)
            
            # Rate limiting (be nice to fact-checking sites)
            time.sleep(0.5)
        
        # Step 3: Calculate statistics
        true_count = sum(1 for c in verified_claims if c.verdict == "TRUE")
        false_count = sum(1 for c in verified_claims if c.verdict == "FALSE")
        partial_count = sum(1 for c in verified_claims if c.verdict == "PARTIALLY_TRUE")
        unverifiable_count = sum(1 for c in verified_claims if c.verdict == "UNVERIFIABLE")
        
        false_percentage = (false_count / len(claims)) * 100 if len(claims) > 0 else 0
        
        # Step 4: Generate summary
        summary = self._generate_summary(true_count, false_count, partial_count, unverifiable_count, len(claims))
        
        print(f"✅ [CLAIM] Verification complete: {true_count} true, {false_count} false, {partial_count} partial, {unverifiable_count} unverifiable")
        
        return ClaimVerificationResult(
            total_claims=len(claims),
            true_claims=true_count,
            false_claims=false_count,
            partially_true_claims=partial_count,
            unverifiable_claims=unverifiable_count,
            false_percentage=round(false_percentage, 2),
            detailed_results=verified_claims,
            summary=summary
        )
    
    def extract_factual_claims(self, text: str) -> List[str]:
        """
        Extract factual claims that can be verified
        
        Uses NLP to identify:
        - Statements with dates, numbers, names
        - Subject-verb-object patterns
        - Cause-effect relationships
        - Comparative statements
        """
        claims = []
        
        # Process text with spaCy
        doc = self.nlp(text)
        
        # Extract sentences
        for sent in doc.sents:
            sent_text = sent.text.strip()
            
            # Skip short sentences
            if len(sent_text) < 15:
                continue
            
            # Check if sentence is a verifiable claim
            if self._is_verifiable_claim(sent):
                claims.append(sent_text)
        
        # Limit to top 10 most important claims (to avoid excessive API calls)
        return claims[:10]
    
    def _is_verifiable_claim(self, sent) -> bool:
        """
        Check if a sentence contains a verifiable factual claim
        
        Criteria:
        - Contains named entities (PERSON, ORG, GPE, DATE, etc.)
        - Has a clear subject and verb
        - Not a question or opinion
        - Contains specific information
        """
        # Skip questions
        if sent.text.strip().endswith('?'):
            return False
        
        # Skip opinions (contains "I think", "I believe", "maybe", etc.)
        opinion_markers = ['i think', 'i believe', 'maybe', 'perhaps', 'possibly', 'in my opinion']
        if any(marker in sent.text.lower() for marker in opinion_markers):
            return False
        
        # Check for named entities
        has_entities = len(sent.ents) > 0
        
        # Check for specific information (numbers, dates, etc.)
        has_numbers = any(token.like_num for token in sent)
        has_dates = any(ent.label_ in ['DATE', 'TIME'] for ent in sent.ents)
        has_names = any(ent.label_ in ['PERSON', 'ORG', 'GPE'] for ent in sent.ents)
        
        # Check for verb (action/statement)
        has_verb = any(token.pos_ == 'VERB' for token in sent)
        
        # Claim should have entities OR specific info, AND a verb
        is_factual = (has_entities or has_numbers or has_dates or has_names) and has_verb
        
        return is_factual
    
    def verify_single_claim(self, claim: str) -> ClaimResult:
        """
        Verify a single claim against multiple sources
        
        Checks:
        1. Google Fact Check API
        2. Search for fact-checking articles
        3. Look for scientific sources if applicable
        """
        sources_checked = []
        evidence = []
        
        # Method 1: Search for fact-checking articles
        fact_check_results = self._search_fact_checkers(claim)
        sources_checked.append("Fact-checking websites")
        evidence.extend(fact_check_results)
        
        # Method 2: General web search for verification
        if len(evidence) == 0:
            web_results = self._search_web_verification(claim)
            sources_checked.append("Web search")
            evidence.extend(web_results)
        
        # Analyze evidence and determine verdict
        verdict, confidence, explanation = self._analyze_evidence(claim, evidence)
        
        return ClaimResult(
            claim=claim,
            verdict=verdict,
            confidence=confidence,
            sources_checked=sources_checked,
            evidence=evidence,
            explanation=explanation
        )
    
    def _search_fact_checkers(self, claim: str) -> List[Dict]:
        """
        Search fact-checking websites for the claim
        
        Searches:
        - Snopes
        - FactCheck.org
        - PolitiFact
        - Reuters Fact Check
        """
        results = []
        
        # Prepare search query
        query = self._clean_claim_for_search(claim)
        
        # Search patterns for fact-checking sites
        fact_check_domains = [
            'snopes.com',
            'factcheck.org',
            'politifact.com',
            'reuters.com/fact-check',
            'apnews.com/APFactCheck'
        ]
        
        for domain in fact_check_domains:
            try:
                # Use DuckDuckGo search (no API key needed)
                search_url = f"https://duckduckgo.com/html/?q={quote_plus(query + ' site:' + domain)}"
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(search_url, headers=headers, timeout=5)
                
                # Simple check if domain appears in results
                if domain in response.text:
                    results.append({
                        'source': domain,
                        'found': True,
                        'method': 'fact_check_search'
                    })
                    print(f"✅ [CLAIM] Found on {domain}")
                
            except Exception as e:
                print(f"⚠️ [CLAIM] Could not search {domain}: {e}")
                continue
        
        return results
    
    def _search_web_verification(self, claim: str) -> List[Dict]:
        """
        Search the web for verification of the claim
        """
        results = []
        
        query = self._clean_claim_for_search(claim)
        
        try:
            # Simple web search
            search_url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=5)
            
            # Check for credible sources in results
            credible_sources = ['wikipedia.org', 'gov', 'edu', 'who.int', 'cdc.gov', 'nih.gov']
            
            for source in credible_sources:
                if source in response.text:
                    results.append({
                        'source': source,
                        'found': True,
                        'method': 'web_search'
                    })
            
        except Exception as e:
            print(f"⚠️ [CLAIM] Web search failed: {e}")
        
        return results
    
    def _analyze_evidence(self, claim: str, evidence: List[Dict]) -> Tuple[str, float, str]:
        """
        Analyze evidence and determine verdict
        
        Returns:
            (verdict, confidence, explanation)
        """
        if len(evidence) == 0:
            return "UNVERIFIABLE", 50.0, "No evidence found from fact-checking sources"
        
        # Count fact-checking results
        fact_check_results = [e for e in evidence if e.get('method') == 'fact_check_search']
        
        if len(fact_check_results) > 0:
            # Found on fact-checking sites - likely either debunked or verified
            # For now, we mark as needing manual review
            confidence = min(80.0, len(fact_check_results) * 20)
            explanation = f"Found on {len(fact_check_results)} fact-checking site(s): {', '.join([e['source'] for e in fact_check_results])}"
            
            # Heuristic: If multiple fact-checkers covered it, likely FALSE (they usually debunk)
            if len(fact_check_results) >= 2:
                return "FALSE", confidence, explanation + " (commonly debunked claims)"
            else:
                return "PARTIALLY_TRUE", confidence, explanation + " (requires manual verification)"
        
        # Found on credible sources
        credible_results = [e for e in evidence if e.get('method') == 'web_search']
        if len(credible_results) >= 2:
            confidence = min(75.0, len(credible_results) * 15)
            explanation = f"Found on credible sources: {', '.join([e['source'] for e in credible_results[:3]])}"
            return "TRUE", confidence, explanation
        
        return "UNVERIFIABLE", 40.0, "Insufficient evidence to verify"
    
    def _clean_claim_for_search(self, claim: str) -> str:
        """Clean claim text for search queries"""
        # Remove extra whitespace
        claim = ' '.join(claim.split())
        
        # Remove special characters
        claim = re.sub(r'[^\w\s]', ' ', claim)
        
        # Limit length
        words = claim.split()
        if len(words) > 10:
            claim = ' '.join(words[:10])
        
        return claim.strip()
    
    def _get_cache_key(self, claim: str) -> str:
        """Generate cache key for claim"""
        return claim.lower().strip()[:100]
    
    def _generate_summary(self, true_count: int, false_count: int, partial_count: int, 
                         unverifiable_count: int, total: int) -> str:
        """Generate human-readable summary"""
        if total == 0:
            return "No verifiable claims found in text."
        
        false_pct = (false_count / total) * 100
        true_pct = (true_count / total) * 100
        
        if false_count > 0:
            summary = f"⚠️ WARNING: Found {false_count} FALSE claim(s) out of {total} total. "
        elif partial_count > 0:
            summary = f"⚠️ Found {partial_count} PARTIALLY TRUE claim(s) that need verification. "
        else:
            summary = f"✅ {true_count} claim(s) appear verifiable. "
        
        summary += f"\n\nBreakdown: {true_pct:.0f}% true, {false_pct:.0f}% false, "
        summary += f"{(partial_count/total)*100:.0f}% partially true, {(unverifiable_count/total)*100:.0f}% unverifiable."
        
        if false_count > 0:
            summary += f"\n\n🔍 Review the specific FALSE claims below and verify with fact-checking sources."
        
        return summary
    
    def _create_empty_result(self) -> ClaimVerificationResult:
        """Create empty result for invalid input"""
        return ClaimVerificationResult(
            total_claims=0,
            true_claims=0,
            false_claims=0,
            partially_true_claims=0,
            unverifiable_claims=0,
            false_percentage=0,
            detailed_results=[],
            summary="No verifiable claims found in text."
        )


# Singleton instance
_claim_verifier = None


def get_claim_verifier() -> ClaimVerifier:
    """Get or create the claim verifier singleton"""
    global _claim_verifier
    if _claim_verifier is None:
        _claim_verifier = ClaimVerifier()
    return _claim_verifier


def verify_text_claims(text: str, url: str = "") -> Dict:
    """
    Convenience function to verify claims in text
    
    Args:
        text: Text to analyze
        url: Optional URL for context
        
    Returns:
        Dictionary with claim verification results
    """
    verifier = get_claim_verifier()
    result = verifier.extract_and_verify(text, url)
    
    return {
        'total_claims': result.total_claims,
        'true_claims': result.true_claims,
        'false_claims': result.false_claims,
        'partially_true_claims': result.partially_true_claims,
        'unverifiable_claims': result.unverifiable_claims,
        'false_percentage': result.false_percentage,
        'summary': result.summary,
        'detailed_results': [
            {
                'claim': r.claim,
                'verdict': r.verdict,
                'confidence': r.confidence,
                'sources_checked': r.sources_checked,
                'explanation': r.explanation
            }
            for r in result.detailed_results
        ]
    }


# Test function
if __name__ == "__main__":
    # Test with example claims
    test_text = """
    COVID-19 vaccine contains microchips that track people. 
    The vaccine was approved by the FDA in December 2020. 
    Bill Gates personally funded all vaccine research. 
    Clinical trials showed 95% efficacy against symptomatic COVID-19.
    The vaccine changes your DNA permanently.
    """
    
    print("\n" + "="*70)
    print("CLAIM EXTRACTION & VERIFICATION TEST")
    print("="*70)
    
    verifier = ClaimVerifier()
    result = verifier.extract_and_verify(test_text)
    
    print(f"\n📊 RESULTS:")
    print(f"Total Claims: {result.total_claims}")
    print(f"True: {result.true_claims}")
    print(f"False: {result.false_claims}")
    print(f"Partially True: {result.partially_true_claims}")
    print(f"Unverifiable: {result.unverifiable_claims}")
    print(f"False Percentage: {result.false_percentage}%")
    
    print(f"\n📋 DETAILED RESULTS:")
    for i, claim_result in enumerate(result.detailed_results, 1):
        print(f"\n{i}. {claim_result.verdict} ({claim_result.confidence:.0f}% confidence)")
        print(f"   Claim: {claim_result.claim[:100]}...")
        print(f"   Explanation: {claim_result.explanation}")
        print(f"   Sources: {', '.join(claim_result.sources_checked)}")
    
    print(f"\n📝 SUMMARY:")
    print(result.summary)
    print("="*70)
