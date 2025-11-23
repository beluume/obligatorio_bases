from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from database import get_connection as get_db_connection

load_dotenv()

app = Flask(__name__)
CORS(app)



# ============================================
# FUNCIÓN PARA DETERMINAR ROL POR EMAIL
# ============================================

def obtener_rol_por_email(email):
    """
    Determina el rol del usuario según el dominio de su email:
    - @correo.ucu.edu.uy → Estudiante de Grado
    - @postgrado.ucu.edu.uy → Estudiante de Posgrado
    - @docentes.ucu.edu.uy → Docente
    """
    email_lower = email.lower()
    
    if '@docentes.ucu.edu.uy' in email_lower:
        return 'docente', 'docente'
    elif '@postgrado.ucu.edu.uy' in email_lower:
        return 'alumno', 'posgrado'
    elif '@correo.ucu.edu.uy' in email_lower:
        return 'alumno', 'grado'
    else:
        # Email genérico @ucu.edu.uy → Estudiante de grado por defecto
        return 'alumno', 'grado'


# ============================================
# ENDPOINTS BASE
# ============================================

@app.route('/')
def home():
    return jsonify({
        'message': 'API Sistema de Salas - UCU',
        'status': 'Funcionando',
        'version': '2.1 - Roles por Email',
        'dominios': {
            'estudiantes_grado': '@correo.ucu.edu.uy',
            'estudiantes_posgrado': '@postgrado.ucu.edu.uy',
            'docentes': '@docentes.ucu.edu.uy'
        }
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
            "database": "connected",
            "db_name": db_name[0] if db_name else None,
            "status": "healthy"
        })
    except Exception as e:
        return jsonify({"database": "error", "error": str(e)}), 500


# ============================================
# ENDPOINT DE LOGIN (ROLES POR EMAIL)
# ============================================

@app.route('/api/login', methods=['POST'])
def login():
    """
    Endpoint de login que asigna el rol según el dominio del email.
    NO valida contraseña (para simplificar el obligatorio).
    """
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'success': False, 'error': 'Email requerido'}), 400
        
        # Determinar rol y tipo por email
        rol, tipo = obtener_rol_por_email(email)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar usuario en la BD
        query = """
            SELECT l.correo, l.ci_participante, p.nombre, p.apellido
            FROM login l
            JOIN participante p ON l.ci_participante = p.ci
            WHERE l.correo = %s
            LIMIT 1
        """
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not user:
            return jsonify({'success': False, 'error': 'Usuario no encontrado en el sistema'}), 404
        
        # Construir respuesta
        return jsonify({
            'success': True,
            'message': 'Login exitoso (sin validación de contraseña)',
            'user': {
                'email': user['correo'],
                'ci': user['ci_participante'],
                'nombre': user['nombre'],
                'apellido': user['apellido'],
                'rol': rol,
                'tipo_usuario': tipo
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



# ============================================
# ENDPOINTS PARA SALAS
# ============================================

@app.route('/api/salas', methods=['GET'])
def get_salas():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                s.nombre_sala,
                s.edificio,
                s.capacidad,
                s.tipo_sala,
                e.direccion,
                e.departamento
            FROM sala s
            LEFT JOIN edificio e
                ON s.edificio = e.nombre_edificio
            ORDER BY s.edificio, s.nombre_sala
        """
        
        cursor.execute(query)
        salas = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': salas})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/salas', methods=['POST'])
def crear_sala():
    try:
        data = request.get_json()
        
        required = ['nombre_sala', 'edificio', 'capacidad', 'tipo_sala']
        for field in required:
            if field not in data or data[field] == '':
                return jsonify({'success': False, 'error': f'Campo requerido: {field}'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO sala (nombre_sala, edificio, capacidad, tipo_sala)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['nombre_sala'],
            data['edificio'],
            data['capacidad'],
            data['tipo_sala']
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Sala creada correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/salas/<nombre_sala>/<edificio>', methods=['PUT'])
def actualizar_sala(nombre_sala, edificio):
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            UPDATE sala
            SET capacidad = %s,
                tipo_sala = %s
            WHERE nombre_sala = %s AND edificio = %s
        """
        cursor.execute(query, (
            data.get('capacidad'),
            data.get('tipo_sala'),
            nombre_sala,
            edificio
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Sala actualizada correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/salas/<nombre_sala>/<edificio>', methods=['DELETE'])
def eliminar_sala(nombre_sala, edificio):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "DELETE FROM sala WHERE nombre_sala = %s AND edificio = %s"
        cursor.execute(query, (nombre_sala, edificio))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Sala eliminada correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/salas/verificar-disponibilidad', methods=['POST'])
def verificar_disponibilidad_sala():
    """
    Verifica si una sala está disponible para un turno y fecha específicos
    """
    try:
        data = request.get_json()
        
        required_fields = ['nombre_sala', 'edificio', 'fecha', 'id_turno']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'error': f'Campo requerido: {field}'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT COUNT(*) AS total
            FROM reserva
            WHERE nombre_sala = %s
              AND edificio = %s
              AND fecha = %s
              AND id_turno = %s
              AND estado = 'activa'
        """
        
        cursor.execute(query, (data['nombre_sala'], data['edificio'], data['fecha'], data['id_turno']))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        disponible = result['total'] == 0
        
        return jsonify({
            'success': True, 
            'disponible': disponible, 
            'message': 'Sala disponible' if disponible else 'Sala ocupada'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



# ============================================
# ENDPOINTS DE TURNOS
# ============================================

@app.route('/api/turnos', methods=['GET'])
def get_turnos():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT id_turno, TIME_FORMAT(hora_inicio, '%H:%i') as hora_inicio, TIME_FORMAT(hora_fin, '%H:%i') as hora_fin FROM turno ORDER BY hora_inicio"
        cursor.execute(query)
        turnos = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': turnos})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



# ============================================
# FUNCIONES AUXILIARES PARA REGLAS DE NEGOCIO
# ============================================

def obtener_resumen_reservas_ci(conn, ci, fecha_reserva):
    """
    Devuelve el total de horas reservadas y la cantidad de reservas activas
    en la semana de la fecha_reserva, para un participante dado.
    Se consideran solo salas de uso libre.
    """
    cursor = conn.cursor(dictionary=True)
    
    # Obtener el rango de la semana (lunes a domingo)
    fecha_dt = datetime.strptime(fecha_reserva, '%Y-%m-%d').date()
    inicio_semana = fecha_dt - timedelta(days=fecha_dt.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    
    query = """
        SELECT 
            COALESCE(SUM(TIMESTAMPDIFF(HOUR, t.hora_inicio, t.hora_fin)), 0) AS horas_semana,
            COUNT(*) AS reservas_semana
        FROM reserva r
        JOIN turno t ON r.id_turno = t.id_turno
        JOIN sala s ON r.nombre_sala = s.nombre_sala AND r.edificio = s.edificio
        WHERE r.fecha BETWEEN %s AND %s
          AND r.estado = 'activa'
          AND s.tipo_sala = 'libre'
          AND r.id_reserva IN (
              SELECT rp.id_reserva
              FROM reserva_participante rp
              WHERE rp.ci_participante = %s
          )
    """
    
    cursor.execute(query, (inicio_semana, fin_semana, ci))
    result = cursor.fetchone()
    cursor.close()
    
    return {
        'horas_semana': float(result['horas_semana']) if result['horas_semana'] else 0,
        'reservas_semana': int(result['reservas_semana']) if result['reservas_semana'] else 0
    }


def verificar_restricciones_estudiante(conn, ci, fecha, id_turno, tipo_usuario):
    """
    Verifica las restricciones de:
    - Máximo 2 horas diarias
    - Máximo 3 reservas activas por semana
    Solo para estudiantes de GRADO y salas de uso libre.
    """
    cursor = conn.cursor(dictionary=True)
    
    # 1) Duración de la nueva reserva
    query_turno = "SELECT TIMESTAMPDIFF(HOUR, hora_inicio, hora_fin) as duracion FROM turno WHERE id_turno = %s"
    cursor.execute(query_turno, (id_turno,))
    turno = cursor.fetchone()
    
    if not turno:
        cursor.close()
        return False, "Turno no encontrado"
    
    # Duración de la nueva reserva en horas (convertir a float si es Decimal)
    nueva_duracion = float(turno['duracion']) if turno['duracion'] else 0
    
    # 2) Total de horas reservadas ese día
    query_horas_dia = """
        SELECT 
            COALESCE(SUM(TIMESTAMPDIFF(HOUR, t.hora_inicio, t.hora_fin)), 0) AS horas_dia
        FROM reserva r
        JOIN turno t ON r.id_turno = t.id_turno
        JOIN sala s ON r.nombre_sala = s.nombre_sala AND r.edificio = s.edificio
        WHERE r.fecha = %s
          AND r.estado = 'activa'
          AND s.tipo_sala = 'libre'
          AND r.id_reserva IN (
              SELECT rp.id_reserva
              FROM reserva_participante rp
              WHERE rp.ci_participante = %s
          )
    """
    
    cursor.execute(query_horas_dia, (fecha, ci))
    result_dia = cursor.fetchone()
    horas_dia_actuales = float(result_dia['horas_dia']) if result_dia['horas_dia'] else 0
    
    if horas_dia_actuales + nueva_duracion > 2:
        cursor.close()
        return False, "Supera el máximo de 2 horas diarias para estudiantes de grado en salas de uso libre."
    
    # 3) Verificar máximo 3 reservas activas por semana
    resumen = obtener_resumen_reservas_ci(conn, ci, fecha)
    if resumen['reservas_semana'] >= 3:
        cursor.close()
        return False, "Supera el máximo de 3 reservas activas por semana para estudiantes de grado en salas de uso libre."
    
    cursor.close()
    return True, "OK"



# ============================================
# ENDPOINTS DE RESERVAS
# ============================================

@app.route('/api/reservas', methods=['GET'])
def get_reservas():
    try:
        # Verificar si se solicita filtrar por CI
        ci_filtro = request.args.get('ci_participante')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if ci_filtro:
            # Obtener solo las reservas del participante específico
            query = """
                SELECT 
                    r.id_reserva,
                    r.nombre_sala,
                    r.edificio,
                    DATE_FORMAT(r.fecha, '%d/%m/%Y') as fecha,
                    TIME_FORMAT(t.hora_inicio, '%H:%i') as hora_inicio,
                    TIME_FORMAT(t.hora_fin, '%H:%i') as hora_fin,
                    r.estado,
                    COUNT(rp.ci_participante) AS cantidad_participantes
                FROM reserva r
                JOIN turno t ON r.id_turno = t.id_turno
                LEFT JOIN reserva_participante rp ON r.id_reserva = rp.id_reserva
                WHERE r.id_reserva IN (
                    SELECT rp2.id_reserva 
                    FROM reserva_participante rp2 
                    WHERE rp2.ci_participante = %s
                )
                GROUP BY 
                    r.id_reserva, r.nombre_sala, r.edificio, r.fecha,
                    t.hora_inicio, t.hora_fin, r.estado
                ORDER BY r.fecha DESC, t.hora_inicio
            """
            cursor.execute(query, (ci_filtro,))
        else:
            # Obtener todas las reservas
            query = """
                SELECT 
                    r.id_reserva,
                    r.nombre_sala,
                    r.edificio,
                    r.fecha,
                    TIME_FORMAT(t.hora_inicio, '%H:%i') as hora_inicio,
                    TIME_FORMAT(t.hora_fin, '%H:%i') as hora_fin,
                    r.estado,
                    COUNT(rp.ci_participante) AS cantidad_participantes
                FROM reserva r
                JOIN turno t ON r.id_turno = t.id_turno
                LEFT JOIN reserva_participante rp ON r.id_reserva = rp.id_reserva
                GROUP BY 
                    r.id_reserva, r.nombre_sala, r.edificio, r.fecha,
                    t.hora_inicio, t.hora_fin, r.estado
                ORDER BY r.fecha DESC, t.hora_inicio
            """
            cursor.execute(query)
        
        reservas = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': reservas})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reservas', methods=['POST'])
def crear_reserva():
    try:
        data = request.get_json()
        
        required_fields = ['nombre_sala', 'edificio', 'fecha', 'id_turno', 'ci_participante', 'email']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'error': f'Campo requerido: {field}'}), 400
        
        email = data['email']
        rol, tipo_usuario = obtener_rol_por_email(email)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar tipo de sala
        query_sala = """
            SELECT tipo_sala
            FROM sala
            WHERE nombre_sala = %s AND edificio = %s
        """
        cursor.execute(query_sala, (data['nombre_sala'], data['edificio']))
        sala = cursor.fetchone()
        
        if not sala:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Sala no encontrada'}), 404
        
        tipo_sala = sala['tipo_sala']
        
        # Reglas por tipo de usuario y tipo de sala
        if tipo_sala == 'posgrado' and tipo_usuario != 'posgrado' and rol != 'docente':
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Solo estudiantes de posgrado y docentes pueden reservar esta sala'}), 403
        
        if tipo_sala == 'docente' and rol != 'docente':
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Solo docentes pueden reservar esta sala'}), 403
        
        # Restricciones de estudiantes de grado en salas de uso libre
        if tipo_usuario == 'grado' and tipo_sala == 'libre':
            ok, msg = verificar_restricciones_estudiante(
                conn,
                data['ci_participante'],
                data['fecha'],
                data['id_turno'],
                tipo_usuario
            )
            if not ok:
                cursor.close()
                conn.close()
                return jsonify({'success': False, 'error': msg}), 403
        
        # Verificar disponibilidad antes de crear
        query_check = """
            SELECT COUNT(*) AS total
            FROM reserva
            WHERE nombre_sala = %s
              AND edificio = %s
              AND fecha = %s
              AND id_turno = %s
              AND estado = 'activa'
        """
        cursor.execute(query_check, (data['nombre_sala'], data['edificio'], data['fecha'], data['id_turno']))
        result = cursor.fetchone()
        
        if result['total'] > 0:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'La sala ya está reservada para ese horario'}), 409
        
        # Crear la reserva
        query_reserva = """
            INSERT INTO reserva (nombre_sala, edificio, fecha, id_turno, estado)
            VALUES (%s, %s, %s, %s, 'activa')
        """
        cursor.execute(query_reserva, (
            data['nombre_sala'],
            data['edificio'],
            data['fecha'],
            data['id_turno']
        ))
        id_reserva = cursor.lastrowid
        
        # Asociar participante
        query_reserva_participante = """
            INSERT INTO reserva_participante (ci_participante, id_reserva, fecha_solicitud_reserva, asistencia)
            VALUES (%s, %s, NOW(), NULL)
        """
        cursor.execute(query_reserva_participante, (data['ci_participante'], id_reserva))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Reserva creada correctamente', 'id_reserva': id_reserva})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reservas/<int:id_reserva>', methods=['PUT'])
def actualizar_reserva(id_reserva):
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            UPDATE reserva
            SET estado = %s
            WHERE id_reserva = %s
        """
        cursor.execute(query, (data.get('estado', 'activa'), id_reserva))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Reserva actualizada correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reservas/<int:id_reserva>', methods=['DELETE'])
def eliminar_reserva(id_reserva):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "DELETE FROM reserva WHERE id_reserva = %s"
        cursor.execute(query, (id_reserva,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Reserva eliminada correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



# ============================================
# ENDPOINTS DE PARTICIPANTES
# ============================================

@app.route('/api/participantes', methods=['GET'])
def get_participantes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT p.ci, p.nombre, p.apellido, p.email
            FROM participante p
            ORDER BY p.apellido, p.nombre
        """
        cursor.execute(query)
        participantes = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': participantes})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/participantes/<ci>', methods=['GET'])
def get_participante(ci):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT p.ci, p.nombre, p.apellido, p.email
            FROM participante p
            WHERE p.ci = %s
        """
        cursor.execute(query, (ci,))
        participante = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not participante:
            return jsonify({'success': False, 'error': 'Participante no encontrado'}), 404
        
        return jsonify({'success': True, 'data': participante})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/participantes', methods=['POST'])
def crear_participante():
    try:
        data = request.get_json()
        
        required = ['ci', 'nombre', 'apellido', 'email']
        for field in required:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'error': f'Campo requerido: {field}'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO participante (ci, nombre, apellido, email)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['ci'],
            data['nombre'],
            data['apellido'],
            data['email']
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Participante creado correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/participantes/<ci>', methods=['PUT'])
def actualizar_participante(ci):
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            UPDATE participante
            SET nombre = %s,
                apellido = %s,
                email = %s
            WHERE ci = %s
        """
        cursor.execute(query, (
            data.get('nombre'),
            data.get('apellido'),
            data.get('email'),
            ci
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Participante actualizado correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/participantes/<ci>', methods=['DELETE'])
def eliminar_participante(ci):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "DELETE FROM participante WHERE ci = %s"
        cursor.execute(query, (ci,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Participante eliminado correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



# ============================================
# ENDPOINTS DE SANCIONES
# ============================================

@app.route('/api/sanciones', methods=['GET'])
def get_sanciones():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                sp.id_sancion,
                sp.ci_participante, 
                p.nombre, 
                p.apellido, 
                p.email,
                sp.fecha_inicio, 
                sp.fecha_fin,
                sp.motivo,
                CASE 
                    WHEN CURDATE() BETWEEN sp.fecha_inicio AND sp.fecha_fin THEN 'Activa'
                    ELSE 'Finalizada'
                END AS estado
            FROM sancion_participante sp
            JOIN participante p ON sp.ci_participante = p.ci
            ORDER BY sp.fecha_inicio DESC
        """
        cursor.execute(query)
        sanciones = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': sanciones})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/sanciones', methods=['POST'])
def crear_sancion():
    try:
        data = request.get_json()
        
        required = ['ci_participante', 'fecha_inicio', 'fecha_fin']
        for field in required:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'error': f'Campo requerido: {field}'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        motivo = data.get('motivo', 'No asistencia a reserva')
        
        query = """
            INSERT INTO sancion_participante (ci_participante, fecha_inicio, fecha_fin, motivo)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['ci_participante'],
            data['fecha_inicio'],
            data['fecha_fin'],
            motivo
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Sanción creada correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/sanciones/<int:id_sancion>', methods=['DELETE'])
def eliminar_sancion(id_sancion):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "DELETE FROM sancion_participante WHERE id_sancion = %s"
        cursor.execute(query, (id_sancion,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Sanción eliminada correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



# ============================================
# ENDPOINTS DE REPORTES / MÉTRICAS
# ============================================

@app.route('/api/reportes/salas-mas-reservadas')
def reporte_salas_mas_reservadas():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                r.nombre_sala,
                r.edificio,
                COUNT(*) AS total_reservas
            FROM reserva r
            GROUP BY r.nombre_sala, r.edificio
            ORDER BY total_reservas DESC
            LIMIT 10
        """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reportes/turnos-demandados')
def reporte_turnos_mas_demandados():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                TIME_FORMAT(t.hora_inicio, '%H:%i') as hora_inicio,
                TIME_FORMAT(t.hora_fin, '%H:%i') as hora_fin,
                COUNT(*) AS total_reservas
            FROM reserva r
            JOIN turno t ON r.id_turno = t.id_turno
            GROUP BY t.hora_inicio, t.hora_fin
            ORDER BY total_reservas DESC
        """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reportes/promedio-participantes')
def reporte_promedio_participantes_por_sala():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                r.nombre_sala,
                r.edificio,
                s.capacidad,
                AVG(subquery.cantidad) AS promedio_participantes
            FROM reserva r
            JOIN sala s ON r.nombre_sala = s.nombre_sala AND r.edificio = s.edificio
            JOIN (
                SELECT 
                    rp.id_reserva,
                    COUNT(*) AS cantidad
                FROM reserva_participante rp
                GROUP BY rp.id_reserva
            ) subquery ON r.id_reserva = subquery.id_reserva
            GROUP BY r.nombre_sala, r.edificio, s.capacidad
            ORDER BY promedio_participantes DESC
        """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reportes/reservas-por-carrera')
def reporte_reservas_por_carrera_facultad():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                f.nombre AS facultad,
                pa.nombre_programa AS carrera,
                COUNT(DISTINCT r.id_reserva) AS total_reservas
            FROM reserva r
            JOIN reserva_participante rp ON r.id_reserva = rp.id_reserva
            JOIN participante p ON rp.ci_participante = p.ci
            JOIN participante_programa_academico ppa ON p.ci = ppa.ci_participante
            JOIN programa_academico pa ON ppa.nombre_programa = pa.nombre_programa
            JOIN facultad f ON pa.id_facultad = f.id_facultad
            GROUP BY f.nombre, pa.nombre_programa
            ORDER BY total_reservas DESC
        """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reportes/ocupacion-edificios')
def reporte_ocupacion_por_edificio():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                e.nombre_edificio,
                COUNT(DISTINCT s.nombre_sala) AS total_salas,
                COUNT(r.id_reserva) AS total_reservas,
                ROUND((COUNT(r.id_reserva) / (COUNT(DISTINCT s.nombre_sala) * 15 * 30)) * 100, 2) AS porcentaje
            FROM edificio e
            LEFT JOIN sala s ON e.nombre_edificio = s.edificio
            LEFT JOIN reserva r ON s.nombre_sala = r.nombre_sala AND s.edificio = r.edificio
            GROUP BY e.nombre_edificio
            ORDER BY porcentaje DESC
        """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reportes/asistencias-por-rol')
def reporte_reservas_asistencias():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                ppa.rol,
                COUNT(DISTINCT r.id_reserva) AS total_reservas,
                SUM(CASE WHEN rp.asistencia = 1 THEN 1 ELSE 0 END) AS asistencias,
                SUM(CASE WHEN rp.asistencia = 0 THEN 1 ELSE 0 END) AS inasistencias
            FROM reserva r
            JOIN reserva_participante rp ON r.id_reserva = rp.id_reserva
            JOIN participante p ON rp.ci_participante = p.ci
            JOIN participante_programa_academico ppa ON p.ci = ppa.ci_participante
            GROUP BY ppa.rol
        """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reportes/sanciones-por-rol')
def reporte_sanciones_por_tipo_usuario():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                ppa.rol,
                COUNT(*) AS total_sanciones,
                SUM(CASE 
                    WHEN CURDATE() BETWEEN sp.fecha_inicio AND sp.fecha_fin 
                    THEN 1 ELSE 0 
                END) AS activas
            FROM sancion_participante sp
            JOIN participante p ON sp.ci_participante = p.ci
            JOIN participante_programa_academico ppa ON p.ci = ppa.ci_participante
            GROUP BY ppa.rol
        """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reportes/reservas-por-estado')
def reporte_reservas_por_estado():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                estado,
                COUNT(*) AS cantidad,
                ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM reserva)), 2) AS porcentaje
            FROM reserva
            GROUP BY estado
            ORDER BY cantidad DESC
        """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reportes/edificio-por-facultad')
def reporte_edificio_por_facultad():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                f.nombre AS facultad,
                r.edificio AS nombre_edificio,
                COUNT(*) AS total
            FROM reserva r
            JOIN reserva_participante rp ON r.id_reserva = rp.id_reserva
            JOIN participante_programa_academico ppa ON rp.ci_participante = ppa.ci_participante
            JOIN programa_academico pa ON ppa.nombre_programa = pa.nombre_programa
            JOIN facultad f ON pa.id_facultad = f.id_facultad
            GROUP BY f.nombre, r.edificio
            HAVING COUNT(*) = (
                SELECT COUNT(*) 
                FROM reserva r2
                JOIN reserva_participante rp2 ON r2.id_reserva = rp2.id_reserva
                JOIN participante_programa_academico ppa2 ON rp2.ci_participante = ppa2.ci_participante
                JOIN programa_academico pa2 ON ppa2.nombre_programa = pa2.nombre_programa
                WHERE pa2.id_facultad = pa.id_facultad
                GROUP BY r2.edificio
                ORDER BY COUNT(*) DESC
                LIMIT 1
            )
        """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reportes/usuarios-mas-activos')
def reporte_usuarios_mas_activos():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                p.nombre,
                p.apellido,
                p.email,
                COUNT(DISTINCT r.id_reserva) AS total_reservas
            FROM participante p
            JOIN reserva_participante rp ON p.ci = rp.ci_participante
            JOIN reserva r ON rp.id_reserva = r.id_reserva
            GROUP BY p.ci, p.nombre, p.apellido, p.email
            ORDER BY total_reservas DESC
            LIMIT 10
        """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reportes/salas-cancelacion')
def reporte_tasa_cancelacion():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                r.nombre_sala,
                r.edificio,
                COUNT(*) AS total,
                SUM(CASE WHEN r.estado = 'cancelada' THEN 1 ELSE 0 END) AS canceladas,
                ROUND((SUM(CASE WHEN r.estado = 'cancelada' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) AS tasa
            FROM reserva r
            GROUP BY r.nombre_sala, r.edificio
            HAVING COUNT(*) > 0
            ORDER BY tasa DESC
        """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



# ============================================
# ENDPOINTS PARA CARGA DE DATOS MAESTROS
# ============================================

@app.route('/api/edificios')
def get_edificios():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM edificio ORDER BY nombre_edificio")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/facultades')
def get_facultades():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM facultad ORDER BY nombre")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/programas_academicos')
def get_programas_academicos():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT pa.nombre_programa, pa.tipo, f.nombre AS facultad
            FROM programa_academico pa
            JOIN facultad f ON pa.id_facultad = f.id_facultad
            ORDER BY pa.nombre_programa
        """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    print("=" * 70)
    print("  🏛️  SISTEMA DE GESTIÓN DE SALAS - UCU v2.1")
    print("  ROL DETERMINADO POR DOMINIO DE EMAIL")
    print("=" * 70)
    print("  📧 Dominios configurados:")
    print("     • @correo.ucu.edu.uy → Estudiante Grado")
    print("     • @postgrado.ucu.edu.uy → Estudiante Posgrado")
    print("     • @docentes.ucu.edu.uy → Docente")
    print("=" * 70)
    print("  ✅ Validaciones implementadas:")
    print("     • Solo estudiantes de grado: límite 2h/día, 3 reservas/semana")
    print("     • Posgrado y docentes: sin límites")
    print("     • Restricciones por tipo de sala según rol")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=5000, debug=True)