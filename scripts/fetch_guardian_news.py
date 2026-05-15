import os
import sys
import requests
from dotenv import load_dotenv
import datetime

# Add the parent directory to the path so we can import src.db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db import get_session, NewsArticle

load_dotenv()

GUARDIAN_API_KEY = os.getenv('GUARDIAN_API_KEY')
GUARDIAN_URL = "https://content.guardianapis.com/search"

# Usamos el mismo query potente que en GNews
SEARCH_QUERY = '("Iran" OR "Israel") AND ("naval" OR "ship" OR "tanker" OR "strategic" OR "Trump" OR "Ayatollah" OR "Khamenei" OR "Hormuz" OR "Red Sea" OR "strike" OR "attack" OR "drones" OR "UAV" OR "explosion" OR "oil" OR "war" OR "famine" OR "humanitarian crisis" OR "pollution")'

def fetch_guardian_news():
    if not GUARDIAN_API_KEY:
        print("Error: GUARDIAN_API_KEY no encontrada en .env")
        return

    params = {
        'q': SEARCH_QUERY,
        'api-key': GUARDIAN_API_KEY,
        'page-size': 50,
        'order-by': "newest",
        'show-fields': "trailText,bodyText" # trailText es como la descripción
    }

    print(f"Consultando The Guardian con el query: {SEARCH_QUERY}")
    try:
        response = requests.get(GUARDIAN_URL, params=params)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error al conectar con The Guardian: {e}")
        return

    results = data.get('response', {}).get('results', [])
    print(f"Se encontraron {len(results)} artículos en The Guardian.")

    session = get_session()
    inserted_count = 0

    for item in results:
        # Verificar si la URL ya existe en la base de datos
        exists = session.query(NewsArticle).filter_by(url=item['webUrl']).first()
        if exists:
            continue

        try:
            # The Guardian usa formato "2024-05-14T20:00:00Z"
            pub_date = datetime.datetime.strptime(item['webPublicationDate'], "%Y-%m-%dT%H:%M:%SZ")
        except:
            pub_date = None

        fields = item.get('fields', {})
        
        new_article = NewsArticle(
            source="The Guardian",
            title=item.get('webTitle', ''),
            description=fields.get('trailText', ''),
            content=fields.get('bodyText', '')[:2000], # Limitamos el contenido para no saturar la DB
            url=item.get('webUrl', ''),
            published_at=pub_date
        )
        session.add(new_article)
        inserted_count += 1

    try:
        session.commit()
        print(f"Guardados exitosamente {inserted_count} nuevos artículos de The Guardian en PostgreSQL.")
    except Exception as e:
        session.rollback()
        print(f"Error al guardar en la base de datos: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    fetch_guardian_news()
