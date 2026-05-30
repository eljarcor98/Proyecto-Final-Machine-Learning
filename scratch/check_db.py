
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Contar artículos
    count = conn.execute(text("SELECT count(*) FROM news_articles")).scalar()
    print(f"Total de artículos: {count}")
    
    # Ver las fuentes
    sources = conn.execute(text("SELECT source, count(*) FROM news_articles GROUP BY source")).fetchall()
    print("\nFuentes:")
    for s in sources:
        print(f"- {s[0]}: {s[1]}")
    
    # Ver algunos títulos
    titles = conn.execute(text("SELECT title FROM news_articles LIMIT 5")).fetchall()
    print("\nÚltimos 5 títulos:")
    for t in titles:
        print(f"- {t[0]}")
