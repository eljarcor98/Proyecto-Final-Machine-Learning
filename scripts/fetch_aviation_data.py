import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

API_KEY = os.getenv("AVIATIONSTACK_KEY")
AIRPORTS = ['TLV', 'IKA', 'AMM', 'BEY']
DATA_DIR = os.path.join('data', 'raw')

def fetch_and_save_flights(airport_code):
    if not API_KEY:
        print("Error: AVIATIONSTACK_KEY not found in environment.")
        return

    url = "http://api.aviationstack.com/v1/flights"
    params = {
        'access_key': API_KEY,
        'dep_iata': airport_code,
        'limit': 100
    }
    
    print(f"Fetching flights from {airport_code}...")
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"flights_{airport_code}_{timestamp}.json"
                filepath = os.path.join(DATA_DIR, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data['data'], f, indent=4)
                
                print(f"Saved {len(data['data'])} flights to {filepath}")
            else:
                print(f"No data returned for {airport_code}: {data.get('error', {}).get('message', 'Unknown error')}")
        else:
            print(f"Failed to fetch data for {airport_code}. Status: {response.status_code}")
    except Exception as e:
        print(f"Error fetching data for {airport_code}: {e}")

if __name__ == "__main__":
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    for airport in AIRPORTS:
        fetch_and_save_flights(airport)
