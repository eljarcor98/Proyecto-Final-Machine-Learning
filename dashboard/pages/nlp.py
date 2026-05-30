import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import sys

# Ajustar ruta para importar desde src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db import get_session, NewsArticle

st.set_page_config(page_title="Análisis NLP OSINT", layout="wide", page_icon="📊")

st.title("📊 Análisis de Narrativas (NLP)")
st.markdown("Análisis de frecuencia de palabras y tópicos extraídos de la base de inteligencia.")

# --- Carga de Datos ---
@st.cache_data(ttl=600)
def load_nlp_data():
    session = get_session()
    try:
        # Obtenemos el texto de todos los artículos
        articles = session.query(NewsArticle.title, NewsArticle.description).all()
        texts = []
        for title, desc in articles:
            full_text = f"{title} {desc if desc else ''}"
            texts.append(full_text)
        return " ".join(texts)
    except Exception as e:
        st.error(f"Error al cargar datos para NLP: {e}")
        return ""
    finally:
        session.close()

corpus = load_nlp_data()

if corpus:
    # --- Nube de Palabras ---
    st.subheader("☁️ Nube de Palabras Clave")
    st.info("Visualización de los términos más recurrentes en las noticias monitoreadas.")
    
    wc = WordCloud(
        width=1200, 
        height=600, 
        background_color="white",
        colormap="viridis",
        max_words=100,
        contour_width=3,
        contour_color='steelblue'
    ).generate(corpus)

    fig, ax = plt.subplots(figsize=(20, 10))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)

    # --- Análisis de Frecuencia ---
    st.markdown("---")
    st.subheader("📈 Top de Términos")
    
    # Conteo simple de palabras (sin stop-words complejas para mantener velocidad)
    from collections import Counter
    import re

    words = re.findall(r'\w+', corpus.lower())
    # Lista básica de stop words en español e inglés
    stop_words = {'de', 'la', 'que', 'el', 'en', 'lo', 'del', 'se', 'los', 'un', 'una', 'con', 'por', 'para', 'las', 'the', 'and', 'a', 'of', 'to', 'in', 'is', 'it', 'that', 'as', 'for', 'was', 'with', 'on'}
    filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
    
    word_counts = Counter(filtered_words).most_common(20)
    df_words = pd.DataFrame(word_counts, columns=['Palabra', 'Frecuencia'])

    fig_bar = px.bar(
        df_words, 
        x='Palabra', 
        y='Frecuencia', 
        color='Frecuencia',
        color_continuous_scale='Viridis',
        title="Términos más frecuentes en el corpus"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.caption("Nota: Este análisis se basa en la frecuencia bruta de términos. Para un análisis de tópicos más avanzado, se sugiere el uso de LDA (Latent Dirichlet Allocation).")
else:
    st.warning("No hay datos suficientes en la base de datos para generar el análisis NLP.")