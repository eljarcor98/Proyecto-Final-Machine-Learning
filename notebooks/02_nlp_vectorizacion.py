"""
02_nlp_vectorizacion.py
========================
Vectorización de noticias OSINT con TF-IDF + KMeans + PCA
Se ejecuta como script de análisis. Guarda gráficas en notebooks/

Requisitos extra: umap-learn (opcional, se usa PCA si no está disponible)
"""

import os
import sys
import datetime
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Sin pantalla (guardamos las gráficas en disco)
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

# ──────────────────────────────────────────
# Intentar cargar UMAP (opcional)
# ──────────────────────────────────────────
try:
    from umap import UMAP
    USE_UMAP = True
    print("[OK] UMAP disponible. Se usará para la reducción final.")
except ImportError:
    USE_UMAP = False
    print("[INFO] UMAP no instalado. Se usará PCA en su lugar.")

# ──────────────────────────────────────────
# Acceso a la base de datos
# ──────────────────────────────────────────
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db import get_session, NewsArticle

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_articles():
    print("\n[1/5] Cargando artículos desde la base de datos...")
    session = get_session()
    try:
        articles = session.query(NewsArticle).filter(
            NewsArticle.published_at >= datetime.datetime(2026, 1, 1)
        ).all()
        print(f"  -> {len(articles)} artículos encontrados desde el 2026-01-01")
        data = {
            'id': [a.id for a in articles],
            'source': [a.source or '' for a in articles],
            'title': [a.title or '' for a in articles],
            'description': [a.description or '' for a in articles],
            'published_at': [a.published_at for a in articles],
        }
        return pd.DataFrame(data)
    finally:
        session.close()


def build_corpus(df):
    """Combina título + descripción en un solo texto por artículo."""
    df['text'] = df['title'].str.strip() + ' ' + df['description'].str.strip()
    df['text'] = df['text'].str.lower()
    # Eliminar artículos sin texto útil
    df = df[df['text'].str.len() > 20].reset_index(drop=True)
    return df


def vectorize(df):
    print("\n[2/5] Vectorizando con TF-IDF...")
    vectorizer = TfidfVectorizer(
        max_features=500,
        stop_words='english',
        ngram_range=(1, 2),
        min_df=2,
        sublinear_tf=True
    )
    X = vectorizer.fit_transform(df['text'])
    feature_names = vectorizer.get_feature_names_out()
    print(f"  -> Matriz TF-IDF: {X.shape[0]} artículos x {X.shape[1]} términos")
    return X, vectorizer, feature_names


def find_optimal_k(X, k_range=range(2, 11)):
    """Usa el método del codo + silhouette para elegir K."""
    print("\n[3/5] Buscando el número óptimo de clusters...")
    X_dense = X.toarray()
    
    inertias = []
    silhouettes = []
    
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X_dense)
        inertias.append(km.inertia_)
        sil = silhouette_score(X_dense, labels, sample_size=min(500, len(labels)))
        silhouettes.append(sil)
        print(f"  K={k} | Inertia: {km.inertia_:.0f} | Silhouette: {sil:.3f}")
    
    # Plot codo + silhouette
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle('Selección del número óptimo de Clusters', fontsize=14, fontweight='bold')
    
    axes[0].plot(list(k_range), inertias, 'bo-', linewidth=2)
    axes[0].set_title('Método del Codo (Inertia)')
    axes[0].set_xlabel('Número de Clusters (K)')
    axes[0].set_ylabel('Inertia')
    axes[0].grid(alpha=0.3)
    
    axes[1].plot(list(k_range), silhouettes, 'ro-', linewidth=2)
    axes[1].set_title('Coeficiente de Silhouette')
    axes[1].set_xlabel('Número de Clusters (K)')
    axes[1].set_ylabel('Silhouette Score')
    axes[1].grid(alpha=0.3)
    
    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, 'cluster_selection.png')
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  -> Gráfica guardada: {out}")
    
    # Elegir K con mejor silhouette
    best_k = list(k_range)[np.argmax(silhouettes)]
    print(f"  -> K óptimo elegido: {best_k}")
    return best_k


def cluster_and_visualize(df, X, k, feature_names):
    print(f"\n[4/5] Aplicando KMeans con K={k}...")
    X_dense = X.toarray()
    
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    df['cluster'] = km.fit_predict(X_dense)
    
    # ── Top palabras por cluster ──────────────────────────────
    print("\n  Top palabras por cluster:")
    cluster_keywords = {}
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]
    for i in range(k):
        top_words = [feature_names[ind] for ind in order_centroids[i, :10]]
        cluster_keywords[i] = top_words
        print(f"  Cluster {i}: {', '.join(top_words)}")
    
    # ── Reducción de dimensionalidad ─────────────────────────
    print("\n[5/5] Reduciendo dimensiones para visualización...")
    if USE_UMAP:
        reducer = UMAP(n_components=2, random_state=42, n_neighbors=15, min_dist=0.1)
        coords = reducer.fit_transform(X_dense)
        method_name = "UMAP"
    else:
        pca = PCA(n_components=50, random_state=42)
        X_pca = pca.fit_transform(X_dense)
        pca2 = PCA(n_components=2, random_state=42)
        coords = pca2.fit_transform(X_pca)
        method_name = "PCA"
    
    df['x'] = coords[:, 0]
    df['y'] = coords[:, 1]
    
    # ── Scatter plot principal ───────────────────────────────
    colors = cm.tab10(np.linspace(0, 1, k))
    fig, ax = plt.subplots(figsize=(14, 9))
    
    for cluster_id in range(k):
        mask = df['cluster'] == cluster_id
        top_label = ', '.join(cluster_keywords[cluster_id][:3])
        ax.scatter(
            df.loc[mask, 'x'], df.loc[mask, 'y'],
            c=[colors[cluster_id]],
            label=f"C{cluster_id}: {top_label}",
            alpha=0.7, s=60, edgecolors='white', linewidth=0.4
        )
    
    ax.set_title(f'Patrones en Noticias OSINT — {method_name} + KMeans (K={k})', fontsize=15, fontweight='bold')
    ax.set_xlabel(f'{method_name} Dim 1')
    ax.set_ylabel(f'{method_name} Dim 2')
    ax.legend(loc='upper right', fontsize=8, framealpha=0.9)
    ax.grid(alpha=0.2)
    
    plt.tight_layout()
    out_scatter = os.path.join(OUTPUT_DIR, 'news_clusters.png')
    plt.savefig(out_scatter, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  -> Scatter guardado: {out_scatter}")
    
    # ── Distribución de artículos por cluster ────────────────
    cluster_counts = df['cluster'].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(
        [f"C{i}\n{', '.join(cluster_keywords[i][:2])}" for i in cluster_counts.index],
        cluster_counts.values,
        color=[colors[i] for i in cluster_counts.index],
        edgecolor='white', linewidth=0.7
    )
    for bar, count in zip(bars, cluster_counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                str(count), ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    ax.set_title('Artículos por Cluster Temático', fontsize=13, fontweight='bold')
    ax.set_ylabel('Número de artículos')
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    out_bar = os.path.join(OUTPUT_DIR, 'cluster_distribution.png')
    plt.savefig(out_bar, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  -> Distribución guardada: {out_bar}")
    
    return df, cluster_keywords


def print_sample_articles(df, cluster_keywords):
    """Muestra un ejemplo de artículo por cluster."""
    print("\n" + "="*60)
    print("  MUESTRA DE ARTÍCULOS POR CLUSTER")
    print("="*60)
    for cid in sorted(df['cluster'].unique()):
        sample = df[df['cluster'] == cid].iloc[0]
        print(f"\n  [Cluster {cid}] Top temas: {', '.join(cluster_keywords[cid][:5])}")
        print(f"  Fuente  : {sample['source']}")
        print(f"  Título  : {sample['title'][:100]}")
        print(f"  Fecha   : {sample['published_at']}")
    print("\n" + "="*60)


if __name__ == "__main__":
    print("="*60)
    print("  VECTORIZACIÓN OSINT - Patrones en Noticias")
    print("="*60)
    
    # 1. Cargar datos
    df = load_articles()
    if df.empty:
        print("[ERROR] No hay artículos en la base de datos. Ejecuta primero los scripts de captura.")
        sys.exit(1)
    
    # 2. Construir corpus
    df = build_corpus(df)
    print(f"  -> Corpus final: {len(df)} artículos con texto válido")
    
    # 3. Vectorizar
    X, vectorizer, feature_names = vectorize(df)
    
    # 4. Encontrar K óptimo
    max_k = min(10, len(df) // 5)
    best_k = find_optimal_k(X, k_range=range(2, max_k + 1))
    
    # 5. Clustering + visualización
    df, cluster_keywords = cluster_and_visualize(df, X, best_k, feature_names)
    
    # 6. Imprimir muestra
    print_sample_articles(df, cluster_keywords)
    
    # 7. Guardar CSV con resultados
    out_csv = os.path.join(OUTPUT_DIR, 'news_clusters.csv')
    df[['id', 'source', 'title', 'published_at', 'cluster']].to_csv(out_csv, index=False, encoding='utf-8')
    print(f"\n[DONE] CSV exportado: {out_csv}")
    print("[DONE] Revisa las graficas en la carpeta notebooks/")
