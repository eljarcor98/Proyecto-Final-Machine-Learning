import os
import sys
import json
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# Añadir el directorio raíz al path para poder importar src.db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db import get_session, NewsAnalysis

CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'processed', 'locations_cache.json')

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def extract_unique_locations():
    session = get_session()
    print("Extrayendo ubicaciones de la base de datos...")
    analyses = session.query(NewsAnalysis).all()
    
    from collections import Counter
    all_locs = []
    for row in analyses:
        if row.locations:
            try:
                locs = json.loads(row.locations)
                all_locs.extend(locs)
            except json.JSONDecodeError:
                pass
                
    session.close()
    
    # Tomar solo los 100 lugares más mencionados para evitar sobrecargar la API
    loc_counts = Counter(all_locs)
    top_100 = [loc for loc, count in loc_counts.most_common(100)]
    return top_100

def geocode_locations():
    unique_locs = extract_unique_locations()
    cache = load_cache()
    
    geolocator = Nominatim(user_agent="osint_agent_geocoder")
    
    to_geocode = [loc for loc in unique_locs if loc not in cache]
    print(f"Total ubicaciones únicas: {len(unique_locs)}. Faltan geocodificar: {len(to_geocode)}.")
    
    new_geocodes = 0
    for idx, loc in enumerate(to_geocode):
        # Evitar sobrecargar la API
        time.sleep(1)
        
        try:
            safe_loc = loc.encode('ascii', 'ignore').decode()
            print(f"[{idx+1}/{len(to_geocode)}] Geocodificando: {safe_loc}...")
            location = geolocator.geocode(loc, timeout=10)
            if location:
                cache[loc] = {"lat": location.latitude, "lon": location.longitude}
            else:
                cache[loc] = None # No encontrado
            new_geocodes += 1
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"Error con {loc}: {e}")
            break # Parar en caso de error de límite para guardar lo avanzado
            
    if new_geocodes > 0:
        save_cache(cache)
        print(f"Se actualizaron {new_geocodes} lugares en caché.")
    else:
        print("La caché ya está actualizada.")

if __name__ == "__main__":
    geocode_locations()
