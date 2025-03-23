from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path('<int:pk>/', views.report_detail, name='report_detail'),
    path('create/', views.create_report, name='create_report'),
    path('<int:pk>/update/', views.update_report, name='update_report'),
    path('<int:pk>/delete/', views.delete_report, name='delete_report'),
    path('<int:pk>/mark-read/', views.mark_as_read, name='mark_as_read'),
    path('<int:pk>/mark-unread/', views.mark_as_unread, name='mark_as_unread'),
]