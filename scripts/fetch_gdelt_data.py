import requests
import json
import os
from datetime import datetime

DATA_DIR = os.path.join('data', 'raw')

def fetch_gdelt_news(query='iran israel usa', limit=20):
    url = "https://api.gdeltproject.org/api/v2/doc/doc"
    params = {
        'query': query,
        'mode': 'artlist',
        'format': 'json',
        'maxrecords': limit
    }
    
    print(f"Fetching GDELT news for: {query}...")
    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            if articles:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"gdelt_news_{timestamp}.json"
                filepath = os.path.join(DATA_DIR, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(articles, f, indent=4)
                print(f"Saved {len(articles)} articles to {filepath}")
            else:
                print("No articles found.")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    fetch_gdelt_news()
