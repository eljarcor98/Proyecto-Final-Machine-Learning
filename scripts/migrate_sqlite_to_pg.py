import os
import sys
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Añadir root al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def migrate_data():
    # 1. Conexión SQLite (Local)
    sqlite_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'osint.db')
    sqlite_engine = create_engine(f'sqlite:///{sqlite_path}')
    
    # 2. Conexión Postgres (Supabase)
    load_dotenv()
    pg_url = os.environ.get('DATABASE_URL')
    if not pg_url or not pg_url.startswith('postgres'):
        print("Error: DATABASE_URL no está configurado para Postgres.")
        return
        
    pg_engine = create_engine(pg_url)
    
    # Crear esquemas correctos antes de insertar
    from src.db import Base
    Base.metadata.drop_all(pg_engine)
    Base.metadata.create_all(pg_engine)
    
    print("Iniciando migración de datos...")
    
    try:
        # Extraer de SQLite
        print("Leyendo 'news_articles' de SQLite...")
        df_articles = pd.read_sql_table('news_articles', sqlite_engine)
        print(f"Encontrados {len(df_articles)} artículos.")
        
        print("Leyendo 'news_analysis' de SQLite...")
        df_analysis = pd.read_sql_table('news_analysis', sqlite_engine)
        print(f"Encontrados {len(df_analysis)} análisis.")
        
        # Insertar a Postgres
        print("Insertando 'news_articles' en Postgres...")
        df_articles.to_sql('news_articles', pg_engine, if_exists='append', index=False)
        print("Artículos migrados.")
        
        print("Insertando 'news_analysis' en Postgres...")
        df_analysis.to_sql('news_analysis', pg_engine, if_exists='append', index=False)
        print("Análisis migrados.")
        
        print("¡Migración completada con éxito!")
        
    except Exception as e:
        print(f"Error durante la migración: {e}")

if __name__ == "__main__":
    migrate_data()
