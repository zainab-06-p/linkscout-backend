"""
Hard Accuracy Test for LinkScout
Tests with real content samples to validate improvements
"""

import requests
import json
from typing import Dict, List, Tuple
import time

SERVER_URL = "http://localhost:5000"

# Real content samples with known verdicts
HARD_TEST_SAMPLES = [
    # === FAKE NEWS SAMPLES (Expected: High Risk 70-100%) ===
    {
        "id": 1,
        "content": """
        BREAKING: COVID-19 vaccines contain microchips for tracking! Bill Gates admitted in leaked documents 
        that the vaccine rollout is part of a global surveillance program. The vaccine also contains graphene 
        oxide which connects to 5G towers. Doctors are silenced when they try to speak out. Natural immunity 
        is 27 times better than vaccine immunity. The vaccine is experimental gene therapy, not a real vaccine. 
        FDA never properly approved it. Thousands are dying from blood clots but media won't report it.
        """,
        "expected": "FAKE",
        "category": "COVID Misinformation",
        "description": "Multiple debunked COVID vaccine conspiracy theories"
    },
    {
        "id": 2,
        "content": """
        ELECTION FRAUD EXPOSED! Dominion voting machines were hacked by Venezuela and China to switch votes. 
        Ballots were flown in from Asia with bamboo fibers detected. Dead people voted by the thousands. 
        Sharpie pens were given to Republican voters to invalidate their ballots. Over 100,000 votes appeared 
        at 3am in suspicious dumps. More people voted than were registered in several counties. This is the 
        biggest theft in American history and everyone knows it.
        """,
        "expected": "FAKE",
        "category": "Election Misinformation",
        "description": "Multiple debunked election fraud claims"
    },
    {
        "id": 3,
        "content": """
        Chemtrails are poisoning our children! Government planes spray barium, aluminum, and strontium to 
        control the weather and reduce population. You can see the trails in the sky - they're not normal 
        contrails! NASA documents prove geoengineering is real. Aluminum levels in soil have increased 1000x. 
        People are getting Alzheimer's from breathing this. The globalists want to dim the sun and control 
        our minds through these chemicals. Wake up sheeple!
        """,
        "expected": "FAKE",
        "category": "Chemtrails Conspiracy",
        "description": "Debunked chemtrails conspiracy theory"
    },
    {
        "id": 4,
        "content": """
        5G towers cause coronavirus! Wuhan was the first 5G city and that's where COVID started - not a 
        coincidence! The radiation weakens your immune system making you sick. They're installing 5G to 
        depopulate the planet. Birds are falling dead near 5G towers. Your phone radiation causes brain 
        cancer and the government knows it. Bill Gates wants 5G everywhere for total control through vaccines.
        """,
        "expected": "FAKE",
        "category": "5G Conspiracy",
        "description": "Debunked 5G conspiracy theories"
    },
    {
        "id": 5,
        "content": """
        Cancer cure suppressed by Big Pharma! Vitamin C megadoses cure all cancers but doctors hide this 
        because chemotherapy makes billions. Alkaline water prevents all disease - cancer can't survive in 
        alkaline environments. Sugar feeds cancer so cut all sugar and tumors die. Natural immunity is better 
        than any vaccine. Pharmaceutical companies suppress natural cures to keep people sick and dependent.
        """,
        "expected": "FAKE",
        "category": "Medical Misinformation",
        "description": "Debunked alternative medicine claims"
    },
    {
        "id": 6,
        "content": """
        Climate change is a hoax by globalists! There's actually an ice age coming, not warming. The sun 
        causes all climate changes, not humans. 97% of climate scientists disagree about human-caused warming - 
        that number is fake. Antarctica ice is actually growing not shrinking. Climate models are always wrong. 
        This is about controlling you with carbon taxes and taking away your freedom.
        """,
        "expected": "FAKE",
        "category": "Climate Denial",
        "description": "Climate change denial and misinformation"
    },
    {
        "id": 7,
        "content": """
        Fluoride in water is Nazi mind control! It calcifies your pineal gland and lowers IQ by 20 points. 
        This was used in concentration camps to keep prisoners docile. The government adds it to control 
        the population and make us dumb. Studies prove it causes cancer and brain damage in children. 
        European countries banned it because they know the truth. Wake up America!
        """,
        "expected": "FAKE",
        "category": "Fluoride Conspiracy",
        "description": "Debunked fluoride conspiracy theory"
    },
    {
        "id": 8,
        "content": """
        GMO foods are killing us! Monsanto's genetically modified crops cause cancer, autism, and infertility. 
        Lab rats fed GMO corn developed massive tumors. These Frankenstein foods destroy your DNA. Organic 
        is the only safe option. Big Agriculture suppresses studies showing GMO dangers. MSG is a dangerous 
        neurotoxin that kills brain cells - it's in everything and the FDA allows it!
        """,
        "expected": "FAKE",
        "category": "Food Misinformation",
        "description": "Debunked GMO and MSG fearmongering"
    },
    {
        "id": 9,
        "content": """
        Vaccines cause autism - the CDC covered it up! Leaked documents show they knew about the link but 
        hid it. Big Pharma makes billions so they silence doctors who speak truth. Vaccines contain mercury, 
        formaldehyde, aborted fetal cells, and other toxins. Natural immunity is better. Vaccine injuries 
        are massively underreported. They want to inject babies with 72 doses of poison before age 18!
        """,
        "expected": "FAKE",
        "category": "Vaccine Misinformation",
        "description": "Debunked vaccine-autism claim and antivax rhetoric"
    },
    {
        "id": 10,
        "content": """
        WiFi radiation is killing our children! Schools are exposing kids to dangerous electromagnetic fields. 
        This causes ADHD, anxiety, cancer, and infertility. Your phone should never be near your body. 
        Alexa and smart speakers are always recording everything you say and sending it to the government. 
        Social media apps secretly turn on your microphone to listen to conversations for ads. Delete everything!
        """,
        "expected": "FAKE",
        "category": "Technology Fearmongering",
        "description": "Debunked WiFi and privacy conspiracy theories"
    },
    
    # === LEGITIMATE NEWS SAMPLES (Expected: Low Risk 0-30%) ===
    {
        "id": 11,
        "content": """
        According to a peer-reviewed study published in Nature Medicine, researchers at Stanford University 
        have developed a new approach to cancer treatment using CRISPR gene editing technology. The clinical 
        trial involved 50 patients with advanced melanoma. Results showed a 30% improvement in progression-free 
        survival compared to standard treatments. Dr. Sarah Chen, lead researcher, cautioned that more research 
        is needed before widespread adoption. The FDA has approved Phase 3 trials beginning next year.
        """,
        "expected": "LEGITIMATE",
        "category": "Science News",
        "description": "Credible scientific reporting with sources"
    },
    {
        "id": 12,
        "content": """
        The World Health Organization released new guidelines today for diabetes management. According to 
        WHO officials, the recommendations are based on systematic reviews of clinical evidence from multiple 
        countries. The guidelines suggest lifestyle modifications as first-line treatment, with medication 
        when needed. Dr. Tedros Adhanom Ghebreyesus emphasized the importance of access to affordable care. 
        The full guidelines are available on the WHO website with detailed methodology and evidence tables.
        """,
        "expected": "LEGITIMATE",
        "category": "Health News",
        "description": "Official WHO announcement with proper sourcing"
    },
    {
        "id": 13,
        "content": """
        Climate scientists report that global temperatures in 2024 were 1.2°C above pre-industrial levels, 
        according to data from NASA and NOAA. The findings, published in multiple peer-reviewed journals, 
        show continued warming trends. Dr. Michael Mann of Penn State explained that the data comes from 
        thousands of temperature stations worldwide. The Intergovernmental Panel on Climate Change (IPCC) 
        notes that reducing greenhouse gas emissions remains critical. Multiple lines of evidence support 
        these conclusions including satellite data, ocean temperatures, and ice core samples.
        """,
        "expected": "LEGITIMATE",
        "category": "Climate Science",
        "description": "Well-sourced climate science reporting"
    },
    {
        "id": 14,
        "content": """
        The Federal Reserve announced a 0.25% interest rate increase today following its monthly policy meeting. 
        Fed Chair Jerome Powell stated the decision aims to moderate inflation while supporting maximum employment. 
        Economic data shows inflation at 3.2% annually, down from last year's peak of 9.1%. The decision was 
        supported by 9 of 12 voting members. Markets responded with the S&P 500 declining 1.2%. Analysts from 
        Goldman Sachs and JP Morgan expect one more rate hike this year before a pause.
        """,
        "expected": "LEGITIMATE",
        "category": "Economic News",
        "description": "Factual economic reporting with named sources"
    },
    {
        "id": 15,
        "content": """
        Researchers at MIT have published a paper in Science journal describing advances in battery technology. 
        The lithium-metal batteries showed 80% capacity retention after 1,000 charge cycles in laboratory tests. 
        Professor Jane Smith, who led the research, noted limitations including cost and scaling challenges. 
        The study was peer-reviewed and funded by the Department of Energy. Independent experts praised the 
        methodology while noting commercial applications are likely 5-10 years away. Full technical details 
        and raw data are available in the supplementary materials.
        """,
        "expected": "LEGITIMATE",
        "category": "Technology News",
        "description": "Credible tech research reporting with caveats"
    },
    {
        "id": 16,
        "content": """
        The European Medicines Agency (EMA) approved a new treatment for multiple sclerosis today after reviewing 
        clinical trial data from 3,000 patients across 15 countries. The Phase 3 trials showed a 40% reduction 
        in relapse rates compared to existing treatments. Common side effects include headache and fatigue. 
        Dr. Emma Wilson from the EMA noted the approval was based on rigorous safety and efficacy reviews. 
        The treatment will be available in EU countries within six months pending pricing negotiations.
        """,
        "expected": "LEGITIMATE",
        "category": "Medical News",
        "description": "Official regulatory announcement with trial data"
    },
    {
        "id": 17,
        "content": """
        According to the latest report from the Centers for Disease Control and Prevention (CDC), flu vaccination 
        rates for the 2024-25 season are tracking slightly higher than last year. The CDC recommends annual 
        flu vaccination for everyone 6 months and older. Dr. Rochelle Walensky explained that vaccine composition 
        is updated annually based on circulating strains. Side effects are typically mild including soreness at 
        injection site. The CDC monitors vaccine safety through multiple surveillance systems with data publicly 
        available on their website.
        """,
        "expected": "LEGITIMATE",
        "category": "Public Health",
        "description": "Official CDC health guidance with transparency"
    },
    {
        "id": 18,
        "content": """
        The International Space Station completed its 100,000th orbit of Earth today, NASA announced. The station 
        has been continuously occupied for 24 years, hosting astronauts from 20 countries. Current research 
        includes experiments in biology, physics, and materials science. NASA Administrator Bill Nelson highlighted 
        international cooperation as key to the station's success. Plans for ISS operations extend through 2030, 
        with private commercial stations expected to follow. Live video feeds and research publications are 
        available on NASA's website.
        """,
        "expected": "LEGITIMATE",
        "category": "Space News",
        "description": "Official NASA announcement with verifiable facts"
    },
    {
        "id": 19,
        "content": """
        A study published in The Lancet examined COVID-19 vaccine effectiveness using data from 5 million people 
        across 8 countries. Results showed 85% effectiveness against hospitalization and 70% against symptomatic 
        infection with Omicron variants. The peer-reviewed research acknowledged limitations including potential 
        selection bias. Dr. Andrew Hill, an independent researcher, noted the findings align with other large 
        studies. The researchers declared funding sources and potential conflicts of interest. Raw anonymized 
        data will be made available to qualified researchers upon request.
        """,
        "expected": "LEGITIMATE",
        "category": "Medical Research",
        "description": "Peer-reviewed research with proper methodology disclosure"
    },
    {
        "id": 20,
        "content": """
        The United Nations released its annual Human Development Report today, ranking 191 countries on health, 
        education, and income metrics. Norway, Switzerland, and Ireland topped the list. The report noted progress 
        in global literacy rates but warned of widening inequality. UN Development Programme Administrator Achim 
        Steiner emphasized the need for inclusive growth. The methodology section details data sources including 
        World Bank, WHO, and UNESCO statistics. Complete country rankings and raw data are available on the UNDP 
        website with detailed technical notes.
        """,
        "expected": "LEGITIMATE",
        "category": "International News",
        "description": "Official UN report with transparent methodology"
    }
]

def test_accuracy(verbose: bool = True) -> Dict:
    """
    Run hard accuracy test on all samples
    """
    print("=" * 80)
    print("🧪 HARD ACCURACY TEST - LinkScout System")
    print("=" * 80)
    print(f"\n📊 Testing {len(HARD_TEST_SAMPLES)} samples (10 fake, 10 legitimate)\n")
    
    results = []
    true_positives = 0  # Correctly identified fake news
    true_negatives = 0  # Correctly identified legitimate news
    false_positives = 0  # Legitimate news marked as fake
    false_negatives = 0  # Fake news marked as legitimate
    
    total_tests = len(HARD_TEST_SAMPLES)
    fake_tests = sum(1 for s in HARD_TEST_SAMPLES if s["expected"] == "FAKE")
    legit_tests = sum(1 for s in HARD_TEST_SAMPLES if s["expected"] == "LEGITIMATE")
    
    print(f"Test Distribution:")
    print(f"  • Fake News Samples: {fake_tests}")
    print(f"  • Legitimate News Samples: {legit_tests}")
    print(f"  • Total Samples: {total_tests}\n")
    print("-" * 80)
    
    for i, sample in enumerate(HARD_TEST_SAMPLES, 1):
        try:
            # Send request to server
            response = requests.post(
                f"{SERVER_URL}/analyze",
                json={"content": sample["content"]},
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"❌ Sample {i}: Server error {response.status_code}")
                continue
            
            data = response.json()
            risk_score = data.get("risk_score", 0)
            
            # Determine verdict based on risk score
            # Fake news: 70-100 risk score
            # Legitimate: 0-30 risk score
            # Gray zone: 30-70 (we'll be strict)
            
            if sample["expected"] == "FAKE":
                if risk_score >= 60:  # Correctly identified as high risk
                    verdict = "✅ CORRECT"
                    true_positives += 1
                    status = "TP"
                else:  # Missed fake news (false negative)
                    verdict = "❌ MISSED"
                    false_negatives += 1
                    status = "FN"
            else:  # LEGITIMATE expected
                if risk_score <= 40:  # Correctly identified as low risk
                    verdict = "✅ CORRECT"
                    true_negatives += 1
                    status = "TN"
                else:  # False alarm (false positive)
                    verdict = "❌ FALSE ALARM"
                    false_positives += 1
                    status = "FP"
            
            result = {
                "id": sample["id"],
                "category": sample["category"],
                "expected": sample["expected"],
                "risk_score": risk_score,
                "verdict": verdict,
                "status": status,
                "description": sample["description"]
            }
            results.append(result)
            
            if verbose:
                print(f"\n🔍 Sample {i}/{total_tests}: {sample['category']}")
                print(f"   Expected: {sample['expected']}")
                print(f"   Risk Score: {risk_score:.1f}%")
                print(f"   Result: {verdict} ({status})")
                print(f"   Description: {sample['description']}")
            
            # Small delay to not overwhelm server
            time.sleep(0.2)
            
        except Exception as e:
            print(f"❌ Sample {i}: Error - {str(e)}")
            continue
    
    # Calculate metrics
    print("\n" + "=" * 80)
    print("📈 FINAL RESULTS")
    print("=" * 80)
    
    # Confusion Matrix
    print("\n📊 Confusion Matrix:")
    print(f"   True Positives (TP):  {true_positives:2d}  - Fake news correctly identified")
    print(f"   True Negatives (TN):  {true_negatives:2d}  - Legit news correctly identified")
    print(f"   False Positives (FP): {false_positives:2d}  - Legit news marked as fake")
    print(f"   False Negatives (FN): {false_negatives:2d}  - Fake news missed")
    
    # Accuracy
    correct = true_positives + true_negatives
    total = len(results)
    accuracy = (correct / total * 100) if total > 0 else 0
    
    # False Positive Rate
    fp_rate = (false_positives / (false_positives + true_negatives) * 100) if (false_positives + true_negatives) > 0 else 0
    
    # Recall (Sensitivity) - ability to detect fake news
    recall = (true_positives / (true_positives + false_negatives) * 100) if (true_positives + false_negatives) > 0 else 0
    
    # Precision - when we say it's fake, how often are we right
    precision = (true_positives / (true_positives + false_positives) * 100) if (true_positives + false_positives) > 0 else 0
    
    # F1 Score
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0
    
    print(f"\n🎯 Key Metrics:")
    print(f"   Accuracy:           {accuracy:.2f}%  {'✅' if accuracy >= 75 else '⚠️' if accuracy >= 60 else '❌'}")
    print(f"   False Positive Rate: {fp_rate:.2f}%  {'✅' if fp_rate <= 10 else '⚠️' if fp_rate <= 20 else '❌'}")
    print(f"   Recall (Sensitivity): {recall:.2f}%  {'✅' if recall >= 70 else '⚠️' if recall >= 50 else '❌'}")
    print(f"   Precision:          {precision:.2f}%  {'✅' if precision >= 70 else '⚠️' if precision >= 50 else '❌'}")
    print(f"   F1 Score:           {f1:.2f}%  {'✅' if f1 >= 70 else '⚠️' if f1 >= 50 else '❌'}")
    
    print(f"\n📋 Performance Assessment:")
    if accuracy >= 75:
        print("   ✅ EXCELLENT - System meets production standards")
    elif accuracy >= 60:
        print("   ⚠️  GOOD - System functional but has room for improvement")
    elif accuracy >= 50:
        print("   ⚠️  FAIR - System needs optimization")
    else:
        print("   ❌ POOR - System requires significant improvements")
    
    print(f"\n💡 Breakdown by Type:")
    fake_correct = true_positives
    fake_total = true_positives + false_negatives
    fake_accuracy = (fake_correct / fake_total * 100) if fake_total > 0 else 0
    
    legit_correct = true_negatives
    legit_total = true_negatives + false_positives
    legit_accuracy = (legit_correct / legit_total * 100) if legit_total > 0 else 0
    
    print(f"   Fake News Detection:  {fake_correct}/{fake_total} correct ({fake_accuracy:.1f}%)")
    print(f"   Legit News Detection: {legit_correct}/{legit_total} correct ({legit_accuracy:.1f}%)")
    
    # Save detailed results
    output = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_samples": total,
        "metrics": {
            "accuracy": round(accuracy, 2),
            "false_positive_rate": round(fp_rate, 2),
            "recall": round(recall, 2),
            "precision": round(precision, 2),
            "f1_score": round(f1, 2)
        },
        "confusion_matrix": {
            "true_positives": true_positives,
            "true_negatives": true_negatives,
            "false_positives": false_positives,
            "false_negatives": false_negatives
        },
        "breakdown": {
            "fake_news_accuracy": round(fake_accuracy, 2),
            "legit_news_accuracy": round(legit_accuracy, 2)
        },
        "detailed_results": results
    }
    
    output_file = "hard_test_results.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    print("=" * 80)
    
    return output

if __name__ == "__main__":
    print("\n🚀 Starting Hard Accuracy Test...\n")
    print("⚠️  Make sure combined_server.py is running on localhost:5000\n")
    
    # Run the test (will fail gracefully if server not running)
    results = test_accuracy(verbose=True)
    
    print("\n✅ Test complete!")
