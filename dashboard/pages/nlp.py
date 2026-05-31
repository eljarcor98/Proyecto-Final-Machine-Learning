import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import sys

# Ajustar ruta para importar desde src (subir 3 niveles para llegar a la raíz)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.db import get_session, NewsArticle, init_db

# Asegurar que la base de datos esté inicializada
init_db()

st.set_page_config(page_title="Análisis NLP OSINT", layout="wide", page_icon="📊")

# Global CSS for consistency and hiding sidebar
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');
    
    /* Use a more targeted font application to avoid overlapping/layout issues */
    html, body, st.markdown, .stApp { 
        font-family: 'Montserrat', sans-serif !important; 
    }
    
    /* Force line-height in all streamlit elements to prevent "montadas" (overlapping) text */
    div[data-testid="stMarkdownContainer"] p, 
    div[data-testid="stAlertContentInfo"] p, 
    div[data-testid="stCaptionContainer"] p {
        line-height: 1.6 !important;
        margin-bottom: 0.5rem !important;
    }

    .stApp { animation: vanishIn 0.6s ease-out; }
    @keyframes vanishIn { 0% { opacity: 0; transform: scale(0.98); } 100% { opacity: 1; transform: scale(1); } }
    [data-testid="stSidebar"], [data-testid="stSidebarCollapseButton"], div[data-testid="stSidebarNav"] { display: none !important; }
    .return-btn {
        display: inline-block;
        padding: 8px 16px;
        background-color: #3b82f6;
        color: white !important;
        text-decoration: none;
        border-radius: 8px;
        font-weight: 600;
        font-family: 'Montserrat', sans-serif;
        transition: background-color 0.3s ease;
        border: none;
        cursor: pointer;
    }
    .return-btn:hover { background-color: #2563eb; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# Return button
st.markdown('<a href="/" target="_self" class="return-btn">⬅️ Volver al Index</a>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.title("📊 Análisis de Narrativas (NLP)")
st.markdown("### 📖 Guía de Flujo de Inteligencia")
st.info("""
**¿De dónde viene la información y cómo se procesa?**  
La inteligencia de este módulo no es estática; es el resultado de un pipeline dinámico. La información proviene de la monitorización constante de medios digitales (GNews, RSS y GDELT), se almacena en una base de datos estructurada y se somete a un proceso de refinamiento lingüístico para extraer los conceptos más relevantes.
""")

# --- "Infografía" Conceptual con Plotly ---
st.subheader("🗺️ Mapa de Procesos (Infografía del Pipeline)")
import plotly.graph_objects as go

# Definición de nodos y aristas para el diagrama de flujo
nodes = ["Fuentes (GNews/RSS)", "DB SQLite", "Preprocesamiento", "Modelado Estadístico", "Dashboard Final"]
x_coords = [1, 2, 3, 4, 5]
y_coords = [1, 1, 1, 1, 1]

edge_x = []
edge_y = []
for i in range(len(nodes)-1):
    edge_x.extend([x_coords[i], x_coords[i+1], None])
    edge_y.extend([y_coords[i], y_coords[i+1], None])

fig_flow = go.Figure()
# Añadir flechas
fig_flow.add_trace(go.Scatter(x=edge_x, y=edge_y, mode='lines+markers', 
                               line=dict(color='#3b82f6', width=3), marker=dict(size=10), 
                               hoverinfo='none', showlegend=False))
# Añadir nodos
fig_flow.add_trace(go.Scatter(x=x_coords, y=y_coords, mode='markers+text',
                              marker=dict(size=40, color='#1e3a8a', symbol='square'),
                              text=nodes, textposition="bottom center",
                              textfont=dict(family="Montserrat", size=12, color="black"),
                              hoverinfo='text', hovertext=nodes))

fig_flow.update_layout(
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    plot_bgcolor='rgba(0,0,0,0)',
    height=300, margin=dict(l=20, r=20, t=20, b=20)
)
st.plotly_chart(fig_flow, use_container_width=True)

st.markdown("---")

st.header("🛠️ Metodología Detallada")
st.markdown("""
#### ⚙️ El Proceso Paso a Paso:

1. **Captura de Datos $\rightarrow$** Utilizamos conectores automatizados que consultan APIs de noticias y feeds RSS. Esta información "bruta" (títulos y descripciones) se guarda en una base de datos **SQLite** usando **SQLAlchemy** para asegurar que no se pierda ninguna noticia relevante.

2. **Refinamiento $\rightarrow$** El texto bruto es ruidoso. Aplicamos la librería `re` (expresiones regulares) para:
    - Convertir todo a minúsculas.
    - Eliminar signos de puntuación.
    - Filtrar *Stop Words* (palabras como "el", "la", "de") que no aportan significado.
    - Mantener solo palabras de 4 o más letras para evitar errores semánticos.

3. **Modelado de Análisis $\rightarrow$** Una vez limpio el texto, aplicamos dos enfoques:
    - **Análisis de Frecuencia:** Usamos la clase `collections.Counter` para contar cuántas veces aparece cada palabra. Esto nos dice exactamente qué temas están dominando la agenda informativa.
    - **Modelo de WordCloud:** Implementamos la librería `WordCloud` para generar una representación visual donde el tamaño de la palabra indica su importancia estadística.

4. **Entrega de Valor $\rightarrow$** Los resultados se proyectan en este Dashboard mediante **Plotly** y **Matplotlib**, convirtiendo miles de palabras en una sola imagen comprensible para la toma de decisiones.
""")

st.markdown("---")
st.header("📝 Resumen de Logros")
st.markdown("""
### 🚀 Hitos del Desarrollo
- **Infraestructura OSINT:** Implementación de un flujo de ingesta masiva de datos desde fuentes abiertas.
- **Pipeline de NLP:** Desarrollo de un proceso de limpieza y tokenización robusto.
- **Inteligencia Visual:** Creación de herramientas de análisis de tendencias basadas en frecuencia y nubes semánticas.
- **Interfaz Profesional:** Despliegue de un panel de control interactivo y responsivo.
""")

# --- Carga de Datos ---
@st.cache_data(ttl=600)
def load_nlp_data():
    session = get_session()
    try:
        # Obtenemos el texto de todos los artículos
        articles = session.query(NewsArticle.title, NewsArticle.description).all()
        if not articles:
            return ""
        
        texts = []
        for title, desc in articles:
            # Asegurar que title no sea None
            t = title if title else ""
            d = desc if desc else ""
            texts.append(f"{t} {d}")
            
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
    st.plotly_chart(fig_bar, width='stretch')

    st.caption("Nota: Este análisis se basa en la frecuencia bruta de términos. Para un análisis de tópicos más avanzado, se sugiere el uso de LDA (Latent Dirichlet Allocation).")
else:
    st.warning("No hay datos suficientes en la base de datos para generar el análisis NLP.")