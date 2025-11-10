"""
Minimal health check server for debugging Railway deployment
Run this to verify basic Flask functionality works
"""
import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'message': 'Basic Flask server running'})

@app.route('/')
def index():
    return jsonify({'message': 'MemeBot Backend', 'port': os.getenv('PORT', '8000')})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    print(f"Starting minimal health check server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
