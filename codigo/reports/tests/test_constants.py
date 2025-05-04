# ==========================================
# Autor: David Colás Martín
# ==========================================
"""
Constantes para los tests de reportes.
"""
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

# Usuarios
ADMIN_USERNAME = "admin_user"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin_password"

USER_USERNAME = "regular_user"
USER_EMAIL = "user@example.com"
USER_PASSWORD = "user_password"

OTHER_USERNAME = "other_user"
OTHER_EMAIL = "other@example.com"
OTHER_PASSWORD = "other_password"

# Reportes
REPORT_TITLE = "Reporte de prueba"
REPORT_DESCRIPTION = "Descripción del reporte de prueba"
REPORT_RESPONSE = "Respuesta al reporte de prueba"

UPDATED_TITLE = "Título actualizado"
UPDATED_DESCRIPTION = "Descripción actualizada"

# Tipos de reportes
REPORT_TYPE_USER = "user"
REPORT_TYPE_RIDE = "ride"
REPORT_TYPE_PAYMENT = "payment"
REPORT_TYPE_SYSTEM = "system"

# Importancia
IMPORTANCE_NORMAL = "normal"
IMPORTANCE_IMPORTANT = "important"
IMPORTANCE_URGENT = "urgent"

# Viajes
RIDE_ORIGIN = "Madrid"
RIDE_DESTINATION = "Barcelona"
RIDE_PRICE = Decimal("25.50")
RIDE_SEATS = 3
RIDE_DAYS_FUTURE = 2

# Constantes para URLs
URL_REPORT_LIST = "reports:report_list"
URL_REPORT_DETAIL = "reports:report_detail"
URL_CREATE_REPORT = "reports:create_report"
URL_UPDATE_REPORT = "reports:update_report"
URL_DELETE_REPORT = "reports:delete_report"
URL_MARK_READ = "reports:mark_as_read"
URL_MARK_UNREAD = "reports:mark_as_unread"

# Templates
TEMPLATE_REPORT_LIST = "reports/report_list.html"
TEMPLATE_REPORT_DETAIL = "reports/report_detail.html"
TEMPLATE_REPORT_FORM = "reports/report_form.html"
TEMPLATE_REPORT_DELETE = "reports/report_confirm_delete.html"
