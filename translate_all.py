import os
import sys
from deep_translator import GoogleTranslator
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Adjust path to import from src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.db import get_session, NewsArticle

def translate_all_articles():
    print("Starting mass translation of articles...")
    session = get_session()
    translator = GoogleTranslator(source='auto', target='es')
    
    try:
        # Fetch articles that are missing translations (NULL or empty string)
        articles = session.query(NewsArticle).filter(
            (NewsArticle.title_es == None) | (NewsArticle.title_es == '') |
            (NewsArticle.description_es == None) | (NewsArticle.description_es == '')
        ).all()
        
        total = len(articles)
        print(f"Found {total} articles needing translation.")
        
        for i, art in enumerate(articles):
            try:
                if not art.title_es and art.title:
                    art.title_es = translator.translate(art.title)
                if not art.description_es and art.description:
                    art.description_es = translator.translate(art.description)
                
                # Commit every 10 articles to avoid losing progress and memory issues
                if (i + 1) % 10 == 0:
                    session.commit()
                    print(f"Processed {i+1}/{total} articles...")
            except Exception as e:
                print(f"Error translating article {art.id}: {e}")
                session.rollback()
                continue
        
        session.commit()
        print("Translation process completed successfully.")
        
    except Exception as e:
        print(f"A critical error occurred: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    translate_all_articles()