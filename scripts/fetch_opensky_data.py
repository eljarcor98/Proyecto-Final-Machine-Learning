import requests
from requests.auth import HTTPBasicAuth
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Ensure project root is in sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.db import db, init_db

# Initialize database tables
init_db()

load_dotenv()

USER = os.getenv("OPENSKY_USERNAME")
PASS = os.getenv("OPENSKY_PASSWORD")

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
                if db.save_flights_data(states):
                    print(f"Saved {len(states)} aircraft states to database.")
                else:
                    print("Error saving aircraft states to database.")
            else:
                print("No aircraft found in the specified region.")
        else:
            print(f"OpenSky Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    fetch_opensky_states()
