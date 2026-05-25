"""
fetch_gdelt_historical.py
=========================
Descarga noticias de GDELT en lotes mensuales desde una fecha de inicio.
Guarda en la base de datos SQLite (osint.db) evitando duplicados.

Uso:
    py scripts/fetch_gdelt_historical.py

Configura START_DATE y END_DATE según el periodo de interés.
"""

import os
import sys
import requests
import datetime
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db import get_session, NewsArticle, init_db

# ──────────────────────────────────────────────────────────
# CONFIGURACIÓN  ← ajusta estas fechas según el conflicto
# ──────────────────────────────────────────────────────────
START_DATE = datetime.datetime(2025, 10, 1)   # Inicio estimado del conflicto
END_DATE   = datetime.datetime.utcnow()        # Hasta hoy

# Query de búsqueda — términos clave del conflicto
QUERY = '(iran OR israel) (war OR conflict OR strike OR attack OR hormuz OR missile OR nuclear)'

GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
MAX_RECORDS = 250   # Máximo por petición en GDELT
SLEEP_BETWEEN = 3   # Segundos entre peticiones (respetar rate limit)

# ──────────────────────────────────────────────────────────

def date_windows(start: datetime.datetime, end: datetime.datetime, days: int = 7):
    """Divide el rango en ventanas de N días."""
    current = start
    while current < end:
        window_end = min(current + datetime.timedelta(days=days), end)
        yield current, window_end
        current = window_end


def gdelt_fetch_window(start: datetime.datetime, end: datetime.datetime) -> list:
    """Consulta GDELT para una ventana de tiempo. Retorna lista de artículos."""
    params = {
        'query':         QUERY,
        'mode':          'artlist',
        'format':        'json',
        'maxrecords':    MAX_RECORDS,
        'sort':          'datedesc',
        'startdatetime': start.strftime('%Y%m%d%H%M%S'),
        'enddatetime':   end.strftime('%Y%m%d%H%M%S'),
    }
    try:
        resp = requests.get(GDELT_URL, params=params, timeout=60)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('articles', [])
        else:
            print(f"  [HTTP {resp.status_code}] {start.date()} → {end.date()}")
            return []
    except Exception as e:
        print(f"  [ERROR] {e}")
        return []


def parse_gdelt_date(date_str: str):
    """Intenta parsear la fecha de GDELT (formato: 20260515T140000Z)."""
    if not date_str:
        return None
    try:
        return datetime.datetime.strptime(date_str, "%Y%m%dT%H%M%SZ")
    except Exception:
        return None


def save_articles(session, articles: list, window_label: str) -> int:
    """Guarda artículos en la BD, evita duplicados por URL. Retorna insertados."""
    inserted = 0
    for art in articles:
        url = art.get('url', '').strip()
        if not url:
            continue
        # Evitar duplicados
        if session.query(NewsArticle).filter_by(url=url).first():
            continue
        new = NewsArticle(
            source=f"GDELT - {art.get('source', 'Unknown')}",
            title=art.get('title', 'No Title').strip(),
            description='',
            content='',
            url=url,
            published_at=parse_gdelt_date(art.get('seendate', ''))
        )
        session.add(new)
        inserted += 1
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"  [DB ERROR en {window_label}] {e}")
        inserted = 0
    return inserted


def run():
    print("=" * 62)
    print("  GDELT Historical Fetcher")
    print(f"  Desde : {START_DATE.date()}")
    print(f"  Hasta : {END_DATE.date()}")
    print(f"  Query : {QUERY[:60]}...")
    print("=" * 62)

    # Asegurar que las tablas existen
    init_db()

    session = get_session()
    total_inserted = 0
    windows = list(date_windows(START_DATE, END_DATE, days=7))
    total_windows = len(windows)

    try:
        for i, (w_start, w_end) in enumerate(windows, 1):
            label = f"{w_start.strftime('%Y-%m-%d')} al {w_end.strftime('%Y-%m-%d')}"
            print(f"[{i:3d}/{total_windows}] {label}", end=' ... ')

            articles = gdelt_fetch_window(w_start, w_end)
            inserted = save_articles(session, articles, label)
            total_inserted += inserted

            print(f"encontrados: {len(articles):3d} | nuevos: {inserted:3d} | total: {total_inserted}")

            if i < total_windows:
                time.sleep(SLEEP_BETWEEN)

    finally:
        session.close()

    print("\n" + "=" * 62)
    print(f"  DONE — Total artículos nuevos insertados: {total_inserted}")
    print("=" * 62)


if __name__ == "__main__":
    run()
