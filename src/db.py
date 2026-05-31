import os
import json
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, func
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Ruta absoluta al osint.db en la raiz del proyecto
    _project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _db_path = os.path.join(_project_root, "osint.db")
    print(f"[AVISO] DATABASE_URL no encontrada en .env. Usando SQLite: {_db_path}")
    DATABASE_URL = f"sqlite:///{_db_path}"

# Set up the engine and declarative base
engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()

class NewsArticle(Base):
    __tablename__ = 'news_articles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    title_es = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    description_es = Column(Text, nullable=True)
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

class AircraftState(Base):
    __tablename__ = 'aircraft_states'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    icao24 = Column(String(10), nullable=False)
    callsign = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    time = Column(String(50), nullable=True)
    lon = Column(Float, nullable=True)
    lat = Column(Float, nullable=True)
    alt = Column(Float, nullable=True)
    vel = Column(Float, nullable=True)
    track = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    """Create the tables in the database if they don't exist."""
    print("Inicializando la base de datos...")
    Base.metadata.create_all(engine)
    print("Base de datos inicializada correctamente.")

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    """Helper function to get a database session."""
    return SessionLocal()

class DatabaseManager:
    def __init__(self):
        self.engine = engine
        self.Session = SessionLocal

    def get_latest_news(self, limit=10):
        session = self.Session()
        try:
            articles = session.query(NewsArticle).order_by(NewsArticle.published_at.desc()).limit(limit).all()
            return [
                {
                    "title": a.title_es or a.title,
                    "source": a.source,
                    "date": a.published_at.strftime('%Y-%m-%d') if a.published_at else "N/A",
                    "url": a.url
                } for a in articles
            ]
        finally:
            session.close()

    def get_timeline_events(self):
        session = self.Session()
        try:
            # Aggregate counts by day
            results = session.query(
                func.date(NewsArticle.published_at).label('date'),
                func.count(NewsArticle.id).label('count')
            ).group_by('date').order_by('date').all()

            timeline = []
            for date_val, count in results:
                # Get a representative article for that day
                rep = session.query(NewsArticle).filter(func.date(NewsArticle.published_at) == date_val).first()
                timeline.append({
                    "date": str(date_val),
                    "count": count,
                    "title": rep.title_es or rep.title if rep else "Eventos múltiples",
                    "url": rep.url if rep else "#"
                })
            return timeline
        finally:
            session.close()

    def get_nlp_entities(self):
        session = self.Session()
        try:
            analyses = session.query(NewsAnalysis).all()
            entity_counts = {}

            for a in analyses:
                # Process Locations
                if a.locations:
                    try:
                        locs = json.loads(a.locations)
                        for l in locs:
                            entity_counts[l] = entity_counts.get(l, 0) + 1
                    except: pass
                
                # Process Organizations
                if a.organizations:
                    try:
                        orgs = json.loads(a.organizations)
                        for o in orgs:
                            entity_counts[o] = entity_counts.get(o, 0) + 1
                    except: pass

            # Sort and format
            sorted_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)
            return [{"entity": e, "count": c, "label": "ENT"} for e, c in sorted_entities]
        finally:
            session.close()

    def get_all_flights(self):
        """Retrieve the most recent snapshot of aircraft states."""
        session = self.Session()
        try:
            # Get the latest timestamp available
            last_update = session.query(func.max(AircraftState.created_at)).scalar()
            if not last_update:
                return []
            
            # Use a small window or exact match, but ensure we get all records for that snapshot
            flights = session.query(AircraftState).filter(AircraftState.created_at == last_update).all()
            
            # Fallback: if exact match failed due to precision, get the most recent 200 records
            if not flights:
                flights = session.query(AircraftState).order_by(AircraftState.created_at.desc()).limit(200).all()

            return [
                {
                    "icao24": f.icao24,
                    "callsign": f.callsign,
                    "country": f.country,
                    "lon": f.lon,
                    "lat": f.lat,
                    "alt": f.alt,
                    "vel": f.vel,
                    "track": f.track,
                    "time": f.time
                } for f in flights
            ]
        finally:
            session.close()

    def save_flights_data(self, states_list):
        """Save a new snapshot of aircraft states to the database."""
        session = self.Session()
        try:
            now = datetime.datetime.utcnow()
            new_states = []
            for s in states_list:
                new_states.append(AircraftState(
                    icao24=s[0] if len(s) > 0 else None,
                    callsign=s[1] if len(s) > 1 else None,
                    country=s[2] if len(s) > 2 else None,
                    time=str(s[3]) if len(s) > 3 else None,
                    lon=s[5] if len(s) > 5 else None,
                    lat=s[6] if len(s) > 6 else None,
                    alt=s[7] if len(s) > 7 else None,
                    vel=s[9] if len(s) > 9 else None,
                    track=s[10] if len(s) > 10 else None,
                    created_at=now
                ))
            session.add_all(new_states)
            session.commit()
            print(f"[DB] Saved {len(new_states)} aircraft states.")
            return True
        except Exception as e:
            print(f"[DB] Error saving flights: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def update_timeline_data(self):
        print("[DB] Actualizando datos de Timeline (Simulado)")
        return True

    def update_nlp_data(self):
        print("[DB] Actualizando datos de NLP (Simulado)")
        return True

# Instantiate the manager as 'db' for api/index.py
db = DatabaseManager()

if __name__ == "__main__":
    init_db()