import requests
import json
import os

# Load Google API key and CSE ID from environment variables or config file
def load_google_config():
    # Try environment variables first
    api_key = os.environ.get('GOOGLE_API_KEY')
    cse_id = os.environ.get('GOOGLE_CSE_ID')
    
    # Fallback to config file if exists
    if not api_key or not cse_id:
        try:
            with open('google_config.json', 'r') as f:
                config = json.load(f)
            api_key = config.get('google_api_key', api_key)
            cse_id = config.get('google_cse_id', cse_id)
        except FileNotFoundError:
            pass
    
    return api_key, cse_id

GOOGLE_API_KEY, GOOGLE_CSE_ID = load_google_config()
GOOGLE_SEARCH_URL = 'https://www.googleapis.com/customsearch/v1'

def google_web_search(query, count=5):
    params = {
        'key': GOOGLE_API_KEY,
        'cx': GOOGLE_CSE_ID,
        'q': query,
        'num': count
    }
    response = requests.get(GOOGLE_SEARCH_URL, params=params)
    response.raise_for_status()
    data = response.json()
    results = []
    for item in data.get('items', []):
        results.append({
            'name': item.get('title', ''),
            'url': item.get('link', ''),
            'snippet': item.get('snippet', '')
        })
    return results
