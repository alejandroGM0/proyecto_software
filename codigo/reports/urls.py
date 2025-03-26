from django.urls import path
from . import views
from .constants import (
    REPORT_LIST_NAME, REPORT_DETAIL_NAME, CREATE_REPORT_NAME, 
    UPDATE_REPORT_NAME, DELETE_REPORT_NAME, MARK_READ_NAME, MARK_UNREAD_NAME
)

app_name = 'reports'

urlpatterns = [
    path('', views.report_list, name=REPORT_LIST_NAME),
    path('<int:pk>/', views.report_detail, name=REPORT_DETAIL_NAME),
    path('create/', views.create_report, name=CREATE_REPORT_NAME),
    path('<int:pk>/update/', views.update_report, name=UPDATE_REPORT_NAME),
    path('<int:pk>/delete/', views.delete_report, name=DELETE_REPORT_NAME),
    path('<int:pk>/mark-read/', views.mark_as_read, name=MARK_READ_NAME),
    path('<int:pk>/mark-unread/', views.mark_as_unread, name=MARK_UNREAD_NAME),
]