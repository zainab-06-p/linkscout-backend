"""
LinkScout End-to-End Test Suite
Tests accuracy, false positive rate, and recall
"""

import requests
import json
import time
from datetime import datetime
from typing import List, Dict

# Configuration
SERVER_URL = "http://localhost:5000"
RESULTS_FILE = "test_results_linkscout.json"

# Test samples - YOU NEED TO ADD REAL URLs
TEST_SAMPLES = [
    # ========================================
    # FAKE NEWS SAMPLES (Expected: FAKE NEWS or SUSPICIOUS)
    # ========================================
    {
        "id": 1,
        "url": "https://example-fake-news.com/article1",  # ⚠️ REPLACE WITH REAL FAKE NEWS URL
        "content": "BREAKING: Scientists PROVE that vaccines contain microchips planted by Bill Gates to control population!",
        "expected_verdict": "FAKE NEWS",
        "expected_range": (70, 100),
        "category": "COVID",
        "description": "Bill Gates microchip conspiracy"
    },
    {
        "id": 2,
        "url": "https://example-fake-news.com/article2",  # ⚠️ REPLACE WITH REAL FAKE NEWS URL
        "content": "SHOCKING: 5G towers are spreading coronavirus! Government hiding truth from citizens!",
        "expected_verdict": "FAKE NEWS",
        "expected_range": (70, 100),
        "category": "COVID",
        "description": "5G coronavirus conspiracy"
    },
    {
        "id": 3,
        "url": "https://example-fake-news.com/article3",  # ⚠️ REPLACE WITH REAL FAKE NEWS URL
        "content": "ELECTION FRAUD EXPOSED: Dominion machines rigged, millions of dead people voted illegally!",
        "expected_verdict": "FAKE NEWS",
        "expected_range": (70, 100),
        "category": "Politics",
        "description": "Election fraud conspiracy"
    },
    {
        "id": 4,
        "url": "https://example-fake-news.com/article4",  # ⚠️ REPLACE WITH REAL FAKE NEWS URL
        "content": "Climate change is a HOAX! Scientists admit they fabricated all data to get funding!",
        "expected_verdict": "FAKE NEWS",
        "expected_range": (70, 100),
        "category": "Climate",
        "description": "Climate denial"
    },
    {
        "id": 5,
        "url": "https://example-fake-news.com/article5",  # ⚠️ REPLACE WITH REAL FAKE NEWS URL
        "content": "NASA finally admits moon landing was FAKED in Hollywood studio by Stanley Kubrick!",
        "expected_verdict": "FAKE NEWS",
        "expected_range": (70, 100),
        "category": "Science",
        "description": "Moon landing conspiracy"
    },
    
    # ========================================
    # REAL NEWS SAMPLES (Expected: APPEARS CREDIBLE)
    # ========================================
    {
        "id": 11,
        "url": "https://www.bbc.com/news",  # ⚠️ REPLACE WITH SPECIFIC BBC ARTICLE
        "content": "The World Health Organization reported today that global vaccination efforts have reached 70% coverage in developed nations. Experts say this marks significant progress in pandemic response.",
        "expected_verdict": "APPEARS CREDIBLE",
        "expected_range": (0, 40),
        "category": "Health",
        "description": "Legitimate health news"
    },
    {
        "id": 12,
        "url": "https://www.reuters.com/world",  # ⚠️ REPLACE WITH SPECIFIC REUTERS ARTICLE
        "content": "The United Nations Security Council met today to discuss climate change initiatives. Member states presented updated emission reduction targets for 2030.",
        "expected_verdict": "APPEARS CREDIBLE",
        "expected_range": (0, 40),
        "category": "Climate",
        "description": "Legitimate climate news"
    },
    {
        "id": 13,
        "url": "https://apnews.com",  # ⚠️ REPLACE WITH SPECIFIC AP ARTICLE
        "content": "Scientists at MIT published research in Nature journal describing advances in renewable energy storage technology. The peer-reviewed study shows promising results.",
        "expected_verdict": "APPEARS CREDIBLE",
        "expected_range": (0, 40),
        "category": "Science",
        "description": "Legitimate science news"
    },
    {
        "id": 14,
        "url": "https://www.nature.com/articles",  # ⚠️ REPLACE WITH SPECIFIC NATURE ARTICLE
        "content": "A new study published in The Lancet medical journal examines the long-term effects of COVID-19. Researchers analyzed data from 10,000 patients over two years.",
        "expected_verdict": "APPEARS CREDIBLE",
        "expected_range": (0, 40),
        "category": "Health",
        "description": "Legitimate medical research"
    },
    {
        "id": 15,
        "url": "https://www.scientificamerican.com",  # ⚠️ REPLACE WITH SPECIFIC ARTICLE
        "content": "Astronomers using the James Webb Space Telescope discovered distant galaxies formed shortly after the Big Bang. The findings were published in the Astrophysical Journal.",
        "expected_verdict": "APPEARS CREDIBLE",
        "expected_range": (0, 40),
        "category": "Science",
        "description": "Legitimate astronomy news"
    },
    
    # ADD MORE SAMPLES TO REACH 35 TOTAL
    # 15 more fake news samples
    # 15 more real news samples
]

def analyze_content(content: str, url: str = "") -> Dict:
    """Send content to LinkScout for analysis"""
    try:
        response = requests.post(
            f"{SERVER_URL}/detect",
            json={"content": content, "url": url},
            timeout=60
        )
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def run_tests() -> Dict:
    """Run all test samples and calculate metrics"""
    print("="*70)
    print("LINKSCOUT TEST SUITE")
    print("="*70)
    print(f"Server: {SERVER_URL}")
    print(f"Total samples: {len(TEST_SAMPLES)}")
    print("="*70)
    
    results = []
    correct = 0
    false_positives = 0
    false_negatives = 0
    true_positives = 0
    true_negatives = 0
    
    for i, sample in enumerate(TEST_SAMPLES, 1):
        print(f"\n[{i}/{len(TEST_SAMPLES)}] Testing: {sample['description']}")
        print(f"   URL: {sample['url']}")
        print(f"   Expected: {sample['expected_verdict']}")
        
        # Analyze
        analysis = analyze_content(sample['content'], sample['url'])
        
        if not analysis.get('success'):
            print(f"   ❌ ERROR: {analysis.get('error', 'Unknown error')}")
            results.append({
                "sample": sample,
                "analysis": None,
                "status": "error"
            })
            continue
        
        # Extract results
        actual_verdict = analysis.get('verdict', '')
        actual_percentage = analysis.get('misinformation_percentage', 0)
        
        print(f"   Actual: {actual_verdict} ({actual_percentage}%)")
        
        # Check if correct
        is_correct = False
        is_true_positive = False
        is_true_negative = False
        is_false_positive = False
        is_false_negative = False
        
        if sample['expected_verdict'] == "FAKE NEWS":
            # This is actually fake news
            if actual_verdict == "FAKE NEWS":
                is_correct = True
                is_true_positive = True
                true_positives += 1
            else:
                is_false_negative = True
                false_negatives += 1
        else:
            # This is actually real news
            if actual_verdict == "APPEARS CREDIBLE":
                is_correct = True
                is_true_negative = True
                true_negatives += 1
            else:
                is_false_positive = True
                false_positives += 1
        
        if is_correct:
            correct += 1
            print(f"   ✅ CORRECT")
        else:
            print(f"   ❌ INCORRECT")
        
        results.append({
            "sample": sample,
            "analysis": {
                "verdict": actual_verdict,
                "percentage": actual_percentage
            },
            "is_correct": is_correct,
            "is_true_positive": is_true_positive,
            "is_true_negative": is_true_negative,
            "is_false_positive": is_false_positive,
            "is_false_negative": is_false_negative
        })
        
        # Small delay to avoid overwhelming server
        time.sleep(1)
    
    # Calculate metrics
    total = len(TEST_SAMPLES)
    accuracy = (correct / total * 100) if total > 0 else 0
    
    # Count actual fake/real news
    actual_fake_count = len([s for s in TEST_SAMPLES if s['expected_verdict'] == "FAKE NEWS"])
    actual_real_count = total - actual_fake_count
    
    # False positive rate = FP / (FP + TN)
    fp_rate = (false_positives / (false_positives + true_negatives) * 100) if (false_positives + true_negatives) > 0 else 0
    
    # Recall (sensitivity) = TP / (TP + FN)
    recall = (true_positives / (true_positives + false_negatives) * 100) if (true_positives + false_negatives) > 0 else 0
    
    # Precision = TP / (TP + FP)
    precision = (true_positives / (true_positives + false_positives) * 100) if (true_positives + false_positives) > 0 else 0
    
    # Print summary
    print("\n" + "="*70)
    print("TEST RESULTS SUMMARY")
    print("="*70)
    print(f"Total Samples: {total}")
    print(f"  - Fake News: {actual_fake_count}")
    print(f"  - Real News: {actual_real_count}")
    print("\n📊 METRICS:")
    print(f"  Accuracy: {accuracy:.2f}% (Target: 75-85%)")
    print(f"  False Positive Rate: {fp_rate:.2f}% (Target: <2%)")
    print(f"  Recall: {recall:.2f}% (Target: 60-75%)")
    print(f"  Precision: {precision:.2f}%")
    print(f"\n📈 CONFUSION MATRIX:")
    print(f"  True Positives: {true_positives} (correctly identified fake news)")
    print(f"  True Negatives: {true_negatives} (correctly identified real news)")
    print(f"  False Positives: {false_positives} (real news marked as fake)")
    print(f"  False Negatives: {false_negatives} (fake news marked as real)")
    
    # Status indicators
    print(f"\n🎯 TARGET STATUS:")
    print(f"  Accuracy: {'✅ PASS' if accuracy >= 75 else '❌ FAIL'}")
    print(f"  False Positive Rate: {'✅ PASS' if fp_rate < 2 else '❌ FAIL'}")
    print(f"  Recall: {'✅ PASS' if recall >= 60 else '❌ FAIL'}")
    
    print("="*70)
    
    # Save results
    summary = {
        "timestamp": datetime.now().isoformat(),
        "overall_metrics": {
            "total_samples": total,
            "fake_news_samples": actual_fake_count,
            "real_news_samples": actual_real_count,
            "accuracy": accuracy,
            "false_positive_rate": fp_rate,
            "recall": recall,
            "precision": precision,
            "true_positives": true_positives,
            "true_negatives": true_negatives,
            "false_positives": false_positives,
            "false_negatives": false_negatives
        },
        "detailed_results": results
    }
    
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {RESULTS_FILE}")
    
    return summary

if __name__ == "__main__":
    print("\n⚠️  IMPORTANT: This test suite uses example URLs.")
    print("⚠️  Please add real fake news and real news URLs to TEST_SAMPLES.")
    print("\nPress CTRL+C to cancel, or wait 5 seconds to continue with examples...\n")
    
    try:
        time.sleep(5)
    except KeyboardInterrupt:
        print("\n\nTest cancelled. Please update TEST_SAMPLES with real URLs.")
        exit(0)
    
    run_tests()
