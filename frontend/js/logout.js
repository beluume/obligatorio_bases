// logout.js - VERSIÓN DEFINITIVA QUE SÍ FUNCIONA

function cerrarSesion() {
    console.log('🔴 Función cerrarSesion llamada');
    
    // Limpiar localStorage
    localStorage.clear();
    console.log('✅ localStorage limpiado');
    
    // Redirigir
    console.log('🔄 Redirigiendo a login.html...');
    window.location.href = 'login.html';
}

// Esperar a que el DOM cargue
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 DOM cargado - Buscando botón cerrar sesión...');
    
    const btnCerrarSesion = document.getElementById('btnCerrarSesion');
    
    if (btnCerrarSesion) {
        console.log('✅ Botón encontrado:', btnCerrarSesion);
        
        btnCerrarSesion.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('🖱️ Click en cerrar sesión detectado');
            
            if (confirm('¿Está seguro que desea cerrar sesión?')) {
                cerrarSesion();
            } else {
                console.log('❌ Usuario canceló');
            }
        });
        
        console.log('✅ Event listener agregado correctamente');
    } else {
        console.error('❌ NO SE ENCONTRÓ el botón con id="btnCerrarSesion"');
    }
});

console.log('📦 logout.js cargado correctamente');