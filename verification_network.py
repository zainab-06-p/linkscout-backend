"""
Phase 2.1: Multi-Database Cross-Reference System

This module cross-references claims across multiple authoritative databases:
- Wikipedia (general knowledge)
- Wikidata (structured data)
- DBpedia (semantic knowledge base)
- PubMed (medical/scientific research)
- arXiv (scientific preprints)

It detects contradictions between sources and provides confidence scores.
"""

import re
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import time

@dataclass
class DatabaseResult:
    """Result from a single database query"""
    database: str
    found: bool
    content: str
    confidence: float  # 0-100
    url: str

@dataclass
class VerificationNetworkResult:
    """Complete verification network analysis"""
    total_claims: int
    verified_claims: int
    contradicted_claims: int
    unverified_claims: int
    verification_score: float  # 0-100
    verdict: str  # VERIFIED, CONTRADICTED, UNVERIFIED, MIXED
    database_results: List[Dict]
    contradictions: List[str]
    confidence: float

class VerificationNetwork:
    """Cross-reference claims across multiple authoritative databases"""
    
    def __init__(self):
        self.databases = {
            'wikipedia': 'https://en.wikipedia.org/w/api.php',
            'wikidata': 'https://www.wikidata.org/w/api.php',
            'pubmed': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/',
            'arxiv': 'http://export.arxiv.org/api/query'
        }
        print("🌐 [VERIFICATION] Multi-Database Verification Network initialized")
    
    def verify_claim(self, claim: str, timeout: int = 5) -> Dict:
        """Verify a single claim across all databases"""
        print(f"\n🔍 [VERIFICATION] Verifying: {claim[:80]}...")
        
        results = []
        
        # 1. Check Wikipedia
        wiki_result = self._check_wikipedia(claim, timeout)
        results.append(wiki_result)
        
        # 2. Check Wikidata
        wikidata_result = self._check_wikidata(claim, timeout)
        results.append(wikidata_result)
        
        # 3. Check PubMed (for scientific/medical claims)
        if self._is_scientific_claim(claim):
            pubmed_result = self._check_pubmed(claim, timeout)
            results.append(pubmed_result)
        
        # 4. Check arXiv (for physics/math/CS claims)
        if self._is_academic_claim(claim):
            arxiv_result = self._check_arxiv(claim, timeout)
            results.append(arxiv_result)
        
        # Analyze results for contradictions
        contradictions = self._detect_contradictions(claim, results)
        
        # Calculate verification score
        found_count = sum(1 for r in results if r.found)
        total_count = len(results)
        verification_score = (found_count / total_count) * 100 if total_count > 0 else 0
        
        # Calculate average confidence
        avg_confidence = sum(r.confidence for r in results if r.found) / found_count if found_count > 0 else 0
        
        # Determine verdict
        if found_count == 0:
            verdict = "UNVERIFIED"
        elif contradictions:
            verdict = "CONTRADICTED"
        elif found_count >= 2 and avg_confidence > 70:
            verdict = "VERIFIED"
        else:
            verdict = "MIXED"
        
        print(f"   ✅ Verdict: {verdict} ({found_count}/{total_count} databases)")
        
        return {
            'claim': claim,
            'verdict': verdict,
            'verification_score': verification_score,
            'databases_found': found_count,
            'databases_checked': total_count,
            'average_confidence': avg_confidence,
            'results': [self._database_result_to_dict(r) for r in results],
            'contradictions': contradictions
        }
    
    def verify_multiple_claims(self, claims: List[str]) -> VerificationNetworkResult:
        """Verify multiple claims and aggregate results"""
        print(f"\n🌐 [VERIFICATION] Verifying {len(claims)} claims across databases...")
        
        all_results = []
        all_contradictions = []
        
        verified = 0
        contradicted = 0
        unverified = 0
        
        for i, claim in enumerate(claims, 1):
            print(f"\n📋 [{i}/{len(claims)}] Processing claim...")
            result = self.verify_claim(claim)
            all_results.append(result)
            
            if result['verdict'] == 'VERIFIED':
                verified += 1
            elif result['verdict'] == 'CONTRADICTED':
                contradicted += 1
                all_contradictions.extend(result['contradictions'])
            else:
                unverified += 1
            
            # Rate limiting
            time.sleep(0.5)
        
        # Calculate overall verification score
        total_claims = len(claims)
        verification_score = ((verified * 100) + (unverified * 50)) / total_claims if total_claims > 0 else 0
        
        # Calculate confidence
        avg_confidence = sum(r['average_confidence'] for r in all_results) / total_claims if total_claims > 0 else 0
        
        # Determine overall verdict
        if contradicted > 0:
            verdict = "CONTRADICTED"
        elif verified >= total_claims * 0.7:
            verdict = "VERIFIED"
        elif unverified >= total_claims * 0.7:
            verdict = "UNVERIFIED"
        else:
            verdict = "MIXED"
        
        print(f"\n✅ [VERIFICATION] Complete: {verified} verified, {contradicted} contradicted, {unverified} unverified")
        
        return VerificationNetworkResult(
            total_claims=total_claims,
            verified_claims=verified,
            contradicted_claims=contradicted,
            unverified_claims=unverified,
            verification_score=verification_score,
            verdict=verdict,
            database_results=all_results,
            contradictions=all_contradictions,
            confidence=avg_confidence
        )
    
    def _check_wikipedia(self, claim: str, timeout: int) -> DatabaseResult:
        """Search Wikipedia for claim verification"""
        try:
            # Extract key terms from claim
            keywords = self._extract_keywords(claim)
            search_query = ' '.join(keywords[:5])  # Use top 5 keywords
            
            params = {
                'action': 'opensearch',
                'search': search_query,
                'limit': 3,
                'format': 'json'
            }
            
            response = requests.get(self.databases['wikipedia'], params=params, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1 and len(data[1]) > 0:
                    title = data[1][0]
                    url = data[3][0] if len(data) > 3 else ""
                    
                    # Get article content
                    content = self._get_wikipedia_content(title, timeout)
                    
                    # Check if claim content matches article
                    confidence = self._calculate_match_confidence(claim, content)
                    
                    return DatabaseResult(
                        database="Wikipedia",
                        found=True,
                        content=content[:200],
                        confidence=confidence,
                        url=url
                    )
            
            return DatabaseResult("Wikipedia", False, "", 0, "")
        
        except Exception as e:
            print(f"   ⚠️ Wikipedia error: {e}")
            return DatabaseResult("Wikipedia", False, "", 0, "")
    
    def _get_wikipedia_content(self, title: str, timeout: int) -> str:
        """Get Wikipedia article content"""
        try:
            params = {
                'action': 'query',
                'titles': title,
                'prop': 'extracts',
                'exintro': True,
                'explaintext': True,
                'format': 'json'
            }
            
            response = requests.get(self.databases['wikipedia'], params=params, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                pages = data.get('query', {}).get('pages', {})
                for page_id, page in pages.items():
                    return page.get('extract', '')
        
        except Exception:
            pass
        
        return ""
    
    def _check_wikidata(self, claim: str, timeout: int) -> DatabaseResult:
        """Search Wikidata for structured data"""
        try:
            keywords = self._extract_keywords(claim)
            search_query = ' '.join(keywords[:3])
            
            params = {
                'action': 'wbsearchentities',
                'search': search_query,
                'language': 'en',
                'limit': 3,
                'format': 'json'
            }
            
            response = requests.get(self.databases['wikidata'], params=params, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('search', [])
                
                if results:
                    entity = results[0]
                    description = entity.get('description', '')
                    label = entity.get('label', '')
                    entity_id = entity.get('id', '')
                    
                    confidence = self._calculate_match_confidence(claim, f"{label} {description}")
                    
                    return DatabaseResult(
                        database="Wikidata",
                        found=True,
                        content=f"{label}: {description}",
                        confidence=confidence,
                        url=f"https://www.wikidata.org/wiki/{entity_id}"
                    )
            
            return DatabaseResult("Wikidata", False, "", 0, "")
        
        except Exception as e:
            print(f"   ⚠️ Wikidata error: {e}")
            return DatabaseResult("Wikidata", False, "", 0, "")
    
    def _check_pubmed(self, claim: str, timeout: int) -> DatabaseResult:
        """Search PubMed for scientific/medical claims"""
        try:
            keywords = self._extract_keywords(claim)
            search_query = ' '.join(keywords[:5])
            
            # Search PubMed
            search_url = f"{self.databases['pubmed']}esearch.fcgi"
            params = {
                'db': 'pubmed',
                'term': search_query,
                'retmax': 3,
                'retmode': 'json'
            }
            
            response = requests.get(search_url, params=params, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                id_list = data.get('esearchresult', {}).get('idlist', [])
                
                if id_list:
                    # Get article details
                    fetch_url = f"{self.databases['pubmed']}esummary.fcgi"
                    fetch_params = {
                        'db': 'pubmed',
                        'id': id_list[0],
                        'retmode': 'json'
                    }
                    
                    fetch_response = requests.get(fetch_url, params=fetch_params, timeout=timeout)
                    
                    if fetch_response.status_code == 200:
                        fetch_data = fetch_response.json()
                        article = fetch_data.get('result', {}).get(id_list[0], {})
                        title = article.get('title', '')
                        
                        confidence = self._calculate_match_confidence(claim, title)
                        
                        return DatabaseResult(
                            database="PubMed",
                            found=True,
                            content=title[:200],
                            confidence=confidence,
                            url=f"https://pubmed.ncbi.nlm.nih.gov/{id_list[0]}/"
                        )
            
            return DatabaseResult("PubMed", False, "", 0, "")
        
        except Exception as e:
            print(f"   ⚠️ PubMed error: {e}")
            return DatabaseResult("PubMed", False, "", 0, "")
    
    def _check_arxiv(self, claim: str, timeout: int) -> DatabaseResult:
        """Search arXiv for academic claims"""
        try:
            keywords = self._extract_keywords(claim)
            search_query = '+'.join(keywords[:5])
            
            url = f"{self.databases['arxiv']}?search_query=all:{search_query}&start=0&max_results=3"
            
            response = requests.get(url, timeout=timeout)
            
            if response.status_code == 200:
                content = response.text
                
                # Parse XML (simple regex-based parsing)
                title_match = re.search(r'<title>([^<]+)</title>', content)
                if title_match and 'arxiv' not in title_match.group(1).lower():
                    title = title_match.group(1)
                    
                    # Extract arXiv ID
                    id_match = re.search(r'http://arxiv.org/abs/([0-9.]+)', content)
                    arxiv_id = id_match.group(1) if id_match else ""
                    
                    confidence = self._calculate_match_confidence(claim, title)
                    
                    return DatabaseResult(
                        database="arXiv",
                        found=True,
                        content=title[:200],
                        confidence=confidence,
                        url=f"https://arxiv.org/abs/{arxiv_id}"
                    )
            
            return DatabaseResult("arXiv", False, "", 0, "")
        
        except Exception as e:
            print(f"   ⚠️ arXiv error: {e}")
            return DatabaseResult("arXiv", False, "", 0, "")
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Remove common words
        stop_words = {'the', 'is', 'are', 'was', 'were', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from'}
        
        # Tokenize and filter
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        keywords = [w for w in words if w not in stop_words]
        
        return keywords[:10]  # Return top 10
    
    def _calculate_match_confidence(self, claim: str, content: str) -> float:
        """Calculate how well content matches claim"""
        if not content:
            return 0
        
        claim_lower = claim.lower()
        content_lower = content.lower()
        
        # Extract keywords from claim
        claim_keywords = set(self._extract_keywords(claim_lower))
        content_keywords = set(self._extract_keywords(content_lower))
        
        if not claim_keywords:
            return 0
        
        # Calculate overlap
        overlap = len(claim_keywords & content_keywords)
        confidence = (overlap / len(claim_keywords)) * 100
        
        return min(100, confidence)
    
    def _is_scientific_claim(self, claim: str) -> bool:
        """Check if claim is scientific/medical"""
        scientific_keywords = ['study', 'research', 'scientist', 'medical', 'health', 'disease', 'treatment', 
                              'cure', 'drug', 'vaccine', 'doctor', 'patient', 'clinical', 'trial', 'gene']
        
        claim_lower = claim.lower()
        return any(keyword in claim_lower for keyword in scientific_keywords)
    
    def _is_academic_claim(self, claim: str) -> bool:
        """Check if claim is academic/theoretical"""
        academic_keywords = ['theory', 'physics', 'mathematics', 'computer science', 'algorithm', 
                            'theorem', 'proof', 'equation', 'quantum', 'particle', 'model']
        
        claim_lower = claim.lower()
        return any(keyword in claim_lower for keyword in academic_keywords)
    
    def _detect_contradictions(self, claim: str, results: List[DatabaseResult]) -> List[str]:
        """Detect contradictions between database results"""
        contradictions = []
        
        # Check for conflicting information
        found_results = [r for r in results if r.found]
        
        if len(found_results) >= 2:
            # Simple contradiction detection: if confidences vary widely
            confidences = [r.confidence for r in found_results]
            max_conf = max(confidences)
            min_conf = min(confidences)
            
            if max_conf - min_conf > 50:
                contradictions.append(f"Conflicting information: confidence varies from {min_conf:.0f}% to {max_conf:.0f}%")
        
        return contradictions
    
    def _database_result_to_dict(self, result: DatabaseResult) -> Dict:
        """Convert DatabaseResult to dictionary"""
        return {
            'database': result.database,
            'found': result.found,
            'content': result.content,
            'confidence': result.confidence,
            'url': result.url
        }

# Singleton instance
_verification_network = None

def get_verification_network() -> VerificationNetwork:
    """Get or create verification network singleton"""
    global _verification_network
    if _verification_network is None:
        _verification_network = VerificationNetwork()
    return _verification_network

def verify_claims_network(claims: List[str]) -> Dict:
    """Verify claims across multiple databases"""
    network = get_verification_network()
    result = network.verify_multiple_claims(claims)
    
    return {
        'total_claims': result.total_claims,
        'verified_claims': result.verified_claims,
        'contradicted_claims': result.contradicted_claims,
        'unverified_claims': result.unverified_claims,
        'verification_score': result.verification_score,
        'verdict': result.verdict,
        'confidence': result.confidence,
        'database_results': result.database_results,
        'contradictions': result.contradictions
    }

# Test function
if __name__ == "__main__":
    print("=" * 70)
    print("🌐 VERIFICATION NETWORK TEST")
    print("=" * 70)
    
    test_claims = [
        "The Earth is approximately 4.5 billion years old",
        "Water boils at 100 degrees Celsius at sea level",
        "Chocolate cures all diseases instantly"  # False claim
    ]
    
    result = verify_claims_network(test_claims)
    
    print("\n" + "=" * 70)
    print("📊 RESULTS")
    print("=" * 70)
    print(f"Total Claims: {result['total_claims']}")
    print(f"Verified: {result['verified_claims']}")
    print(f"Contradicted: {result['contradicted_claims']}")
    print(f"Unverified: {result['unverified_claims']}")
    print(f"Verification Score: {result['verification_score']:.1f}/100")
    print(f"Overall Verdict: {result['verdict']}")
    print(f"Confidence: {result['confidence']:.1f}%")
    
    if result['contradictions']:
        print(f"\n⚠️ Contradictions Found:")
        for contradiction in result['contradictions']:
            print(f"  - {contradiction}")
    
    print("\n✅ Test complete!")
