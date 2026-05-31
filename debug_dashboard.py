import os
import json
import pandas as pd
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.db import get_session, NewsArticle

def debug_radar():
    print("\n--- Debugging Radar ---")
    data_dir = 'data/raw'
    if not os.path.exists(data_dir):
        print("Error: data/raw directory does not exist")
        return
    
    files = [f for f in os.listdir(data_dir) if f.startswith('opensky_states_')]
    if not files:
        print("Error: No opensky_states_ files found")
        return
    
    latest = sorted(files, reverse=True)[0]
    print(f"Testing latest file: {latest}")
    try:
        with open(os.path.join(data_dir, latest), 'r') as f:
            data = json.load(f)
        print(f"Data type: {type(data)}")
        df = pd.DataFrame(data, columns=['icao24', 'callsign', 'country', 'time', 'contact', 'lon', 'lat', 'alt', 'ground', 'vel', 'track', 'vert', 'sensors', 'geo_alt', 'squawk', 'spi', 'pos_src'])
        print(f"DataFrame shape: {df.shape}")
        if df.empty:
            print("Warning: DataFrame is empty")
        else:
            print("Success: Radar data loaded correctly")
            print(df.head(2))
    except Exception as e:
        print(f"Error loading radar data: {e}")

def debug_nlp():
    print("\n--- Debugging NLP ---")
    session = get_session()
    try:
        articles = session.query(NewsArticle.title, NewsArticle.description).all()
        print(f"Articles found in DB: {len(articles)}")
        if len(articles) == 0:
            print("Warning: No articles found in database for NLP analysis")
        else:
            print("Success: Database contains articles for NLP")
            # Test a sample
            title, desc = articles[0]
            print(f"Sample Title: {title}")
    except Exception as e:
        print(f"Error querying database for NLP: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    debug_radar()
    debug_nlp()