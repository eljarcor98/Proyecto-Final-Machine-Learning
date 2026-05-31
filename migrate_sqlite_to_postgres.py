import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def migrate():
    # Get target PostgreSQL URL
    target_url = os.getenv("DATABASE_URL")
    if not target_url:
        print("Error: DATABASE_URL not found in .env file.")
        return

    # Local SQLite path
    sqlite_path = "osint.db"
    if not os.path.exists(sqlite_path):
        print(f"Error: Local database file {sqlite_path} not found.")
        return

    source_url = f"sqlite:///{sqlite_path}"

    print(f"Starting migration from SQLite ({sqlite_path}) to PostgreSQL...")
    
    try:
        source_engine = create_engine(source_url)
        target_engine = create_engine(target_url)

        tables = ['news_articles', 'news_analysis']

        with source_engine.connect() as source_conn, target_engine.connect() as target_conn:
            # Start a transaction for the target
            trans = target_conn.begin()
            try:
                for table in tables:
                    print(f"Migrating table: {table}...")
                    
                    # Fetch all data from source
                    result = source_conn.execute(text(f"SELECT * FROM {table}"))
                    rows = result.fetchall()
                    
                    if not rows:
                        print(f"No data found in {table}, skipping.")
                        continue
                    
                    # Get column names
                    columns = result.keys()
                    col_names = ", ".join(columns)
                    placeholders = ", ".join([f":{col}" for col in columns])
                    
                    # Construct INSERT statement
                    insert_stmt = text(f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})")
                    
                    # Convert rows to dictionaries for execution
                    data = [dict(zip(columns, row)) for row in rows]
                    
                    # Execute batch insert
                    target_conn.execute(insert_stmt, data)
                    print(f"Successfully migrated {len(data)} rows to {table}.")
                
                trans.commit()
                print("\nMigration completed successfully!")
                
            except Exception as e:
                trans.rollback()
                print(f"\nError during data transfer: {e}")
                raise e

    except Exception as e:
        print(f"Critical error: {e}")

if __name__ == "__main__":
    migrate()