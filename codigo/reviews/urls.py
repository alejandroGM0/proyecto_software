from django.urls import path
from . import views
from .constants import (
    CREATE_REVIEW_NAME, DELETE_REVIEW_NAME, 
    LIST_REVIEWS_NAME, DETAIL_REVIEW_NAME, 
    APP_NAMESPACE
)

app_name = APP_NAMESPACE

urlpatterns = [
    path('create/<int:ride_id>/', views.create, name=CREATE_REVIEW_NAME),
    path('delete/<int:review_id>/', views.delete, name=DELETE_REVIEW_NAME),
    path('list/', views.list_reviews, name=LIST_REVIEWS_NAME),
    path('detail/<int:review_id>/', views.detail, name=DETAIL_REVIEW_NAME),
]