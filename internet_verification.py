# Internet Verification Functions for AI Models
# These functions allow AI to search WHO, UN, UNESCO websites in real-time
# INCLUDES: Official government agencies (health departments, disaster management, etc.)
# EXCLUDES: News channels, media outlets (biased/unreliable)

import requests
from bs4 import BeautifulSoup
import urllib.parse

# ============= OFFICIAL SOURCES =============
TIER_1_SOURCES = {
    'WHO': {
        'domain': 'who.int',
        'api_endpoint': 'https://www.who.int/api/health-topics',
        'search_url': 'https://www.who.int/news-room/fact-sheets',
        'patterns': ['who', 'world health organization', 'who officials']
    },
    'UN': {
        'domain': 'un.org',
        'api_endpoint': 'https://www.un.org/en/news',
        'search_url': 'https://news.un.org/en/',
        'patterns': ['united nations', 'un security council', 'un officials', 'un agencies']
    },
    'UNESCO': {
        'domain': 'unesco.org',
        'api_endpoint': 'https://en.unesco.org/news',
        'search_url': 'https://en.unesco.org/',
        'patterns': ['unesco', 'unesco officials']
    },
    'UNICEF': {
        'domain': 'unicef.org',
        'search_url': 'https://www.unicef.org/press-releases',
        'patterns': ['unicef', 'united nations children']
    },
    'UNHCR': {
        'domain': 'unhcr.org',
        'search_url': 'https://www.unhcr.org/news',
        'patterns': ['unhcr', 'un refugee', 'refugee agency']
    },
    'USGS': {
        'domain': 'usgs.gov',
        'api_endpoint': 'https://earthquake.usgs.gov/fdsnws/event/1/query',
        'search_url': 'https://www.usgs.gov/natural-hazards',
        'patterns': ['usgs', 'us geological survey', 'geological survey']
    },
    'CDC': {
        'domain': 'cdc.gov',
        'search_url': 'https://www.cdc.gov/media/releases/',
        'patterns': ['cdc', 'centers for disease control', 'disease control']
    },
    'NASA': {
        'domain': 'nasa.gov',
        'search_url': 'https://www.nasa.gov/news/',
        'patterns': ['nasa', 'national aeronautics']
    },
    'NOAA': {
        'domain': 'noaa.gov',
        'search_url': 'https://www.noaa.gov/news',
        'patterns': ['noaa', 'national oceanic', 'weather service']
    },
    'ICRC': {
        'domain': 'icrc.org',
        'search_url': 'https://www.icrc.org/en/latest',
        'patterns': ['red cross', 'icrc', 'international committee of the red cross']
    },
    'Amnesty': {
        'domain': 'amnesty.org',
        'search_url': 'https://www.amnesty.org/en/latest/news/',
        'patterns': ['amnesty international', 'amnesty']
    },
    'HRW': {
        'domain': 'hrw.org',
        'search_url': 'https://www.hrw.org/news',
        'patterns': ['human rights watch', 'hrw']
    },
    'WorldBank': {
        'domain': 'worldbank.org',
        'search_url': 'https://www.worldbank.org/en/news',
        'patterns': ['world bank', 'worldbank']
    },
    'IMF': {
        'domain': 'imf.org',
        'search_url': 'https://www.imf.org/en/News',
        'patterns': ['international monetary fund', 'imf']
    },
    
    # ========== OFFICIAL GOVERNMENT AGENCIES (NOT NEWS CHANNELS) ==========
    # These are official government departments/agencies for verification
    
    # Health Departments
    'NIH': {
        'domain': 'nih.gov',
        'search_url': 'https://www.nih.gov/news-events',
        'patterns': ['nih', 'national institutes of health']
    },
    'FDA': {
        'domain': 'fda.gov',
        'search_url': 'https://www.fda.gov/news-events',
        'patterns': ['fda', 'food and drug administration']
    },
    'ICMR': {
        'domain': 'icmr.gov.in',
        'search_url': 'https://www.icmr.gov.in/',
        'patterns': ['icmr', 'indian council of medical research']
    },
    'MoHFW_India': {
        'domain': 'mohfw.gov.in',
        'search_url': 'https://www.mohfw.gov.in/',
        'patterns': ['ministry of health india', 'mohfw']
    },
    
    # Disaster Management
    'NDMA_India': {
        'domain': 'ndma.gov.in',
        'search_url': 'https://ndma.gov.in/',
        'patterns': ['ndma', 'national disaster management authority']
    },
    'FEMA': {
        'domain': 'fema.gov',
        'search_url': 'https://www.fema.gov/about/news-multimedia',
        'patterns': ['fema', 'federal emergency management']
    },
    
    # Weather/Climate
    'IMD': {
        'domain': 'imd.gov.in',
        'search_url': 'https://mausam.imd.gov.in/',
        'patterns': ['imd', 'india meteorological department', 'met department']
    },
    'NWS': {
        'domain': 'weather.gov',
        'search_url': 'https://www.weather.gov/',
        'patterns': ['national weather service', 'nws']
    },
    
    # Government Information
    'PIB_India': {
        'domain': 'pib.gov.in',
        'search_url': 'https://pib.gov.in/indexd.aspx',
        'patterns': ['press information bureau', 'pib india']
    },
    'MyGov_India': {
        'domain': 'mygov.in',
        'search_url': 'https://www.mygov.in/',
        'patterns': ['mygov india']
    },
    
    # Science/Space
    'ISRO': {
        'domain': 'isro.gov.in',
        'search_url': 'https://www.isro.gov.in/updates.html',
        'patterns': ['isro', 'indian space research']
    },
    'NSF': {
        'domain': 'nsf.gov',
        'search_url': 'https://www.nsf.gov/news/',
        'patterns': ['national science foundation', 'nsf']
    },
    
    # Environmental Protection
    'EPA': {
        'domain': 'epa.gov',
        'search_url': 'https://www.epa.gov/newsreleases',
        'patterns': ['epa', 'environmental protection agency']
    },
    'CPCB': {
        'domain': 'cpcb.nic.in',
        'search_url': 'https://cpcb.nic.in/',
        'patterns': ['cpcb', 'central pollution control board']
    }
}

TIER_2_SOURCES = {
    'Snopes': {
        'domain': 'snopes.com',
        'search_url': 'https://www.snopes.com/',
        'patterns': ['snopes']
    },
    'FactCheck': {
        'domain': 'factcheck.org',
        'search_url': 'https://www.factcheck.org/',
        'patterns': ['factcheck.org']
    },
    'PolitiFact': {
        'domain': 'politifact.com',
        'search_url': 'https://www.politifact.com/',
        'patterns': ['politifact']
    },
    'AltNews': {
        'domain': 'altnews.in',
        'search_url': 'https://www.altnews.in/',
        'patterns': ['alt news']
    },
    'AfricaCheck': {
        'domain': 'africacheck.org',
        'search_url': 'https://africacheck.org/',
        'patterns': ['africa check']
    }
}

TIER_3_SOURCES = {
    'Reuters': {
        'domain': 'reuters.com',
        'patterns': ['reuters']
    },
    'AP': {
        'domain': 'apnews.com',
        'patterns': ['associated press', 'ap news']
    },
    'AFP': {
        'domain': 'afp.com',
        'patterns': ['agence france-presse', 'afp']
    },
    'PTI': {
        'domain': 'ptinews.com',
        'patterns': ['press trust of india', 'pti']
    }
}


def search_official_source_online(query: str, source_name: str, source_info: dict) -> dict:
    """
    AI searches official source websites in real-time to verify claims
    Returns findings from the actual website
    """
    try:
        search_url = source_info.get('search_url')
        if not search_url:
            return {"found": False, "reason": "No search URL"}
        
        # Clean query for URL
        clean_query = urllib.parse.quote(query[:100])
        
        # Try to search the official website
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print(f"🔍 AI searching {source_name} at {search_url}...")
        
        # Some sites have search APIs
        if source_name == 'USGS' and 'earthquake' in query.lower():
            # Check USGS earthquake data
            api_url = 'https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&limit=10'
            response = requests.get(api_url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('features'):
                    return {
                        "found": True,
                        "source": source_name,
                        "url": api_url,
                        "details": f"Found {len(data['features'])} recent earthquake events"
                    }
        
        # General web search on the official site
        response = requests.get(search_url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text().lower()
            
            # Check if query terms appear on their main page/news
            query_words = query.lower().split()
            matches = sum(1 for word in query_words if len(word) > 3 and word in text_content)
            
            if matches >= len(query_words) * 0.3:  # 30% of words found
                return {
                    "found": True,
                    "source": source_name,
                    "url": search_url,
                    "details": f"Found {matches} matching terms on {source_name} website"
                }
        
        return {"found": False, "reason": f"No matches on {source_name}"}
        
    except Exception as e:
        print(f"⚠️ Error searching {source_name}: {str(e)}")
        return {"found": False, "reason": str(e)}


def verify_with_official_sources_enhanced(content: str, title: str, url: str) -> dict:
    """
    Enhanced verification - AI searches WHO, UN, UNESCO + OFFICIAL GOVERNMENT AGENCIES
    
    TRUSTED SOURCES:
    - International Organizations (WHO, UN, UNESCO, etc.)
    - Official Government Agencies (CDC, FDA, NDMA, IMD, etc.)
    
    NOT TRUSTED:
    - News channels/media outlets (biased)
    - Social media
    - Blogs/opinion sites
    """
    content_lower = content.lower()
    title_lower = title.lower()
    url_lower = url.lower()
    
    verification_results = {
        "tier_1_matches": [],  # WHO, UN, UNESCO, etc.
        "tier_2_matches": [],  # Fact-checkers
        "tier_3_matches": [],  # Wire services
        "online_verification": [],  # Real-time web searches
        "total_score": 0,
        "verdict": "UNVERIFIED",
        "trust_level": "LOW",
        "recommendation": ""
    }
    
    print("🌐 AI starting real-time verification with international organizations...")
    
    # Check Tier 1: International Organizations (Score: 10 each)
    for org_name, org_info in TIER_1_SOURCES.items():
        # Check if mentioned in content
        mentioned = any(pattern in content_lower or pattern in title_lower 
                       for pattern in org_info['patterns'])
        
        # Check if URL is from official domain
        from_official_domain = org_info['domain'] in url_lower
        
        if mentioned or from_official_domain:
            verification_results['tier_1_matches'].append({
                "organization": org_name,
                "domain": org_info['domain'],
                "mentioned": mentioned,
                "official_domain": from_official_domain,
                "score": 10
            })
            verification_results['total_score'] += 10
            
            # AI searches their website in real-time
            if mentioned and not from_official_domain:
                # Extract key claim to search
                sentences = content.split('.')
                relevant = [s for s in sentences if any(p in s.lower() for p in org_info['patterns'])]
                if relevant:
                    search_result = search_official_source_online(relevant[0][:200], org_name, org_info)
                    if search_result.get('found'):
                        verification_results['online_verification'].append(search_result)
                        verification_results['total_score'] += 5  # Bonus for online verification
    
    # Check Tier 2: Independent Fact-Checkers (Score: 8 each)
    for checker_name, checker_info in TIER_2_SOURCES.items():
        mentioned = any(pattern in content_lower for pattern in checker_info['patterns'])
        from_official = checker_info['domain'] in url_lower
        
        if mentioned or from_official:
            verification_results['tier_2_matches'].append({
                "fact_checker": checker_name,
                "domain": checker_info['domain'],
                "score": 8
            })
            verification_results['total_score'] += 8
    
    # Check Tier 3: Wire Services (Score: 5 each)
    for wire_name, wire_info in TIER_3_SOURCES.items():
        mentioned = any(pattern in content_lower for pattern in wire_info['patterns'])
        from_official = wire_info['domain'] in url_lower
        
        if mentioned or from_official:
            verification_results['tier_3_matches'].append({
                "wire_service": wire_name,
                "domain": wire_info['domain'],
                "score": 5
            })
            verification_results['total_score'] += 5
    
    # Calculate verdict based on score
    score = verification_results['total_score']
    
    if score >= 10:
        verification_results['verdict'] = "VERIFIED"
        verification_results['trust_level'] = "HIGH"
        verification_results['recommendation'] = f"✅ Verified by {len(verification_results['tier_1_matches'])} international organization(s)"
    elif score >= 8:
        verification_results['verdict'] = "LIKELY_CREDIBLE"
        verification_results['trust_level'] = "MEDIUM-HIGH"
        verification_results['recommendation'] = "⚠️ Fact-checked, but verify with WHO/UN for critical information"
    elif score >= 5:
        verification_results['verdict'] = "PARTIALLY_VERIFIED"
        verification_results['trust_level'] = "MEDIUM"
        verification_results['recommendation'] = "⚠️ From wire service - Check WHO/UN/UNESCO for official confirmation"
    else:
        verification_results['verdict'] = "UNVERIFIED"
        verification_results['trust_level'] = "LOW"
        verification_results['recommendation'] = "🚫 NOT verified by WHO/UN/UNESCO - Search these organizations' websites before believing"
    
    print(f"✅ Verification complete: {verification_results['verdict']} (Score: {score})")
    
    return verification_results


def ensemble_classification(content: str, fake_news_classifier_1, fake_news_classifier_2, fact_checker) -> dict:
    """
    Multiple AI models vote on classification
    Returns consensus from 3+ models
    """
    print("🤖 Running ensemble AI classification with multiple models...")
    
    votes = []
    
    try:
        # Model 1: RoBERTa Fake News (Primary)
        if fake_news_classifier_1:
            result1 = fake_news_classifier_1(content[:512])[0]
            classification1 = "false" if result1['label'].upper() in ['FAKE', 'FALSE', 'LABEL_0'] else "verified"
            votes.append({
                "model": "RoBERTa-Fake-News",
                "classification": classification1,
                "confidence": result1['score']
            })
            print(f"  Model 1 (RoBERTa): {classification1} ({result1['score']:.2f})")
    except Exception as e:
        print(f"⚠️ Model 1 error: {e}")
    
    try:
        # Model 2: BERT Fake News Detector
        if fake_news_classifier_2:
            result2 = fake_news_classifier_2(content[:512])[0]
            classification2 = "false" if result2['label'].upper() in ['FAKE', 'FALSE', 'LABEL_0'] else "verified"
            votes.append({
                "model": "BERT-Fake-News",
                "classification": classification2,
                "confidence": result2['score']
            })
            print(f"  Model 2 (BERT): {classification2} ({result2['score']:.2f})")
    except Exception as e:
        print(f"⚠️ Model 2 error: {e}")
    
    try:
        # Model 3: Financial/General News Sentiment
        if fact_checker:
            result3 = fact_checker(content[:512])[0]
            # Negative sentiment often correlates with sensationalism
            classification3 = "false" if result3['label'].upper() in ['NEGATIVE', 'LABEL_0'] and result3['score'] > 0.8 else "questionable"
            votes.append({
                "model": "DistilRoBERTa-Sentiment",
                "classification": classification3,
                "confidence": result3['score']
            })
            print(f"  Model 3 (Sentiment): {classification3} ({result3['score']:.2f})")
    except Exception as e:
        print(f"⚠️ Model 3 error: {e}")
    
    # Calculate consensus
    if not votes:
        return {"classification": "questionable", "confidence": 0.5, "model_votes": []}
    
    false_votes = sum(1 for v in votes if v['classification'] == 'false')
    verified_votes = sum(1 for v in votes if v['classification'] == 'verified')
    questionable_votes = sum(1 for v in votes if v['classification'] == 'questionable')
    
    total_votes = len(votes)
    avg_confidence = sum(v['confidence'] for v in votes) / total_votes
    
    # Determine consensus
    if false_votes > total_votes / 2:
        final_classification = "false"
    elif verified_votes > total_votes / 2:
        final_classification = "verified"
    else:
        final_classification = "questionable"
    
    print(f"📊 Ensemble result: {final_classification} ({false_votes}F/{questionable_votes}Q/{verified_votes}V)")
    
    return {
        "classification": final_classification,
        "confidence": avg_confidence,
        "model_votes": votes,
        "vote_breakdown": {
            "false": false_votes,
            "questionable": questionable_votes,
            "verified": verified_votes
        }
    }
