// URL del backend
const API_URL = 'http://localhost:5000/api';

// Cargar salas cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    cargarSalas();
});

// Función para cargar salas desde el backend
async function cargarSalas() {
    const contenedor = document.getElementById('salas-lista');
    
    try {
        // Mostrar mensaje de carga
        contenedor.innerHTML = '<p>Cargando salas...</p>';
        
        // Llamar al backend
        const response = await fetch(`${API_URL}/salas`);
        const data = await response.json();
        
        // Si hay salas, mostrarlas
        if (data.success && data.data.length > 0) {
            mostrarTabla(data.data);
        } else {
            contenedor.innerHTML = '<p>No hay salas disponibles.</p>';
        }
        
    } catch (error) {
        console.error('Error:', error);
        contenedor.innerHTML = `
            <p style="color: red;">
                Error al conectar con el backend.<br>
                Asegurate que el backend esté corriendo en http://localhost:5000
            </p>
        `;
    }
}

// Función para crear la tabla HTML
function mostrarTabla(salas) {
    const contenedor = document.getElementById('salas-lista');
    
    let html = `
        <table>
            <thead>
                <tr>
                    <th>Nombre</th>
                    <th>Edificio</th>
                    <th>Capacidad</th>
                    <th>Tipo</th>
                    <th>Piso</th>
                    <th>Equipamiento</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    // Agregar cada sala a la tabla
    salas.forEach(sala => {
        // Traducir el tipo de sala
        let tipoTexto = sala.tipo_sala;
        if (sala.tipo_sala === 'libre') tipoTexto = 'Uso Libre';
        if (sala.tipo_sala === 'posgrado') tipoTexto = ' Posgrado';
        if (sala.tipo_sala === 'docente') tipoTexto = 'Docente';
        
        html += `
            <tr>
                <td><strong>${sala.nombre_sala}</strong></td>
                <td>${sala.edificio}</td>
                <td>${sala.capacidad} personas</td>
                <td>${tipoTexto}</td>
                <td>${sala.piso || 'N/A'}</td>
                <td>${sala.equipamiento || 'Sin equipamiento'}</td>
            </tr>
        `;
    });
    
    html += `
            </tbody>
        </table>
        <p style="margin-top: 15px; color: #666;">
            Total de salas: <strong>${salas.length}</strong>
        </p>
    `;
    
    contenedor.innerHTML = html;
}