import os
import sys
import requests
import datetime
import json

# Add the parent directory to the path so we can import src.db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db import get_session, NewsArticle

def fetch_gdelt_historical(query='(iran OR israel OR "middle east") (conflict OR strike OR war OR attack)', limit=250):
    """
    Fetch historical news from GDELT DOC API v2.
    GDELT doesn't require an API key.
    """
    url = "https://api.gdeltproject.org/api/v2/doc/doc"
    
    # We use a broad search for the conflict
    # timespan:4m should cover since start of the year (May -> Jan is 4 months)
    params = {
        'query': query,
        'mode': 'artlist',
        'format': 'json',
        'maxrecords': limit,
        'timespan': '4m', # Last 4 months
        'sort': 'datedesc'
    }
    
    print(f"Consultando GDELT para noticias históricas (últimos 4 meses) con query: {query}")
    try:
        response = requests.get(url, params=params, timeout=60)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            print(f"Se encontraron {len(articles)} artículos en GDELT.")
            
            session = get_session()
            inserted_count = 0
            
            for art in articles:
                url_art = art.get('url')
                if not url_art:
                    continue
                
                # Check for duplicates
                exists = session.query(NewsArticle).filter_by(url=url_art).first()
                if exists:
                    continue
                
                # Parse date (GDELT format: "20260515T123000Z")
                pub_date_str = art.get('seendate', '')
                pub_date = None
                if pub_date_str:
                    try:
                        pub_date = datetime.datetime.strptime(pub_date_str, "%Y%m%dT%H%M%SZ")
                    except:
                        pass
                
                new_article = NewsArticle(
                    source=f"GDELT - {art.get('source', 'Unknown')}",
                    title=art.get('title', 'No Title'),
                    description="", # GDELT artlist doesn't give description
                    content="",
                    url=url_art,
                    published_at=pub_date
                )
                session.add(new_article)
                inserted_count += 1
            
            try:
                session.commit()
                print(f"Guardados exitosamente {inserted_count} nuevos artículos de GDELT en la base de datos.")
            except Exception as e:
                session.rollback()
                print(f"Error al guardar en la base de datos: {e}")
            finally:
                session.close()
        else:
            print(f"Error en la API de GDELT: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error de conexión con GDELT: {e}")

if __name__ == "__main__":
    fetch_gdelt_historical()
