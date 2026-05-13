import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import datetime

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Set up the engine and declarative base
engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()

class NewsArticle(Base):
    __tablename__ = 'news_articles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    url = Column(String(1000), unique=True, nullable=False)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class NewsAnalysis(Base):
    __tablename__ = 'news_analysis'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, unique=True, nullable=False)
    locations = Column(Text, nullable=True) # JSON list of places
    organizations = Column(Text, nullable=True) # JSON list of orgs
    topic = Column(String(100), nullable=True) # Category
    
def init_db():
    """Create the tables in the database if they don't exist."""
    print("Inicializando la base de datos...")
    Base.metadata.create_all(engine)
    print("Base de datos inicializada correctamente.")

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    """Returns a new database session."""
    return SessionLocal()

if __name__ == "__main__":
    init_db()
