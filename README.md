# 🛰️ Proyecto Final ML1: Sistema de Inteligencia Multifuente (OSINT)
## Escenario: Conflicto Irán – Israel – EE. UU.

Este repositorio contiene el desarrollo de un sistema de inteligencia multifuente diseñado para monitorear y analizar la actividad en la región de Medio Oriente, centrándose en el triángulo geopolítico de Irán, Israel y EE. UU. El sistema utiliza técnicas de **Machine Learning** y **OSINT** para extraer conocimiento de fuentes públicas y gratuitas.

---

## 🚀 Avances Actuales
*   **Recolección Automatizada**: Implementación de scripts para la captura de datos en tiempo real.
*   **Radar Aéreo**: Dashboard interactivo capaz de visualizar el tráfico aéreo en zonas de conflicto.
*   **Integración Multifuente**: Conexión con APIs de GDELT (eventos y noticias) y OpenSky (estado de aeronaves).
*   **Repositorio Independiente**: Migración exitosa a este repositorio único para mayor agilidad en el desarrollo.

---

## 📂 Estructura del Proyecto

*   `dashboard/`: 🖥️ Aplicación web interactiva construida con **Streamlit** y **Pydeck**.
*   `scripts/`: ⚙️ Motores de recolección de datos:
    *   `fetch_opensky_data.py`: Captura de estados de vuelos en vivo.
    *   `fetch_gdelt_data.py`: Extracción de eventos noticiosos globales.
    *   `fetch_aviation_data.py`: Cruce de información técnica de aeronaves.
*   `notebooks/`: 📓 Espacio de experimentación y EDA (Análisis Exploratorio de Datos).
*   `data/`: 📊 Almacenamiento organizado por etapas (raw/processed).
*   `models/`: 🧠 Almacenamiento de modelos entrenados para predicción o clasificación.

---

## 🛠️ Requisitos e Instalación

1.  **Clonar el repositorio**:
    ```bash
    git clone https://github.com/eljarcor98/Proyecto-Final-Machine-Learning.git
    ```
2.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configuración de Credenciales**:
    *   Asegúrate de crear un archivo `.env` en la raíz (basado en el archivo de ejemplo) para tus llaves de API.
    *   *Nota: Por seguridad, las credenciales personales no se suben al repositorio.*

---

## 📡 Cómo ejecutar el Radar
Para iniciar el panel interactivo de inteligencia aérea, ejecuta:
```bash
streamlit run dashboard/app.py
```

---

## 🎯 Próximos Pasos (Roadmap)
- [ ] Implementar modelos de detección de anomalías en rutas de vuelo.
- [ ] Realizar Análisis de Sentimiento en los feeds de GDELT para medir la tensión regional.
- [ ] Correlacionar eventos terrestres (GDELT) con picos de tráfico aéreo (OpenSky).
- [ ] Desplegar la aplicación final en Streamlit Cloud o plataforma similar.

---

## 👥 Colaboradores
*   **Arnold Torres** (@eljarcor98)
*   **Nicolás**

---

## 🎓 Contexto Académico
*   **Institución**: Universidad Externado de Colombia.
*   **Curso**: Machine Learning 1.
*   **Docente**: Julián Zuluaga.
