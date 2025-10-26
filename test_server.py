"""
Quick test to see if server crashes
"""
import requests
import json

try:
    print("Testing server...")
    
    # Test health
    response = requests.get('http://localhost:5000/health', timeout=5)
    print(f"✅ Health check: {response.status_code}")
    
    # Test analysis
    print("\nTesting analysis...")
    data = {
        'content': 'This is a test article.',
        'paragraphs': [{'index': 0, 'text': 'This is a test article.', 'type': 'p'}],
        'title': 'Test',
        'url': ''
    }
    
    response = requests.post(
        'http://localhost:5000/api/v1/analyze-chunks',
        json=data,
        timeout=120
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success!")
        print(f"Verdict: {result.get('verdict')}")
        print(f"Risk: {result.get('misinformation_percentage')}%")
    else:
        print(f"❌ Error: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
