"""
03_nlp_multilingual.py
======================
Análisis temático multilingüe usando Sentence-Transformers.
Resuelve el problema de los diferentes idiomas en GDELT.
"""

import os
import sys
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sentence_transformers import SentenceTransformer

# Configuración de rutas
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.db import get_session, NewsArticle

def run_analysis():
    print("Cargando noticias desde la base de datos...")
    session = get_session()
    # Cargamos todo el histórico recolectado
    articles = session.query(NewsArticle).all()
    session.close()

    df = pd.DataFrame({
        'id':           [a.id for a in articles],
        'source':       [a.source or '' for a in articles],
        'title':        [a.title or '' for a in articles],
        'description':  [a.description or '' for a in articles],
        'published_at': [a.published_at for a in articles],
    })

    print(f"Total articulos cargados: {len(df)}")
    
    # Preprocesamiento básico
    df['text'] = df['title'].str.strip() + ' ' + df['description'].str.strip()
    df = df[df['text'].str.len() > 10].reset_index(drop=True)
    
    print("Generando Embeddings Multilingües (esto puede tardar unos minutos)...")
    # Modelo ligero y potente para 50+ idiomas
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    # Generamos los vectores
    X = model.encode(df['text'].tolist(), show_progress_bar=True)
    print(f"Vectores generados: {X.shape}")

    # Selección de K (optimizado para velocidad)
    print("Calculando numero optimo de clusters...")
    k_range = range(4, 11)
    silhouettes = []
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=5)
        labels = km.fit_predict(X)
        sil = silhouette_score(X, labels, sample_size=1000)
        silhouettes.append(sil)
    
    best_k = list(k_range)[np.argmax(silhouettes)]
    print(f"K optimo detectado: {best_k}")

    # Clustering final
    km_final = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    df['cluster'] = km_final.fit_predict(X)

    # Reducción de dimensiones para visualización
    print("Reduciendo dimensiones con PCA...")
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X)
    df['x'] = coords[:, 0]
    df['y'] = coords[:, 1]

    # Visualización
    plt.figure(figsize=(12, 8))
    colors = cm.tab10(np.linspace(0, 1, best_k))
    for i in range(best_k):
        mask = df['cluster'] == i
        plt.scatter(df.loc[mask, 'x'], df.loc[mask, 'y'], 
                    c=[colors[i]], label=f'Cluster {i}', alpha=0.6, s=40)
    
    plt.title(f'Clusters Multilingues de Noticias OSINT (K={best_k})', fontweight='bold')
    plt.legend()
    plt.grid(alpha=0.3)
    out_img = os.path.join(PROJECT_ROOT, 'notebooks', 'multilingual_clusters.png')
    plt.savefig(out_img, dpi=150, bbox_inches='tight')
    print(f"Grafica guardada en: {out_img}")

    # Exportación
    out_csv = os.path.join(PROJECT_ROOT, 'notebooks', 'news_clusters_multilingual.csv')
    df[['id', 'source', 'title', 'published_at', 'cluster']].to_csv(out_csv, index=False)
    print(f"Resultados exportados a: {out_csv}")

if __name__ == "__main__":
    run_analysis()
