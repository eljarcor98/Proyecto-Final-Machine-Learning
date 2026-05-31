import os
import sys
import feedparser
from bs4 import BeautifulSoup
import datetime
from email.utils import parsedate_to_datetime

# Add the parent directory to the path so we can import src.db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db import get_session, NewsArticle

RSS_FEEDS = {
    "BBC Middle East": "http://feeds.bbci.co.uk/news/world/middle_east/rss.xml",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    # El feed de Google News para búsqueda específica (ej. Iran Israel conflict)
    "Google News (Conflict)": "https://news.google.com/rss/search?q=Iran+Israel+conflict&hl=en-US&gl=US&ceid=US:en"
}

def clean_html(raw_html):
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator=' ').strip()

def fetch_rss_news():
    session = get_session()
    total_inserted = 0

    for source_name, feed_url in RSS_FEEDS.items():
        print(f"Consultando RSS de {source_name}...")
        feed = feedparser.parse(feed_url)
        
        inserted_count = 0
        for entry in feed.entries:
            url = entry.get('link', '')
            
            # Evitar duplicados
            exists = session.query(NewsArticle).filter_by(url=url).first()
            if exists:
                continue

            title = entry.get('title', '')
            # Extraer descripción y limpiar HTML si lo hay
            description_html = entry.get('description', '')
            description = clean_html(description_html)
            
            # Intentar parsear la fecha
            pub_date = None
            if 'published' in entry:
                try:
                    pub_date = parsedate_to_datetime(entry.published).replace(tzinfo=None)
                except:
                    pass

            new_article = NewsArticle(
                source=f"RSS - {source_name}",
                title=title,
                description=description,
                content="", # Normalmente RSS no da el contenido completo
                url=url,
                published_at=pub_date
            )
            session.add(new_article)
            inserted_count += 1
            total_inserted += 1

        try:
            session.commit()
            print(f"-> {inserted_count} nuevos artículos guardados de {source_name}.")
        except Exception as e:
            session.rollback()
            print(f"-> Error al guardar datos de {source_name}: {e}")

    session.close()
    print(f"\nProceso RSS completado. Total nuevos artículos guardados: {total_inserted}")

if __name__ == "__main__":
    fetch_rss_news()
