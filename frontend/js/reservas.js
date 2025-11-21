const API_URL = 'http://localhost:5000/api';

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Página de reservas cargada');
    cargarReservas();
});

async function cargarReservas() {
    const contenedor = document.getElementById('reservas-lista');
    
    try {
        contenedor.innerHTML = '<p>⏳ Cargando reservas...</p>';
        
        console.log(`📡 Llamando a: ${API_URL}/reservas`);
        
        const response = await fetch(`${API_URL}/reservas`);
        const data = await response.json();
        
        console.log(`📊 Datos recibidos:`, data);
        
        if (data.success && data.data && data.data.length > 0) {
            console.log(`✅ ${data.data.length} reservas encontradas`);
            mostrarTablaReservas(data.data);
        } else {
            console.log('⚠️ No se encontraron reservas');
            contenedor.innerHTML = '<p>No hay reservas registradas en el sistema.</p>';
        }
        
    } catch (error) {
        console.error('❌ Error:', error);
        contenedor.innerHTML = `
            <div style="padding: 20px; background: #ffebee; border-left: 4px solid #f44336;">
                <h3 style="color: #d32f2f;">❌ Error al cargar reservas</h3>
                <p>Verifica que el backend esté corriendo en http://localhost:5000</p>
                <p style="color: #666; font-size: 0.9em;">Error: ${error.message}</p>
            </div>
        `;
    }
}

function mostrarTablaReservas(reservas) {
    const contenedor = document.getElementById('reservas-lista');
    
    let html = `
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Sala</th>
                    <th>Edificio</th>
                    <th>Fecha</th>
                    <th>Horario</th>
                    <th>Estado</th>
                    <th>Participantes</th>
                    <th>Cantidad</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    reservas.forEach(reserva => {
        // Colores según estado
        let estadoColor = '';
        let estadoTexto = reserva.estado.toUpperCase();
        
        if (reserva.estado === 'activa') {
            estadoColor = 'color: green; font-weight: bold;';
            estadoTexto = '✅ ' + estadoTexto;
        } else if (reserva.estado === 'cancelada') {
            estadoColor = 'color: red; font-weight: bold;';
            estadoTexto = '❌ ' + estadoTexto;
        } else if (reserva.estado === 'finalizada') {
            estadoColor = 'color: blue; font-weight: bold;';
            estadoTexto = '✔️ ' + estadoTexto;
        } else if (reserva.estado === 'sin_asistencia') {
            estadoColor = 'color: orange; font-weight: bold;';
            estadoTexto = '⚠️ SIN ASISTENCIA';
        }
        
        html += `
            <tr>
                <td style="text-align: center;">${reserva.id_reserva}</td>
                <td><strong>${reserva.nombre_sala}</strong></td>
                <td>${reserva.edificio}</td>
                <td>${reserva.fecha}</td>
                <td>${reserva.hora_inicio} - ${reserva.hora_fin}</td>
                <td style="${estadoColor}">${estadoTexto}</td>
                <td>${reserva.participantes || 'Sin participantes'}</td>
                <td style="text-align: center;">${reserva.num_participantes || 0}</td>
            </tr>
        `;
    });
    
    html += `
            </tbody>
        </table>
        <p style="margin-top: 15px; color: #666; text-align: center;">
            ✅ Total de reservas: <strong>${reservas.length}</strong>
        </p>
    `;
    
    contenedor.innerHTML = html;
    console.log('✅ Tabla de reservas renderizada');
}