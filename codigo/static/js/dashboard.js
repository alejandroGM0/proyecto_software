//==========================================
// Autor:Álvaro Pérez Gregorio
//==========================================
// Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar el selector de período
    initPeriodSelector();
});

function initPeriodSelector() {
    const periodToggle = document.querySelector('.period-select-button');
    const periodMenu = document.querySelector('.period-dropdown-menu');
    const periodDropdown = document.querySelector('.period-dropdown');
    
    if (!periodToggle || !periodMenu) return;
    
    // Abrir/cerrar el dropdown al hacer clic
    periodToggle.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        periodDropdown.classList.toggle('active');
    });
    
    // Cerrar el dropdown cuando se hace clic fuera
    document.addEventListener('click', function(e) {
        if (!periodDropdown.contains(e.target)) {
            periodDropdown.classList.remove('active');
        }
    });
    
    // Evitar que los clics dentro del dropdown lo cierren
    periodMenu.addEventListener('click', function(e) {
        e.stopPropagation();
    });
    
    // Seleccionar período
    document.querySelectorAll('.period-option').forEach(item => {
        item.addEventListener('click', function(e) {
            // No prevenimos el comportamiento por defecto para mantener la navegación por URL
            
            // Marcar el ítem como seleccionado (visual únicamente)
            document.querySelectorAll('.period-option').forEach(i => {
                i.classList.remove('active-period-clicked');
            });
            this.classList.add('active-period-clicked');
            
            // No necesitamos cerrar el dropdown aquí ya que se navegará a una nueva URL
            
            console.log('Período seleccionado:', this.getAttribute('href').split('=')[1]);
        });
    });
    
    // Añadir efecto de hover más elegante
    const periodArrow = document.querySelector('.period-arrow');
    if (periodArrow) {
        periodToggle.addEventListener('mouseenter', function() {
            periodArrow.style.transform = 'translateY(2px)';
        });
        
        periodToggle.addEventListener('mouseleave', function() {
            if (!periodDropdown.classList.contains('active')) {
                periodArrow.style.transform = 'translateY(0)';
            }
        });
    }
}