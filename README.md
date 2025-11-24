# Sistema de Gestión de Reserva de Salas de Estudio - UCU

## Descripción del Proyecto

Sistema de información para la gestión de salas de estudio en la Universidad Católica del Uruguay. Permite la reserva de salas, control de asistencia, gestión de sanciones y generación de reportes para apoyar la toma de decisiones académicas.

**Trabajo Obligatorio - Base de Datos 1**  
Universidad Católica del Uruguay - Segundo Semestre 2025

---

## Equipo

- Belén Mendes
- Manuel Chouhy
- Nicolás Pérez

Antes de comenzar, asegúrate de tener instalado:

- Python 3.9 o superior
- MySQL 8.0 o superior (o Docker como alternativa)
- Git para clonar el repositorio

---

## Instalación

### Paso 1: Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/obligatorio-bases-ucu.git
cd obligatorio-bases-ucu
```

### Paso 2: Configurar la Base de Datos

#### Usando Docker (Recomendado)
```bash
docker-compose up -d
```

Esto iniciará un contenedor de MySQL con la siguiente configuración:
- Host: `localhost`
- Puerto: `3307`
- Usuario: `root`
- Contraseña: `manuelmanuel`
- Base de datos: `ucu_salas`

#### Usando MySQL Local

Si prefieres usar MySQL instalado localmente:
```sql
CREATE DATABASE ucu_salas;
```

Luego ajusta las credenciales en el archivo `.env` (ver Paso 4).

### Paso 3: Importar las Tablas

#### Con Docker:
```bash
docker exec -i ucu_salas_db mysql -u root -pmanuelmanuel ucu_salas < database/ucu_salas_edificio.sql
docker exec -i ucu_salas_db mysql -u root -pmanuelmanuel ucu_salas < database/ucu_salas_facultad.sql
docker exec -i ucu_salas_db mysql -u root -pmanuelmanuel ucu_salas < database/ucu_salas_participante.sql
docker exec -i ucu_salas_db mysql -u root -pmanuelmanuel ucu_salas < database/ucu_salas_login.sql
docker exec -i ucu_salas_db mysql -u root -pmanuelmanuel ucu_salas < database/ucu_salas_programa_academico.sql
docker exec -i ucu_salas_db mysql -u root -pmanuelmanuel ucu_salas < database/ucu_salas_participante_programa_academico.sql
docker exec -i ucu_salas_db mysql -u root -pmanuelmanuel ucu_salas < database/ucu_salas_sala.sql
docker exec -i ucu_salas_db mysql -u root -pmanuelmanuel ucu_salas < database/ucu_salas_turno.sql
docker exec -i ucu_salas_db mysql -u root -pmanuelmanuel ucu_salas < database/ucu_salas_reserva.sql
docker exec -i ucu_salas_db mysql -u root -pmanuelmanuel ucu_salas < database/ucu_salas_reserva_participante.sql
docker exec -i ucu_salas_db mysql -u root -pmanuelmanuel ucu_salas < database/ucu_salas_sancion_participante.sql
```

O importa todo de una vez:
```bash
cat database/*.sql | docker exec -i ucu_salas_db mysql -u root -pmanuelmanuel ucu_salas
```

#### Con MySQL Local:
```bash
mysql -u tu_usuario -p ucu_salas < database/ucu_salas_edificio.sql
mysql -u tu_usuario -p ucu_salas < database/ucu_salas_facultad.sql
# Continúa con el resto de archivos en el mismo orden
```

### Paso 4: Instalar Dependencias de Python
```bash
cd backend

# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 5: Configurar Variables de Entorno

Crea un archivo `.env` dentro de la carpeta `backend/`:

**Si usas Docker:**
```env
DB_HOST=localhost
DB_PORT=3307
DB_USER=root
DB_PASSWORD=manuelmanuel
DB_NAME=ucu_salas
```

**Si usas MySQL local:**
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_NAME=ucu_salas
```

### Paso 6: Iniciar el Servidor Backend
```bash
# Desde la carpeta backend/
python app.py
```

El servidor estará disponible en: `http://localhost:5000`

### Paso 7: Abrir el Frontend

**Opción 1:** Abre directamente el archivo `frontend/login.html` en tu navegador.

**Opción 2:** Usa un servidor HTTP local (recomendado):
```bash
cd frontend
python -m http.server 8080
```

Luego visita: `http://localhost:8080/login.html`

---

## Uso del Sistema

### Usuarios de Prueba

El sistema incluye tres usuarios preconfigurados:

**Estudiante de Grado:**
- Email: `nombre.apellido@correo.ucu.edu.uy`
- Contraseña: cualquier texto
- Permisos: Puede reservar solo salas de uso libre

**Estudiante de Posgrado:**
- Email: `nombre.apellido@postgrado.ucu.edu.uy`
- Contraseña: cualquier texto
- Permisos: Puede reservar salas libres y salas exclusivas de posgrado

**Docente:**
- Email: `nombre.apellido@docentes.ucu.edu.uy`
- Contraseña: cualquier texto
- Permisos: Puede reservar cualquier tipo de sala

**Nota:** En esta versión de prueba no se validan contraseñas. El rol se determina automáticamente por el dominio del email.

### Realizar una Reserva

1. Inicia sesión con uno de los usuarios de prueba
2. Haz clic en "Reservas" en el menú de navegación
3. Completa el formulario:
   - Selecciona una sala (solo verás las permitidas según tu rol)
   - Elige la fecha
   - Selecciona el turno horario (bloques de 1 hora)
   - Opcionalmente agrega participantes (ingresa sus cédulas)
4. Haz clic en "Crear Reserva"

El sistema validará automáticamente disponibilidad, límites diarios y semanales, sanciones y capacidad.

### Ver Mis Reservas

1. Haz clic en "Mi Perfil" en el menú
2. Verás todas tus reservas organizadas por estado (activas, finalizadas, canceladas)
3. Puedes cancelar reservas activas desde esta pantalla

### Consultar Reportes

1. Haz clic en "Reportes" en el menú
2. Selecciona el tipo de reporte que deseas consultar
3. Los reportes incluyen estadísticas de salas, turnos, ocupación, asistencias y más

---
