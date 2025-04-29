"""
Constantes utilizadas en la aplicación de reportes.
"""

# Namespace de la aplicación
APP_NAMESPACE = "reports"

# Nombres de URLs
REPORT_LIST_NAME = "report_list"
REPORT_DETAIL_NAME = "report_detail"
CREATE_REPORT_NAME = "create_report"
UPDATE_REPORT_NAME = "update_report"
DELETE_REPORT_NAME = "delete_report"
MARK_READ_NAME = "mark_as_read"
MARK_UNREAD_NAME = "mark_as_unread"
MY_REPORTS_NAME = "my_reports"


def get_url_full(name):
    """
    Devuelve el nombre completo de una URL incluyendo el namespace.
    Ejemplo: get_url_full(REPORT_LIST_NAME) -> 'reports:report_list'
    """
    return f"{APP_NAMESPACE}:{name}"


# Templates
REPORT_LIST_TEMPLATE = "reports/report_list.html"
REPORT_DETAIL_TEMPLATE = "reports/report_detail.html"
REPORT_FORM_TEMPLATE = "reports/report_form.html"
REPORT_DELETE_TEMPLATE = "reports/report_confirm_delete.html"

# Claves de contexto
REPORT_KEY = "report"
REPORTS_KEY = "reports"
FILTER_FORM_KEY = "filter_form"
PAGE_OBJ_KEY = "page_obj"
IS_PAGINATED_KEY = "is_paginated"
PAGINATOR_KEY = "paginator"
IS_ADMIN_KEY = "is_admin"
RESPONSE_FORM_KEY = "response_form"
REPORTED_USER_KEY = "reported_user"
RIDE_KEY = "ride"
PAYMENT_KEY = "payment"

# ID params
USER_ID_PARAM = "user_id"
RIDE_ID_PARAM = "ride_id"
PAYMENT_ID_PARAM = "payment_id"

# Tipos de reporte
PAYMENT_TYPE = "payment"
RIDE_TYPE = "ride"
USER_TYPE = "user"
SYSTEM_TYPE = "system"
USER_REPORT = "user"
RIDE_REPORT = "ride"
PAYMENT_REPORT = "payment"
SYSTEM_REPORT = "system"

# Niveles de importancia
NORMAL_IMPORTANCE = "normal"
IMPORTANT_IMPORTANCE = "important"
URGENT_IMPORTANCE = "urgent"

# Mensajes
REPORT_CREATED_SUCCESS = "Reporte enviado exitosamente."
REPORT_UPDATED_SUCCESS = "Reporte actualizado exitosamente."
REPORT_DELETED_SUCCESS = "Reporte eliminado exitosamente."
RESPONSE_SENT_SUCCESS = "Respuesta enviada correctamente."
REPORT_MARKED_READ = True
REPORT_MARKED_UNREAD = False
REPORT_ALREADY_RESPONDED_ERROR = (
    "No puedes editar un reporte que ya ha sido respondido."
)
NO_PERMISSION_ERROR = "No tienes permiso para realizar esta acción."
NO_VIEW_PERMISSION_ERROR = "No tienes permiso para ver este reporte."
NO_EDIT_PERMISSION_ERROR = "No tienes permiso para editar este reporte."
NO_DELETE_PERMISSION_ERROR = "No tienes permiso para eliminar este reporte."
NO_MARK_PERMISSION_ERROR = (
    "Solo los administradores pueden marcar reportes como leídos/no leídos."
)

# Paginación
REPORTS_PER_PAGE = 10

# Formatos
DATE_FORMAT = "d/m/Y H:i"
