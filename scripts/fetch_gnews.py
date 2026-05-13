import os
import sys
import requests
from dotenv import load_dotenv
import datetime

# Add the parent directory to the path so we can import src.db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db import get_session, NewsArticle

load_dotenv()

GNEWS_API_KEY = os.getenv('GNEWS_API_KEY')
GNEWS_URL = "https://gnews.io/api/v4/search"

# Términos de búsqueda relacionados con el conflicto
SEARCH_QUERY = '("Iran" OR "Israel") AND ("US" OR "United States" OR "conflict" OR "strike" OR "attack")'

def fetch_gnews():
    if not GNEWS_API_KEY:
        print("Error: GNEWS_API_KEY no encontrada en .env")
        return

    params = {
        'q': SEARCH_QUERY,
        'lang': 'en',
        'max': 100,  # Máximo de artículos por petición en plan gratuito (10-100 dependiendo de la key, intentamos 100)
        'sortby': 'publishedAt',
        'apikey': GNEWS_API_KEY
    }

    print(f"Consultando GNews con el query: {SEARCH_QUERY}")
    try:
        response = requests.get(GNEWS_URL, params=params)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error al conectar con GNews: {e}")
        return

    articles = data.get('articles', [])
    print(f"Se encontraron {len(articles)} artículos en GNews.")

    session = get_session()
    inserted_count = 0

    for item in articles:
        # Verificar si la URL ya existe en la base de datos para no duplicar
        exists = session.query(NewsArticle).filter_by(url=item['url']).first()
        if exists:
            continue

        try:
            pub_date = datetime.datetime.strptime(item['publishedAt'], "%Y-%m-%dT%H:%M:%S%z")
            pub_date = pub_date.replace(tzinfo=None) # Convertir a naive timestamp
        except:
            pub_date = None

        new_article = NewsArticle(
            source=f"GNews - {item.get('source', {}).get('name', 'Unknown')}",
            title=item.get('title', ''),
            description=item.get('description', ''),
            content=item.get('content', ''),
            url=item.get('url', ''),
            published_at=pub_date
        )
        session.add(new_article)
        inserted_count += 1

    try:
        session.commit()
        print(f"Guardados exitosamente {inserted_count} nuevos artículos de GNews en PostgreSQL.")
    except Exception as e:
        session.rollback()
        print(f"Error al guardar en la base de datos: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    fetch_gnews()
