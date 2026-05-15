import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ACLED_EMAIL = os.getenv("ACLED_EMAIL")
ACLED_PASSWORD = os.getenv("ACLED_PASSWORD")
DATA_DIR = os.path.join('data', 'raw')

def get_access_token(username, password, token_url="https://acleddata.com/oauth/token"):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'username': username,
        'password': password,
        'grant_type': "password",
        'client_id': "acled",
        'scope': "authenticated"
    }

    try:
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()
        token_data = response.json()
        return token_data['access_token']
    except Exception as e:
        print(f"Error obteniendo token de ACLED: {e}")
        return None

def fetch_acled_events():
    if not ACLED_EMAIL or not ACLED_PASSWORD:
        print("Error: Credenciales de ACLED no configuradas en .env")
        return

    token = get_access_token(ACLED_EMAIL, ACLED_PASSWORD)
    if not token:
        return

    # Simplificamos los parámetros para evitar errores de sintaxis en la API
    base_url = "https://acleddata.com/api/acled/read?_format=json"
    
    # Usamos el formato exacto de tu ejemplo inicial
    parameters = {
        "country": "Iran:OR:country=Israel:OR:country=Palestine:OR:country=Lebanon",
        "limit": 100,
        "fields": "event_id_cnty|event_date|event_type|country|location|latitude|longitude|fatalities|notes"
    }

    print(f"Consultando eventos de ACLED para la zona del conflicto...")
    try:
        response = requests.get(
            base_url,
            params=parameters,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
            return

        data = response.json()
        
        if data.get("status") == 200:
            events = data.get("data", [])
            print(f"Se encontraron {len(events)} eventos en ACLED.")
            
            if events:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"acled_events_{timestamp}.json"
                filepath = os.path.join(DATA_DIR, filename)
                
                if not os.path.exists(DATA_DIR):
                    os.makedirs(DATA_DIR)
                    
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(events, f, indent=4, ensure_ascii=False)
                print(f"Eventos guardados en: {filepath}")
            else:
                print("No se encontraron eventos nuevos.")
        else:
            print(f"Error en respuesta de ACLED: {data.get('message')}")
            
    except Exception as e:
        print(f"Error al conectar con ACLED: {e}")

if __name__ == "__main__":
    fetch_acled_events()
