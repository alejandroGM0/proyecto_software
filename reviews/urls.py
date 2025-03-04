from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('create/<int:ride_id>/', views.create, name='create'),
    path('delete/<int:review_id>/', views.delete, name='delete'),
    path('list/', views.list_reviews, name='list'),
    path('detail/<int:review_id>/', views.detail, name='detail'),
]