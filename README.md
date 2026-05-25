# 🛰️ Proyecto Final ML1: Sistema de Inteligencia Multifuente (OSINT)
## Escenario: Conflicto Irán – Israel – EE. UU.

Este repositorio contiene el desarrollo de un sistema de inteligencia multifuente diseñado para monitorear y analizar la actividad en la región de Medio Oriente, centrándose en el triángulo geopolítico de Irán, Israel y EE. UU. El sistema utiliza técnicas de **Machine Learning** y **OSINT** para extraer conocimiento de fuentes públicas y gratuitas.

---

## 🚀 Avances Actuales
*   **Recolección Automatizada**: Implementación de scripts para la captura de datos en tiempo real de GNews, RSS y GDELT.
*   **Procesamiento NLP**: Extracción de entidades (ubicaciones) y tópicos mediante NLP (`spacy`) en `src/nlp_utils.py`.
*   **Dashboard Interactivo**: Aplicación web con dos módulos:
    *   **Radar Aéreo**: Tráfico aéreo en zonas de conflicto (vía OpenSky).
    *   **Timeline Geopolítico**: Mapa de calor evolutivo con las menciones geográficas extraídas de las noticias.
*   **Backend en la Nube**: Migración exitosa de SQLite local a **PostgreSQL en Supabase**, permitiendo que todo el equipo comparta y procese la misma base de datos en tiempo real.

---

## 📂 Estructura del Proyecto

*   `dashboard/`: 🖥️ Aplicación web interactiva construida con **Streamlit** y **Pydeck**.
*   `src/`: ⚙️ Utilidades base (Conexión DB, Procesamiento NLP, Geocodificación).
*   `scripts/`: ⚙️ Motores de recolección de datos y orquestadores:
    *   `orchestrator.py`: Orquestador principal que consolida el raspado de GNews, GDELT y RSS.
*   `notebooks/`: 📓 Espacio de experimentación y EDA (Análisis Exploratorio de Datos).
*   `data/`: 📊 Almacenamiento organizado y caché local (ej. caché de coordenadas).

---

## 🛠️ Requisitos e Instalación

1.  **Clonar el repositorio**:
    ```bash
    git clone https://github.com/eljarcor98/Proyecto-Final-Machine-Learning.git
    ```
2.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm
    ```
3.  **Configuración de Credenciales (.env)**:
    *   Debes crear un archivo `.env` en la raíz del proyecto.
    *   **Para conectarte a la base de datos de Supabase compartida con el equipo**, el archivo `.env` debe contener obligatoriamente esta línea:
        ```env
        DATABASE_URL="postgresql://postgres.[PROYECTO]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres"
        ```
    *   *Nota: Pide la URL de conexión exacta (Connection Pooler) a un administrador del equipo.*

---

## 📡 Cómo ejecutar el Proyecto

Para iniciar el panel interactivo (Radar y Timeline), asegúrate de tener activado tu entorno virtual y ejecuta:
```bash
python -m streamlit run dashboard/app.py
```

Para procesar nuevas noticias en la base de datos, ejecuta el orquestador:
```bash
python scripts/orchestrator.py
```

---

## 🎯 Próximos Pasos (Roadmap)
- [x] Extraer ubicaciones y tópicos de noticias (NLP).
- [x] Visualizar un Timeline Geoespacial animado.
- [x] Migrar a Postgres (Supabase) para trabajo colaborativo.
- [ ] Implementar modelos de detección de anomalías en rutas de vuelo.
- [ ] Realizar Análisis de Sentimiento usando `sentence-transformers` para medir la tensión regional.
- [ ] Desplegar la aplicación final en Streamlit Cloud.

---

## 👥 Colaboradores
*   **Arnold Torres** (@eljarcor98)
*   **Nicolás**

---

## 🎓 Contexto Académico
*   **Institución**: Universidad Externado de Colombia.
*   **Curso**: Machine Learning 1.
*   **Docente**: Julián Zuluaga.
