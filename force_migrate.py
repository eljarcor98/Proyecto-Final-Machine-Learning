import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Force load .env from the current directory
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"DATABASE_URL: {DATABASE_URL}")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL no encontrada. La migración no puede proceder.")
    exit(1)

engine = create_engine(DATABASE_URL)

def force_migrate():
    print("Iniciando migración forzada...")
    try:
        with engine.connect() as conn:
            print("Conexión establecida exitosamente.")
            
            # PostgreSQL specific check for column existence
            # Check title_es
            res_title = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='news_articles' AND column_name='title_es'")).fetchall()
            if not res_title:
                print("Agregando columna title_es...")
                conn.execute(text("ALTER TABLE news_articles ADD COLUMN title_es TEXT"))
                conn.commit()
                print("Columna title_es agregada.")
            else:
                print("Columna title_es ya existe.")

            # Check description_es
            res_desc = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='news_articles' AND column_name='description_es'")).fetchall()
            if not res_desc:
                print("Agregando columna description_es...")
                conn.execute(text("ALTER TABLE news_articles ADD COLUMN description_es TEXT"))
                conn.commit()
                print("Columna description_es agregada.")
            else:
                print("Columna description_es ya existe.")
        
        print("Migración forzada completada exitosamente.")
    except Exception as e:
        print(f"ERROR DURANTE LA MIGRACIÓN: {e}")

if __name__ == "__main__":
    force_migrate()