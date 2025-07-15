# Web
from flask import Flask, render_template

app = Flask(__name__)

API_BASE_URL = "http://localhost:8000/api/"

@app.route('/')
def index():
    """Main page of the Web Interface"""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='localhost', port=8001, debug=True)