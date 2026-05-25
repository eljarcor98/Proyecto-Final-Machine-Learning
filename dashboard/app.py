import streamlit as st
import pandas as pd
import pydeck as pdk
import airportsdata
import os
import json
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Page config
st.set_page_config(page_title="Radar OSINT", layout="wide")

# Autorefresh cada 60 segundos para no saturar
st_autorefresh(interval=60000, key="radar_refresh")

st.title("🛰️ Radar de Inteligencia OSINT")

tab1, tab2, tab3 = st.tabs(["🛰️ Radar Aéreo", "🗺️ Timeline del Conflicto", "📊 Análisis NLP (EDA)"])

with tab1:
    # --- Session State ---
    if 'history' not in st.session_state:
        st.session_state.history = {}
    if 'selected_icao' not in st.session_state:
        st.session_state.selected_icao = None

    def update_data_manual():
        with st.spinner("Actualizando datos de radar..."):
            os.system("py scripts/fetch_opensky_data.py")
        st.success("Radar actualizado")

    # Sidebar: Control y Estado
    st.sidebar.title("🎮 Controles")
    if st.sidebar.button("🔄 Actualizar Radar Ahora"):
        update_data_manual()

    st.sidebar.markdown("---")
    st.sidebar.subheader("🤖 Estado del Orquestador")
    st.sidebar.info("El orquestador automatiza GNews, RSS y GDELT.")
    st.sidebar.caption("Sugerencia: Ejecuta `py scripts/orchestrator.py` en tu servidor para automatización total.")

    def load_data():
        data_dir = 'data/raw'
        if not os.path.exists(data_dir):
            return pd.DataFrame()
        files = [f for f in os.listdir(data_dir) if f.startswith('opensky_states_')]
        if not files: return pd.DataFrame()
        latest = sorted(files, reverse=True)[0]
        try:
            with open(os.path.join(data_dir, latest), 'r') as f:
                data = json.load(f)
            return pd.DataFrame(data, columns=['icao24', 'callsign', 'country', 'time', 'contact', 'lon', 'lat', 'alt', 'ground', 'vel', 'track', 'vert', 'sensors', 'geo_alt', 'squawk', 'spi', 'pos_src'])
        except:
            return pd.DataFrame()

    df = load_data()

    if not df.empty:
        # Update History
        for _, row in df.iterrows():
            icao = row['icao24']
            if icao not in st.session_state.history: st.session_state.history[icao] = []
            pos = [row['lon'], row['lat']]
            if not st.session_state.history[icao] or st.session_state.history[icao][-1] != pos:
                st.session_state.history[icao].append(pos)
                if len(st.session_state.history[icao]) > 30: st.session_state.history[icao].pop(0)

        def get_color(icao):
            if icao == st.session_state.selected_icao:
                return [255, 0, 255, 255] # Magenta
            return [0, 128, 255, 200]    # Azul

        df['fill_color'] = df['icao24'].apply(get_color)

        layers = []
        layers.append(pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position="[lon, lat]",
            get_color="[200, 200, 200, 30]",
            get_radius=5000,
        ))

        if st.session_state.selected_icao:
            trace = st.session_state.history.get(st.session_state.selected_icao, [])
            if len(trace) > 1:
                layers.append(pdk.Layer(
                    "PathLayer",
                    data=[{"path": trace}],
                    get_path="path",
                    get_color="[255, 0, 255, 255]",
                    get_width=5,
                ))

        layers.append(pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position="[lon, lat]",
            get_fill_color="fill_color",
            get_radius=15000,
            pickable=True,
            id="planes"
        ))

        view = pdk.ViewState(latitude=33, longitude=45, zoom=4, pitch=0)
        r = pdk.Deck(layers=layers, initial_view_state=view, map_style="light", tooltip={"text": "{callsign}\nPaís: {country}"})
        
        selection = st.pydeck_chart(r, on_select="rerun", selection_mode="single-object")
        
        if selection and selection.get("selection", {}).get("objects", {}).get("planes"):
            new_icao = selection["selection"]["objects"]["planes"][0]['icao24']
            if st.session_state.selected_icao != new_icao:
                st.session_state.selected_icao = new_icao
                st.rerun()

        if st.session_state.selected_icao:
            sel_row = df[df['icao24'] == st.session_state.selected_icao]
            if not sel_row.empty:
                st.sidebar.success(f"Seguimiento: {sel_row.iloc[0]['callsign']}")
                if st.sidebar.button("❌ Dejar de seguir"): 
                    st.session_state.selected_icao = None
                    st.rerun()
        
        st.markdown("---")
        st.subheader("📰 Últimas Noticias de Inteligencia")
        
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from src.db import get_session, NewsArticle, engine
        from sqlalchemy import desc

        session = get_session()
        try:
            articles = session.query(NewsArticle).order_by(desc(NewsArticle.published_at)).limit(10).all()
            cols = st.columns(2)
            for i, art in enumerate(articles):
                with cols[i % 2]:
                    with st.expander(f"{art.source} | {art.title[:60]}..."):
                        st.write(f"**Publicado:** {art.published_at}")
                        st.write(art.description or "Sin descripción")
                        st.link_button("Ver noticia completa", art.url)
        except Exception as e:
            st.error(f"Error cargando noticias: {e}")
        finally:
            session.close()

        st.sidebar.caption(f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")
    else:
        st.warning("Esperando datos de radar... Pulsa 'Actualizar' en la barra lateral si es necesario.")

with tab2:
    st.header("🗺️ Evolución del Conflicto en el Mapa")
    st.write("Visualización temporal de las ubicaciones extraídas de las noticias.")
    
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.db import engine

    @st.cache_data
    def load_timeline_data():
        query = """
        SELECT a.published_at, n.locations 
        FROM news_articles a 
        JOIN news_analysis n ON a.id = n.article_id 
        WHERE a.published_at IS NOT NULL AND n.locations IS NOT NULL
        """
        try:
            df_tl = pd.read_sql(query, engine)
            df_tl['date'] = pd.to_datetime(df_tl['published_at']).dt.date
            return df_tl
        except Exception as e:
            st.error("Error cargando base de datos")
            return pd.DataFrame()
            
    df_tl = load_timeline_data()
    
    cache_path = 'data/processed/locations_cache.json'
    if not df_tl.empty and os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            loc_cache = json.load(f)
            
        # Transformar data para PyDeck
        map_data = []
        for _, row in df_tl.iterrows():
            if row['locations']:
                try:
                    locs = json.loads(row['locations'])
                    for loc in locs:
                        if loc in loc_cache and loc_cache[loc]:
                            map_data.append({
                                'date': row['date'],
                                'loc_name': loc,
                                'lat': loc_cache[loc]['lat'],
                                'lon': loc_cache[loc]['lon']
                            })
                except:
                    pass
                    
        df_map = pd.DataFrame(map_data)
        
        if not df_map.empty:
            dates = sorted(df_map['date'].unique())
            if dates:
                selected_date = st.slider("Selecciona la fecha:", min_value=dates[0], max_value=dates[-1], value=dates[-1])
                
                df_day = df_map[df_map['date'] == selected_date]
                # Agrupar por coordenada para dar intensidad al punto
                df_grouped = df_day.groupby(['lat', 'lon', 'loc_name']).size().reset_index(name='mentions')
                
                # Mapa
                view_map = pdk.ViewState(latitude=33, longitude=45, zoom=3, pitch=45)
                
                layer = pdk.Layer(
                    "ColumnLayer",
                    data=df_grouped,
                    get_position="[lon, lat]",
                    get_elevation="mentions",
                    elevation_scale=10000,
                    radius=50000,
                    get_fill_color="[255, mentions * 10, 0, 200]",
                    pickable=True,
                    auto_highlight=True,
                )
                
                st.pydeck_chart(pdk.Deck(
                    layers=[layer],
                    initial_view_state=view_map,
                    tooltip={"text": "{loc_name}\nMenciones: {mentions}"}
                ))
                
                st.dataframe(df_grouped.sort_values(by='mentions', ascending=False).head(10)[['loc_name', 'mentions']])
        else:
            st.info("No hay datos geocodificados aún.")
    else:
        st.info("Construyendo caché de ubicaciones... Ejecuta el geocoder en backend.")

with tab3:
    st.header("📊 Análisis Exploratorio de Datos (NLP)")
    st.write("Visualización de las métricas extraídas y analizadas por el modelo de Procesamiento de Lenguaje Natural.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if os.path.exists("timeline.png"):
            st.image("timeline.png", caption="Volumen de Noticias por Día")
        else:
            st.info("Genera el timeline con notebooks/01_nlp_eda.py")
            
        if os.path.exists("locations.png"):
            st.image("locations.png", caption="Top 20 Lugares y Entidades Geográficas")
            
    with col2:
        if os.path.exists("topics.png"):
            st.image("topics.png", caption="Distribución de Tópicos Generales")
            
        if os.path.exists("topics_timeline.png"):
            st.image("topics_timeline.png", caption="Evolución de Tópicos en el Tiempo")
