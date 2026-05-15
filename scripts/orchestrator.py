import schedule
import time
import subprocess
import os
import sys
from datetime import datetime

# Rutas a los scripts
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = {
    "gnews": os.path.join(BASE_DIR, "scripts", "fetch_gnews.py"),
    "rss": os.path.join(BASE_DIR, "scripts", "fetch_rss_news.py"),
    "opensky": os.path.join(BASE_DIR, "scripts", "fetch_opensky_data.py"),
    "gdelt": os.path.join(BASE_DIR, "scripts", "fetch_gdelt_data.py"),
    "acled": os.path.join(BASE_DIR, "scripts", "fetch_acled_data.py"),
    "guardian": os.path.join(BASE_DIR, "scripts", "fetch_guardian_news.py")
}

def run_script(name):
    script_path = SCRIPTS.get(name)
    if not script_path:
        print(f"[{datetime.now()}] Script {name} no encontrado.")
        return

    print(f"[{datetime.now()}] Ejecutando {name}...")
    try:
        # Usamos sys.executable para asegurar que use el mismo entorno python
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[{datetime.now()}] {name} completado exitosamente.")
        else:
            print(f"[{datetime.now()}] Error en {name}: {result.stderr}")
    except Exception as e:
        print(f"[{datetime.now()}] Excepción al ejecutar {name}: {e}")

# --- Programación de Tareas ---

# GNews: Cada 4 horas (6 veces al día = 6 consultas, dentro del límite de 100)
schedule.every(4).hours.do(run_script, name="gnews")

# RSS News: Cada hora
schedule.every(1).hours.do(run_script, name="rss")

# GDELT: Cada 2 horas
schedule.every(2).hours.do(run_script, name="gdelt")

# ACLED: Cada 24 horas (los eventos no cambian minuto a minuto)
schedule.every(24).hours.do(run_script, name="acled")

# The Guardian: Cada 4 horas
schedule.every(4).hours.do(run_script, name="guardian")

# OpenSky: Cada 15 minutos (para mantener el radar actualizado)
schedule.every(15).minutes.do(run_script, name="opensky")

def start_orchestrator():
    print(f"[{datetime.now()}] Orquestador OSINT iniciado.")
    print("Ejecutando primera ronda de captura...")
    
    # Ejecución inicial al arrancar
    run_script("gnews")
    run_script("rss")
    run_script("opensky")
    run_script("acled")
    run_script("guardian")
    
    print("\nEsperando por las siguientes tareas programadas...")
    while True:
        schedule.run_pending()
        time.sleep(60) # Revisar cada minuto

if __name__ == "__main__":
    start_orchestrator()
