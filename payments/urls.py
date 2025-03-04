from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('pay/', views.pay, name='pay'),
    path('payment/<int:payment_id>/', views.payment, name='payment'),
    path('refund/<int:payment_id>/', views.refund, name='refund'),
]