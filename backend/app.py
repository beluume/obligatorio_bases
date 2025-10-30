from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'salas_app'),
    'password': os.getenv('DB_PASSWORD', 'SalasUCU2025!'),
    'database': os.getenv('DB_NAME', 'salas_estudio_ucu')
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/')
def home():
    return jsonify({'message': 'API Sistema de Salas - UCU', 'status': 'Avance 31/10'})

@app.route('/api/health')
def health():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/api/participantes', methods=['GET'])
def get_participantes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM participante LIMIT 10")
        participantes = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'data': participantes})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/participantes', methods=['POST'])
def create_participante():
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query_login = "INSERT INTO login (correo, contrasena) VALUES (%s, %s)"
        cursor.execute(query_login, (data['email'], 'temp123'))
        
        query_part = "INSERT INTO participante (ci, nombre, apellido, email, telefono) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query_part, (data['ci'], data['nombre'], data['apellido'], data['email'], data.get('telefono')))
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Participante creado'}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/salas', methods=['GET'])
def get_salas():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM sala")
        salas = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'data': salas})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("Backend corriendo en: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)