/**
 * Inicializa las estadísticas de mensajes
 * @param {string} msgDataJson - Datos de mensajes en formato JSON
 */
function initializeMessageStats(msgDataJson) {
    const msgData = JSON.parse(msgDataJson);
    const currentPeriod = msgData.period;
    
    setupChartDefaults();
    checkAndToggleDataVisibility(msgData);
    
    document.addEventListener('DOMContentLoaded', function() {
        initializeCharts(msgData);
    });
    
    setupWindowResizeHandlers();
}

/**
 * Configuración predeterminada para las gráficas
 */
function setupChartDefaults() {
    Chart.defaults.font.family = "-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', Arial, sans-serif";
    Chart.defaults.color = '#86868b';
}

/**
 * Verifica la disponibilidad de datos y muestra/oculta los mensajes correspondientes
 */
function checkAndToggleDataVisibility(msgData) {
    const hasMessageData = msgData.datasets && msgData.datasets[0] && 
                         msgData.datasets[0].data && 
                         msgData.datasets[0].data.some(count => count > 0);
    
    toggleNoDataMessage('messagesChart', !hasMessageData);
    
    const hasMessageStatus = msgData.total_messages > 0;
    toggleNoDataMessage('messageStatusChart', !hasMessageStatus);
}

/**
 * Inicializa todas las gráficas de la página
 */
function initializeCharts(msgData) {
    renderActivityChart(msgData);
    renderStatusChart(msgData);
}

/**
 * Renderiza la gráfica de actividad de mensajes
 */
function renderActivityChart(msgData) {
    if (!document.getElementById('messagesChart')) return;
    
    const messagesCtx = document.getElementById('messagesChart').getContext('2d');
    new Chart(
        messagesCtx,
        {
            type: 'line',
            data: getActivityChartData(msgData),
            options: getActivityChartOptions()
        }
    );
}

/**
 * Obtiene los datos para la gráfica de actividad
 */
function getActivityChartData(msgData) {
    return {
        labels: msgData.labels || [],
        datasets: [{
            label: getChartTitle(msgData.period),
            data: msgData.datasets && msgData.datasets[0] ? msgData.datasets[0].data : [],
            backgroundColor: 'rgba(52, 199, 89, 0.1)',
            borderColor: '#34c759',
            borderWidth: 2,
            pointBackgroundColor: '#34c759',
            pointBorderColor: '#fff',
            pointRadius: 4,
            pointHoverRadius: 6,
            fill: true,
            tension: 0.3
        }]
    };
}

/**
 * Obtiene las opciones para la gráfica de actividad
 */
function getActivityChartOptions() {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: getTooltipOptions()
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    precision: 0
                }
            }
        }
    };
}

/**
 * Obtiene las opciones para los tooltips
 */
function getTooltipOptions() {
    return {
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
        titleColor: '#1D1D1F',
        bodyColor: '#1D1D1F',
        borderColor: 'rgba(0, 0, 0, 0.1)',
        borderWidth: 1,
        padding: 12,
        boxPadding: 6,
        usePointStyle: true,
        titleFont: {
            weight: '600',
            size: 14
        },
        bodyFont: {
            size: 13
        },
        callbacks: {
            label: function(context) {
                return ' Mensajes: ' + context.raw;
            }
        }
    };
}

/**
 * Renderiza la gráfica de estado de mensajes
 */
function renderStatusChart(msgData) {
    if (!document.getElementById('messageStatusChart') || !msgData.total_messages) return;
    
    const statusCtx = document.getElementById('messageStatusChart').getContext('2d');
    new Chart(
        statusCtx,
        {
            type: 'doughnut',
            data: getStatusChartData(msgData),
            options: getStatusChartOptions(msgData)
        }
    );
}

/**
 * Obtiene los datos para la gráfica de estado
 */
function getStatusChartData(msgData) {
    return {
        labels: ['Leídos', 'No leídos'],
        datasets: [{
            data: [
                msgData.total_messages - msgData.unread_messages,
                msgData.unread_messages
            ],
            backgroundColor: ['#34c759', '#ff3b30'],
            borderWidth: 0,
            borderRadius: 5,
            spacing: 2
        }]
    };
}

/**
 * Obtiene las opciones para la gráfica de estado
 */
function getStatusChartOptions(msgData) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '60%',
        plugins: {
            legend: {
                position: 'right',
                labels: {
                    padding: 20,
                    font: {
                        size: 14
                    },
                    usePointStyle: true,
                    pointStyle: 'circle'
                }
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const label = context.label || '';
                        const value = context.raw || 0;
                        const percentage = Math.round((value / msgData.total_messages) * 100);
                        return ` ${label}: ${value} (${percentage}%)`;
                    }
                }
            }
        }
    };
}

/**
 * Obtiene el título de la gráfica según el período
 */
function getChartTitle(period) {
    switch (period) {
        case 'today': return 'Mensajes por hora';
        case 'week': return 'Mensajes por día';
        case 'month': return 'Mensajes por día';
        case 'year': return 'Mensajes por mes';
        case 'all': return 'Mensajes por mes';
        default: return 'Mensajes';
    }
}

/**
 * Configura los manejadores de redimensionamiento de ventana
 */
function setupWindowResizeHandlers() {
    window.addEventListener('resize', function() {
        if (typeof Chart !== 'undefined' && Chart.instances) {
            Chart.instances.forEach((chart) => {
                chart.resize();
            });
        }
    });
}
