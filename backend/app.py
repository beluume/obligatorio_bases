from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuración de BD
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': 'manuelmanuel',
    'database': os.getenv('DB_NAME', 'ucu_salas'),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


# ENDPOINTS

@app.route('/')
def home():
    return jsonify({
        'message': 'API Sistema de Salas - UCU',
        'status': 'Funcionando',
        'endpoints': [
            'GET /api/health',
            'GET /api/participantes',
            'GET /api/salas',
            'GET /api/reservas',
            'GET /api/edificios',
            'GET /api/turnos',
            'GET /api/facultades',
            'GET /api/programas',
            'GET /api/sanciones'
        ]
    })

@app.route('/api/health')
def health():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'db_name': db_name[0] if db_name else 'unknown'
        })
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

# PARTICIPANTES

@app.route('/api/participantes', methods=['GET'])
def get_participantes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT p.ci, p.nombre, p.apellido, p.email,
                   ppa.nombre_programa, ppa.rol,
                   pa.tipo as tipo_programa
            FROM participante p
            LEFT JOIN participante_programa_academico ppa ON p.ci = ppa.ci_participante
            LEFT JOIN programa_academico pa ON ppa.nombre_programa = pa.nombre_programa
            ORDER BY p.apellido, p.nombre
        """
        cursor.execute(query)
        participantes = cursor.fetchall()
        cursor.close()
        conn.close()
        
        print(f"✓ Participantes consultados: {len(participantes)}")
        return jsonify({'success': True, 'data': participantes, 'count': len(participantes)})
    except Exception as e:
        print(f"✗ Error en participantes: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# SALAS

@app.route('/api/salas', methods=['GET'])
def get_salas():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT s.nombre_sala, s.edificio, s.capacidad, s.tipo_sala,
                   e.direccion, e.departamento
            FROM sala s
            JOIN edificio e ON s.edificio = e.nombre_edificio
            ORDER BY s.edificio, s.nombre_sala
        """
        cursor.execute(query)
        salas = cursor.fetchall()
        cursor.close()
        conn.close()
        
        print(f"✓ Salas consultadas: {len(salas)}")
        return jsonify({'success': True, 'data': salas, 'count': len(salas)})
    except Exception as e:
        print(f"✗ Error en salas: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# RESERVAS

@app.route('/api/reservas', methods=['GET'])
def get_reservas():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT r.id_reserva, r.nombre_sala, r.edificio, r.fecha, r.estado,
                   t.hora_inicio, t.hora_fin,
                   GROUP_CONCAT(CONCAT(p.nombre, ' ', p.apellido) SEPARATOR ', ') as participantes,
                   COUNT(DISTINCT rp.ci_participante) as num_participantes
            FROM reserva r
            JOIN turno t ON r.id_turno = t.id_turno
            LEFT JOIN reserva_participante rp ON r.id_reserva = rp.id_reserva
            LEFT JOIN participante p ON rp.ci_participante = p.ci
            GROUP BY r.id_reserva, r.nombre_sala, r.edificio, r.fecha, r.estado,
                     t.hora_inicio, t.hora_fin
            ORDER BY r.fecha DESC, t.hora_inicio
        """
        cursor.execute(query)
        reservas = cursor.fetchall()
        cursor.close()
        conn.close()
        
        print(f"✓ Reservas consultadas: {len(reservas)}")
        return jsonify({'success': True, 'data': reservas, 'count': len(reservas)})
    except Exception as e:
        print(f"✗ Error en reservas: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# EDIFICIOS

@app.route('/api/edificios', methods=['GET'])
def get_edificios():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM edificio ORDER BY nombre_edificio"
        cursor.execute(query)
        edificios = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': edificios})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# TURNOS

@app.route('/api/turnos', methods=['GET'])
def get_turnos():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM turno ORDER BY hora_inicio"
        cursor.execute(query)
        turnos = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': turnos})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# FACULTADES


@app.route('/api/facultades', methods=['GET'])
def get_facultades():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM facultad ORDER BY nombre"
        cursor.execute(query)
        facultades = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': facultades})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# PROGRAMAS ACADÉMICOS
# ============================================

@app.route('/api/programas', methods=['GET'])
def get_programas():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT pa.nombre_programa, pa.tipo, pa.id_facultad,
                   f.nombre as nombre_facultad
            FROM programa_academico pa
            JOIN facultad f ON pa.id_facultad = f.id_facultad
            ORDER BY f.nombre, pa.nombre_programa
        """
        cursor.execute(query)
        programas = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': programas})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# SANCIONES
# ============================================

@app.route('/api/sanciones', methods=['GET'])
def get_sanciones():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT s.id_sancion, s.ci_participante, s.fecha_inicio, s.fecha_fin, s.motivo,
                   p.nombre, p.apellido, p.email
            FROM sancion_participante s
            JOIN participante p ON s.ci_participante = p.ci
            ORDER BY s.fecha_inicio DESC
        """
        cursor.execute(query)
        sanciones = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': sanciones})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 70)
    print("  🏛️  SISTEMA DE GESTIÓN DE SALAS - UCU")
    print("  Backend API REST - Python Flask")
    print("=" * 70)
    print(f"  URL: http://localhost:5000")
    print(f"   Base de datos: {DB_CONFIG['database']}")
    print(f"   Debug mode: ON")
    print("=" * 70)
    print("\n  Endpoints disponibles:")
    print("    GET  /                     - Info del API")
    print("    GET  /api/health           - Health check")
    print("    GET  /api/participantes    - Listar participantes")
    print("    GET  /api/salas            - Listar salas")
    print("    GET  /api/reservas         - Listar reservas")
    print("    GET  /api/edificios        - Listar edificios")
    print("    GET  /api/turnos           - Listar turnos")
    print("    GET  /api/facultades       - Listar facultades")
    print("    GET  /api/programas        - Listar programas")
    print("    GET  /api/sanciones        - Listar sanciones")
    print("=" * 70)
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=True)