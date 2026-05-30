import streamlit as st
import pandas as pd
import pydeck as pdk
import os
import sys
from datetime import datetime

# Ajustar ruta para importar desde src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db import get_session, NewsArticle

st.set_page_config(page_title="Timeline del Conflicto", layout="wide", page_icon="⏳")

st.title("⏳ Línea de Tiempo del Conflicto")
st.markdown("Visualización geo-temporal de eventos críticos y noticias relacionadas.")

# --- Carga de Datos ---
@st.cache_data(ttl=600)
def load_timeline_data():
    session = get_session()
    try:
        # Obtenemos artículos que tengan coordenadas
        articles = session.query(NewsArticle).filter(NewsArticle.latitude != None, NewsArticle.longitude != None).all()
        data = []
        for art in articles:
            data.append({
                "id": art.id,
                "title": art.title,
                "description": art.description,
                "url": art.url,
                "source": art.source,
                "published_at": art.published_at,
                "lat": art.latitude,
                "lon": art.longitude
            })
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error al cargar datos de la línea de tiempo: {e}")
        return pd.DataFrame()
    finally:
        session.close()

df = load_timeline_data()

if not df.empty:
    # Convertir fechas a datetime
    df['published_at'] = pd.to_datetime(df['published_at'])
    min_date = df['published_at'].min()
    max_date = df['published_at'].max()

    # --- UI: Filtro Temporal ---
    st.sidebar.header("📅 Filtro Temporal")
    selected_date = st.sidebar.slider(
        "Seleccione la fecha de corte", 
        min_value=min_date.date(), 
        max_value=max_date.date(), 
        value=max_date.date()
    )

    # Filtrar datos según fecha
    filtered_df = df[df['published_at'].dt.date <= selected_date]

    # --- Mapa Interactivo ---
    # Capa de puntos
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered_df,
        get_position="[lon, lat]",
        get_color="[255, 0, 0, 160]",
        get_radius=100000, # 100km
        pickable=True,
        id="news_points"
    )

    view = pdk.ViewState(latitude=32, longitude=45, zoom=3, pitch=0)
    r = pdk.Deck(
        layers=[layer], 
        initial_view_state=view, 
        map_style="dark", 
        tooltip={"text": "{title}\nFuente: {source}"}
    )

    # Renderizado con captura de selección
    selection = st.pydeck_chart(r, on_select="rerun", selection_mode="single-object")

    # --- Implementación de Resumen Interactivo ---
    if selection and selection.get("selection", {}).get("objects", {}).get("news_points"):
        # Obtener la información del objeto seleccionado
        selected_point = selection["selection"]["objects"]["news_points"][0]
        art_id = selected_point.get('id')
        
        # Buscar el artículo en el DataFrame
        if art_id is not None:
            art_info = filtered_df[filtered_df['id'] == art_id].iloc[0]
            
            st.sidebar.markdown("---")
            st.sidebar.subheader("📄 Resumen del Evento")
            st.sidebar.markdown(f"**{art_info['title']}**")
            st.sidebar.caption(f"Fuente: {art_info['source']} | Fecha: {art_info['published_at'].strftime('%Y-%m-%d')}")
            st.sidebar.write(art_info['description'] or "Sin descripción disponible.")
            st.sidebar.link_button("Leer artículo completo", art_info['url'])
    else:
        st.sidebar.info("Haz clic en un punto rojo del mapa para ver el resumen de la noticia.")

    # --- Tabla de Eventos Recientes ---
    st.markdown("---")
    st.subheader("📝 Listado de Eventos hasta la Fecha Seleccionada")
    st.dataframe(
        filtered_df[['published_at', 'title', 'source']].sort_values('published_at', ascending=False),
        use_container_width=True
    )

else:
    st.warning("No se encontraron datos geocodificados para generar la línea de tiempo.")