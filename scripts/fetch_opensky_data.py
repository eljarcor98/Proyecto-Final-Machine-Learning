import requests
from requests.auth import HTTPBasicAuth
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

USER = os.getenv("OPENSKY_USERNAME")
PASS = os.getenv("OPENSKY_PASSWORD")
DATA_DIR = os.path.join('data', 'raw')

def fetch_opensky_states():
    # Bounding box: Israel, Iran, Jordan, etc.
    params = {
        'lamin': 25.0,
        'lomin': 30.0,
        'lamax': 40.0,
        'lomax': 65.0
    }
    url = "https://opensky-network.org/api/states/all"
    
    print("Fetching real-time states from OpenSky...")
    try:
        response = requests.get(url, params=params, auth=HTTPBasicAuth(USER, PASS))
        if response.status_code == 200:
            data = response.json()
            states = data.get('states', [])
            if states:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"opensky_states_{timestamp}.json"
                filepath = os.path.join(DATA_DIR, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(states, f, indent=4)
                
                print(f"Saved {len(states)} aircraft states to {filepath}")
            else:
                print("No aircraft found in the specified region.")
        else:
            print(f"OpenSky Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    fetch_opensky_states()
