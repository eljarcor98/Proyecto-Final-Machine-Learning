import os
import sys
import pandas as pd
import json
from sqlalchemy import text

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db import engine

def create_daily_dataset():
    print("Extrayendo datos de PostgreSQL para Feature Engineering...")
    
    query = """
    SELECT a.id, a.published_at, n.topic, n.locations
    FROM news_articles a
    JOIN news_analysis n ON a.id = n.article_id
    WHERE a.published_at IS NOT NULL
    """
    
    df = pd.read_sql(query, engine)
    df['date'] = pd.to_datetime(df['published_at']).dt.date
    
    # 1. Agrupar por fecha
    daily_stats = df.groupby('date').size().reset_index(name='total_articles')
    
    # 2. % de noticias de conflicto por día
    conflict_counts = df[df['topic'] == 'Militar/Conflicto'].groupby('date').size().reset_index(name='conflict_articles')
    daily_stats = pd.merge(daily_stats, conflict_counts, on='date', how='left').fillna(0)
    daily_stats['pct_conflict'] = (daily_stats['conflict_articles'] / daily_stats['total_articles']) * 100
    
    # 3. % de noticias de economía por día
    eco_counts = df[df['topic'] == 'Economía'].groupby('date').size().reset_index(name='eco_articles')
    daily_stats = pd.merge(daily_stats, eco_counts, on='date', how='left').fillna(0)
    daily_stats['pct_economy'] = (daily_stats['eco_articles'] / daily_stats['total_articles']) * 100
    
    # 4. Conteo de menciones a Israel e Irán
    def count_mentions(row_locs, country):
        if not row_locs: return 0
        locs = json.loads(row_locs)
        return sum(1 for l in locs if country.lower() in l.lower())

    df['mentions_israel'] = df['locations'].apply(lambda x: count_mentions(x, 'Israel'))
    df['mentions_iran'] = df['locations'].apply(lambda x: count_mentions(x, 'Iran'))
    
    mentions_df = df.groupby('date')[['mentions_israel', 'mentions_iran']].sum().reset_index()
    daily_stats = pd.merge(daily_stats, mentions_df, on='date', how='left')
    
    # 5. Crear el TARGET (Variable Objetivo)
    # Definimos Alerta Alta (1) si pct_conflict > 30% Y total_articles > 1 (para evitar sesgo de pocos datos)
    # O si las menciones de Israel/Irán son muy altas.
    daily_stats['target_alert'] = ((daily_stats['pct_conflict'] > 30) | 
                                  (daily_stats['mentions_israel'] + daily_stats['mentions_iran'] > 10)).astype(int)
    
    # Guardar dataset procesado
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'daily_ml_dataset.csv')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    daily_stats.to_csv(output_path, index=False)
    
    print(f"Dataset creado exitosamente con {len(daily_stats)} días de datos.")
    print(f"Ubicación: {output_path}")
    print(f"Distribución de clases:\n{daily_stats['target_alert'].value_counts()}")
    
    return daily_stats

if __name__ == "__main__":
    create_daily_dataset()
