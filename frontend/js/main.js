// URL del backend
const API_URL = 'http://localhost:5000/api';

// Cargar salas cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    console.log('Pagina cargada, llamando al backend...');
    cargarSalas();
    
    // Mostrar nombre del usuario logueado
    const email = localStorage.getItem('usuarioEmail');
    if (email) {
        document.getElementById('usuarioActual').textContent = email;
    }
});

// Función para cargar salas desde el backend
async function cargarSalas() {
    const contenedor = document.getElementById('salas-lista');
    
    try {
        // Mostrar mensaje de carga
        contenedor.innerHTML = '<p class="mensaje-carga">Cargando salas...</p>';
        
        const response = await fetch(`${API_URL}/salas`);
        console.log('Respuesta recibida del backend:', response.status);
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Datos recibidos del backend:', data);
        
        if (data.success && data.data && Array.isArray(data.data)) {
            if (data.data.length === 0) {
                contenedor.innerHTML = `
                    <div class="mensaje-vacio">
                        <h3>No hay salas registradas</h3>
                        <p>Por el momento no hay salas disponibles en el sistema.</p>
                    </div>
                `;
            } else {
                mostrarTabla(data.data);
            }
        } else {
            throw new Error('Formato de respuesta inesperado desde el backend');
        }
        
    } catch (error) {
        console.error('Error al llamar al backend:', error);
        contenedor.innerHTML = `
            <div class="mensaje-error">
                <h3>Error al cargar las salas</h3>
                <p>Ocurrió un problema al conectarse con el servidor.</p>
                <p style="font-size: 0.9em; opacity: 0.8;">Detalle técnico: ${error.message}</p>
            </div>
        `;
    }
}

// Renderizado mejorado - SIMPLIFICADO
function mostrarTabla(salas) {
    const contenedor = document.getElementById('salas-lista');
    
    let html = `
        <div style="overflow-x: auto;">
            <table>
                <thead>
                    <tr>
                        <th style="text-align: left;">Nombre</th>
                        <th style="text-align: center;">Capacidad</th>
                        <th style="text-align: center;">Tipo</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    salas.forEach(sala => {
        html += `
            <tr>
                <td style="text-align: left;"><strong>${sala.nombre_sala}</strong></td>
                <td style="text-align: center;">${sala.capacidad} personas</td>
                <td style="text-align: center;">
                    <span class="badge-tipo ${getClaseTipoSala(sala.tipo_sala)}">
                        ${mapearTipoSala(sala.tipo_sala)}
                    </span>
                </td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
        <p class="text-center mt-15" style="color: var(--color-cyan); font-weight: 600;">
            Total de salas disponibles: <strong>${salas.length}</strong>
        </p>
    `;
    
    contenedor.innerHTML = html;
    console.log('Tabla renderizada exitosamente');
}

function getClaseTipoSala(tipo) {
    switch (tipo) {
        case 'libre':
            return 'badge-libre';
        case 'posgrado':
            return 'badge-posgrado';
        case 'docente':
            return 'badge-docente';
        default:
            return '';
    }
}

function mapearTipoSala(tipo) {
    switch (tipo) {
        case 'libre':
            return 'Uso Libre';
        case 'posgrado':
            return 'Posgrado';
        case 'docente':
            return 'Docente';
        default:
            return tipo;
    }
}