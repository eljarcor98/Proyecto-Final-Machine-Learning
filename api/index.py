from flask import Flask, render_template, jsonify, request
import os
from src.db import db  # Import the database connection utility

app = Flask(__name__)

# --- VIEW ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/radar')
def radar():
    return render_template('radar.html')

@app.route('/timeline')
def timeline():
    return render_template('timeline.html')

@app.route('/nlp')
def nlp():
    return render_template('nlp.html')

# --- API DATA ROUTES ---

@app.route('/api/radar-data')
def radar_data():
    try:
        # Fetch flights from the database
        # Expected: List of dicts with lat, lon, callsign, type, etc.
        flights = db.get_all_flights() 
        return jsonify(flights)
    except Exception as e:
        print(f"Error fetching radar data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/timeline-data')
def timeline_data():
    try:
        # Fetch aggregated event counts by date
        # Expected: List of dicts [{ 'date': '2024-01-01', 'count': 5, 'title': '...', 'url': '...' }]
        data = db.get_timeline_events()
        return jsonify(data)
    except Exception as e:
        print(f"Error fetching timeline data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/nlp-data')
def nlp_data():
    try:
        # Fetch Named Entities (NER) data
        # Expected: List of dicts [{ 'entity': 'Israel', 'label': 'LOC', 'count': 120 }]
        data = db.get_nlp_entities()
        return jsonify(data)
    except Exception as e:
        print(f"Error fetching NLP data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/news')
def news_data():
    try:
        # Fetch latest news headlines
        news = db.get_latest_news()
        return jsonify(news)
    except Exception as e:
        print(f"Error fetching news: {e}")
        return jsonify({"error": str(e)}), 500

# --- REFRESH ENDPOINTS (POST) ---

@app.route('/api/refresh-radar', methods=['POST'])
def refresh_radar():
    try:
        # Logic to trigger a new scrape/update of flights
        db.update_flights_data() 
        return jsonify({"status": "success", "message": "Radar data updated"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/refresh-timeline', methods=['POST'])
def refresh_timeline():
    try:
        # Logic to trigger a new scrape/update of events
        db.update_timeline_data()
        return jsonify({"status": "success", "message": "Timeline data updated"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/refresh-nlp', methods=['POST'])
def refresh_nlp():
    try:
        # Logic to trigger a new NLP processing run
        db.update_nlp_data()
        return jsonify({"status": "success", "message": "NLP data updated"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Vercel expects the app object
# The runtime will handle the port and address