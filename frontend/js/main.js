// URL del backend
const API_URL = 'http://localhost:5000/api';

// Cargar salas cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Página cargada, llamando al backend...');
    cargarSalas();
});

// Función para cargar salas desde el backend
async function cargarSalas() {
    const contenedor = document.getElementById('salas-lista');
    
    try {
        // Mostrar mensaje de carga
        contenedor.innerHTML = '<p>⏳ Cargando salas...</p>';
        
        console.log(`📡 Llamando a: ${API_URL}/salas`);
        
        // Llamar al backend
        const response = await fetch(`${API_URL}/salas`);
        
        console.log(`📥 Respuesta recibida:`, response.status);
        
        const data = await response.json();
        
        console.log(`📊 Datos recibidos:`, data);
        
        // Si hay salas, mostrarlas
        if (data.success && data.data && data.data.length > 0) {
            console.log(`✅ ${data.data.length} salas encontradas`);
            mostrarTabla(data.data);
        } else {
            console.log('⚠️ No se encontraron salas');
            contenedor.innerHTML = '<p>No hay salas disponibles en la base de datos.</p>';
        }
        
    } catch (error) {
        console.error('❌ Error:', error);
        contenedor.innerHTML = `
            <div style="padding: 20px; background: #ffebee; border-left: 4px solid #f44336; margin: 10px 0;">
                <h3 style="color: #d32f2f; margin-bottom: 10px;">❌ Error al conectar con el backend</h3>
                <p><strong>Verifica que:</strong></p>
                <ul style="margin: 10px 0;">
                    <li>El backend esté corriendo: <code>python app.py</code></li>
                    <li>Esté en el puerto 5000: <code>http://localhost:5000</code></li>
                    <li>La base de datos tenga datos</li>
                </ul>
                <p style="color: #666; font-size: 0.9em; margin-top: 10px;">
                    Error técnico: ${error.message}
                </p>
            </div>
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
                    <th>Dirección</th>
                    <th>Departamento</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    // Agregar cada sala a la tabla
    salas.forEach(sala => {
        // Traducir el tipo de sala con emojis
        let tipoTexto = sala.tipo_sala;
        let tipoColor = '';
        
        if (sala.tipo_sala === 'libre') {
            tipoTexto = '🟢 Uso Libre';
            tipoColor = 'color: green;';
        } else if (sala.tipo_sala === 'posgrado') {
            tipoTexto = '🔵 Posgrado';
            tipoColor = 'color: blue;';
        } else if (sala.tipo_sala === 'docente') {
            tipoTexto = '🟡 Docente';
            tipoColor = 'color: #ff9800;';
        }
        
        html += `
            <tr>
                <td><strong>${sala.nombre_sala}</strong></td>
                <td>${sala.edificio}</td>
                <td style="text-align: center;">${sala.capacidad} personas</td>
                <td style="${tipoColor}">${tipoTexto}</td>
                <td>${sala.direccion || 'N/A'}</td>
                <td>${sala.departamento || 'N/A'}</td>
            </tr>
        `;
    });
    
    html += `
            </tbody>
        </table>
        <p style="margin-top: 15px; color: #666; text-align: center;">
            ✅ Total de salas disponibles: <strong>${salas.length}</strong>
        </p>
    `;
    
    contenedor.innerHTML = html;
    console.log('✅ Tabla renderizada exitosamente');
}