# ==========================================
# Autor: Alejandro Gasca Mediel
# ==========================================
"""
Constantes para la aplicación de dashboard
"""

# URLs patterns
URL_DASHBOARD = 'dashboard:dashboard'
URL_TRIP_STATS = 'dashboard:trip_stats'
URL_MSG_STATS = 'dashboard:msg_stats'
URL_REPORT_STATS = 'dashboard:report_stats'
URL_USER_STATS = 'dashboard:user_stats'
URL_REPORT_DETAIL = 'dashboard:report_detail'
URL_MARK_REPORT = 'dashboard:mark_report'
URL_RIDE_MANAGEMENT = 'dashboard:ride_management'
URL_USER_MANAGEMENT = 'dashboard:user_management'
URL_CHAT_MANAGEMENT = 'dashboard:chat_management'

# Templates
TEMPLATE_DASHBOARD = 'dashboard/dashboard.html'
TEMPLATE_TRIP_STATS = 'dashboard/trip_stats.html'
TEMPLATE_MSG_STATS = 'dashboard/msg_stats.html'
TEMPLATE_REPORT_STATS = 'dashboard/report_stats.html'
TEMPLATE_USER_STATS = 'dashboard/user_stats.html'
TEMPLATE_REPORT_DETAIL = 'dashboard/report_detail.html'
TEMPLATE_RIDE_MANAGEMENT = 'dashboard/ride_management.html'
TEMPLATE_USER_MANAGEMENT = 'dashboard/user_management.html'
TEMPLATE_CHAT_MANAGEMENT = 'dashboard/chat_management.html'

# Context variables
CONTEXT_TRIP_DATA = 'trip_data'
CONTEXT_MSG_DATA = 'msg_data'
CONTEXT_REPORT_DATA = 'report_data'
CONTEXT_USER_DATA = 'user_data'
CONTEXT_PAYMENT_DATA = 'payment_data'
CONTEXT_TIME_PERIOD = 'time_period'

# Default values
DEFAULT_PERIOD = 'week'

# Period options
PERIOD_TODAY = 'today'
PERIOD_WEEK = 'week'
PERIOD_MONTH = 'month'
PERIOD_YEAR = 'year'
PERIOD_ALL = 'all'

# Period text display
PERIOD_TEXT_TODAY = 'Hoy'
PERIOD_TEXT_WEEK = 'Esta Semana'
PERIOD_TEXT_MONTH = 'Este Mes'
PERIOD_TEXT_YEAR = 'Este Año'
PERIOD_TEXT_ALL = 'Total'

# Tipos de gráficos
CHART_TYPE_LINE = 'line'
CHART_TYPE_BAR = 'bar'
CHART_TYPE_PIE = 'pie'
CHART_TYPE_DOUGHNUT = 'doughnut'

# Colores para gráficos
CHART_COLORS = [
    '#0071e3',  # Apple blue
    '#34c759',  # Apple green
    '#ff9500',  # Apple orange
    '#ff3b30',  # Apple red
    '#5ac8fa',  # Apple blue light
    '#007aff',  # Apple blue bright
    '#4cd964',  # Apple green bright
    '#ff2d55'   # Apple pink
]
