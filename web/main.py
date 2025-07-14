from flask import Flask, render_template, jsonify
import requests
import os

app = Flask(__name__)

# Konfiguration
API_BASE_URL = "http://localhost:8080/api/"

@app.route('/')
def index():
    """Hauptseite des Web-Interfaces"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Proxy für API Status Abfrage"""
    try:
        response = requests.get(f"{API_BASE_URL}/status", timeout=5)
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({"error": f"API nicht erreichbar: {str(e)}"}), 500

@app.route('/health')
def health_check():
    """Health Check für den Flask Server"""
    return jsonify({
        "status": "healthy",
        "service": "web-interface",
        "api_url": API_BASE_URL
    })

if __name__ == '__main__':
    app.run(host='localhost', port=8001, debug=True)
