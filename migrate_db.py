import os
from src.db import engine

def migrate():
    print("Iniciando proceso de migración...")
    try:
        with engine.connect() as conn:
            print("Conexión establecida. Verificando columnas de traducción...")
            # Check for title_es in PostgreSQL
            res_title = conn.execute("SELECT column_name FROM information_schema.columns WHERE table_name='news_articles' AND column_name='title_es'").fetchall()
            
            if not res_title:
                print("Agregando columna title_es...")
                conn.execute("ALTER TABLE news_articles ADD COLUMN title_es TEXT")
                conn.commit()
            else:
                print("Columna title_es ya existe.")
                
            # Check for description_es in PostgreSQL
            res_desc = conn.execute("SELECT column_name FROM information_schema.columns WHERE table_name='news_articles' AND column_name='description_es'").fetchall()
            
            if not res_desc:
                print("Agregando columna description_es...")
                conn.execute("ALTER TABLE news_articles ADD COLUMN description_es TEXT")
                conn.commit()
            else:
                print("Columna description_es ya existe.")
        print("Migración completada exitosamente.")
    except Exception as e:
        print(f"ERROR DURANTE LA MIGRACIÓN: {e}")

if __name__ == "__main__":
    migrate()