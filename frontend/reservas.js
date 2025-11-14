const API_URL = 'http://localhost:5000/api';

document.addEventListener('DOMContentLoaded', function() {
    cargarReservas();
});

async function cargarReservas() {
    const contenedor = document.getElementById('reservas-lista');
    
    try {
        contenedor.innerHTML = '<p>Cargando reservas...</p>';
        
        const response = await fetch(`${API_URL}/reservas`);
        const data = await response.json();
        
        if (data.success && data.data.length > 0) {
            mostrarTablaReservas(data.data);
        } else {
            contenedor.innerHTML = '<p>No hay reservas registradas.</p>';
        }
        
    } catch (error) {
        console.error('Error:', error);
        contenedor.innerHTML = '<p style="color: red;">Error al cargar reservas.</p>';
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
                </tr>
            </thead>
            <tbody>
    `;
    
    reservas.forEach(reserva => {
        let estadoColor = '';
        if (reserva.estado === 'activa') estadoColor = 'color: green;';
        if (reserva.estado === 'cancelada') estadoColor = 'color: red;';
        if (reserva.estado === 'finalizada') estadoColor = 'color: blue;';
        
        html += `
            <tr>
                <td>${reserva.id_reserva}</td>
                <td>${reserva.nombre_sala}</td>
                <td>${reserva.edificio}</td>
                <td>${reserva.fecha}</td>
                <td>${reserva.hora_inicio} - ${reserva.hora_fin}</td>
                <td style="${estadoColor}"><strong>${reserva.estado.toUpperCase()}</strong></td>
                <td>${reserva.participantes || 'Sin participantes'}</td>
            </tr>
        `;
    });
    
    html += `
            </tbody>
        </table>
        <p style="margin-top: 15px; color: #666;">
            Total de reservas: <strong>${reservas.length}</strong>
        </p>
    `;
    
    contenedor.innerHTML = html;
}