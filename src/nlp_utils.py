import os
import sys
import spacy
import json
from collections import Counter
import datetime

# Add the parent directory to the path so we can import src.db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db import get_session, NewsArticle, NewsAnalysis

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("El modelo de spacy no está instalado. Ejecuta: py -m spacy download en_core_web_sm")
    sys.exit(1)

# Diccionario de keywords para Tópicos
TOPIC_KEYWORDS = {
    "Militar/Conflicto": ["strike", "attack", "missile", "drone", "military", "war", "idf", "hamas", "hezbollah", "explosions", "killed", "army"],
    "Diplomacia/Geopolítica": ["diplomacy", "un", "united nations", "biden", "netanyahu", "talks", "peace", "summit", "deal", "negotiations", "embassy"],
    "Economía": ["oil", "sanctions", "economy", "market", "trade", "prices", "export", "import", "embargo"]
}

def get_topic(text):
    text_lower = text.lower()
    scores = {topic: 0 for topic in TOPIC_KEYWORDS}
    
    for topic, keywords in TOPIC_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                scores[topic] += 1
                
    # Retornar el tópico con más puntaje
    max_score = max(scores.values())
    if max_score > 0:
        for topic, score in scores.items():
            if score == max_score:
                return topic
    return "Otro"

def process_articles():
    session = get_session()
    articles = session.query(NewsArticle).all()
    print(f"Iniciando procesamiento de NLP para {len(articles)} artículos...")
    
    processed_count = 0
    for article in articles:
        # Verificar si ya está analizado
        exists = session.query(NewsAnalysis).filter_by(article_id=article.id).first()
        if exists:
            continue
            
        text = f"{article.title} {article.description or ''} {article.content or ''}"
        
        # spaCy NLP
        doc = nlp(text)
        
        locations = []
        organizations = []
        
        for ent in doc.ents:
            if ent.label_ == "GPE": # Geopolitical Entity (countries, cities, states)
                locations.append(ent.text)
            elif ent.label_ == "ORG":
                organizations.append(ent.text)
                
        # Limpiar y obtener los más comunes (evitar duplicados masivos en un mismo artículo)
        locations = list(set(locations))
        organizations = list(set(organizations))
        
        # Tópico
        topic = get_topic(text)
        
        analysis = NewsAnalysis(
            article_id=article.id,
            locations=json.dumps(locations),
            organizations=json.dumps(organizations),
            topic=topic
        )
        session.add(analysis)
        processed_count += 1
        
    try:
        session.commit()
        print(f"Procesamiento finalizado. {processed_count} nuevos artículos analizados.")
    except Exception as e:
        session.rollback()
        print(f"Error al guardar análisis: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    process_articles()
