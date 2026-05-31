
import os
import sys
from sqlalchemy import text
from dotenv import load_dotenv

# Añadir el directorio raíz al path para importar src.db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db import get_session, NewsArticle

load_dotenv()

def query_news(keyword=None, limit=10):
    session = get_session()
    try:
        if keyword:
            print(f"\n--- Buscando noticias sobre: '{keyword}' ---")
            # Consulta SQL pura usando text()
            query = text("""
                SELECT source, title, published_at 
                FROM news_articles 
                WHERE title ILIKE :kw OR description ILIKE :kw OR content ILIKE :kw
                ORDER BY published_at DESC 
                LIMIT :limit
            """)
            results = session.execute(query, {"kw": f"%{keyword}%", "limit": limit}).fetchall()
        else:
            print(f"\n--- Últimas {limit} noticias en la base de datos ---")
            query = text("SELECT source, title, published_at FROM news_articles ORDER BY published_at DESC LIMIT :limit")
            results = session.execute(query, {"limit": limit}).fetchall()

        if not results:
            print("No se encontraron resultados.")
        for row in results:
            date = row[2].strftime("%Y-%m-%d %H:%M") if row[2] else "N/A"
            print(f"[{date}] [{row[0]}] {row[1]}")
            
    except Exception as e:
        print(f"Error al realizar la consulta: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    # Ejemplo: Buscar 'Trump'
    query_news(keyword="Trump", limit=5)
    
    # Ejemplo: Buscar 'naval'
    query_news(keyword="naval", limit=5)
    
    # Ejemplo: Ver las últimas noticias generales
    query_news(limit=5)
