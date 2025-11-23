const API_URL = 'http://localhost:5000/api';

document.addEventListener('DOMContentLoaded', function() {
    console.log('Pagina de reservas cargada');
    cargarReservas();
});

async function cargarReservas() {
    const contenedor = document.getElementById('reservas-lista');
    
    try {
        contenedor.innerHTML = '<p class="mensaje-carga">Cargando reservas...</p>';
        
        console.log(`Llamando a: ${API_URL}/reservas`);
        
        const response = await fetch(`${API_URL}/reservas`);
        const data = await response.json();
        
        console.log(`Datos recibidos:`, data);
        
        if (data.success && data.data && data.data.length > 0) {
            console.log(`${data.data.length} reservas encontradas`);
            mostrarTablaReservas(data.data);
        } else {
            console.log('No se encontraron reservas');
            contenedor.innerHTML = `
                <div style="text-align: center; padding: 40px; background: rgba(23, 145, 129, 0.1); border-radius: 12px;">
                    <p style="font-size: 2.5rem; margin-bottom: 15px;">📅</p>
                    <h3 style="color: var(--color-cyan); margin-bottom: 10px;">No hay reservas registradas</h3>
                    <p style="color: var(--color-text-secondary);">
                        El sistema no tiene reservas activas en este momento.
                    </p>
                </div>
            `;
        }
        
    } catch (error) {
        console.error('Error:', error);
        contenedor.innerHTML = `
            <div class="mensaje-error">
                <h3>Error al cargar reservas</h3>
                <p style="color: var(--color-text-secondary); margin-bottom: 15px;">
                    No se pudo conectar con el servidor para obtener las reservas.
                </p>
                <p><strong>Verifica que:</strong></p>
                <ul>
                    <li>El backend este corriendo en <code>http://localhost:5000</code></li>
                    <li>La base de datos esté accesible y tenga datos</li>
                    <li>No haya problemas de red o firewall</li>
                </ul>
                <p style="margin-top: 15px; padding: 10px; background: rgba(0,0,0,0.2); border-radius: 6px; font-size: 0.9em;">
                    <strong>Error tecnico:</strong> ${error.message}
            </p>
                <button onclick="cargarReservas()" style="margin-top: 15px;">
                    Reintentar
                </button>
            </div>
        `;
    }
}

function mostrarTablaReservas(reservas) {
    const contenedor = document.getElementById('reservas-lista');
    
    // Calcular estadísticas
    const stats = calcularEstadisticas(reservas);
    
    let html = `
        <div class="resumen-reservas">
            <div class="card-resumen">
                <h4>Activas</h4>
                <p>${stats.activas}</p>
            </div>
            <div class="card-resumen">
                <h4>Canceladas</h4>
                <p>${stats.canceladas}</p>
            </div>
            <div class="card-resumen">
                <h4>Finalizadas</h4>
                <p>${stats.finalizadas}</p>
            </div>
            <div class="card-resumen">
                <h4>Sin asistencia</h4>
                <p>${stats.sinAsistencia}</p>
            </div>
        </div>
        
        <div style="overflow-x: auto; margin-top: 20px;">
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
        html += `
            <tr>
                <td>${reserva.id_reserva}</td>
                <td>${reserva.nombre_sala}</td>
                <td>${reserva.edificio}</td>
                <td>${reserva.fecha}</td>
                <td>${reserva.hora_inicio} - ${reserva.hora_fin}</td>
                <td>${reserva.estado}</td>
                <td>${reserva.participantes || '-'}</td>
                <td>${reserva.cantidad_participantes || '-'}</td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
        <p class="text-center mt-15" style="color: var(--color-cyan); font-weight: 600;">
            Total de reservas: <strong>${reservas.length}</strong>
        </p>
    `;
    
    contenedor.innerHTML = html;
    console.log('Tabla de reservas renderizada con estadisticas');
}

function calcularEstadisticas(reservas) {
    return {
        activas: reservas.filter(r => r.estado === 'activa').length,
        canceladas: reservas.filter(r => r.estado === 'cancelada').length,
        finalizadas: reservas.filter(r => r.estado === 'finalizada').length,
        sinAsistencia: reservas.filter(r => r.estado === 'sin_asistencia').length
    };
}