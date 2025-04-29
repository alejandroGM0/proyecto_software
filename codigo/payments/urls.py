from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("", views.payment_list, name="payment_list"),
    path("history/", views.payment_history, name="payment_history"),
    path("<int:pk>/", views.payment_detail, name="payment_detail"),
    path("create/<int:ride_id>/", views.create_payment, name="create_payment"),
    path("<int:pk>/success/", views.payment_success, name="payment_success"),
    path("<int:pk>/cancel/", views.payment_cancel, name="payment_cancel"),
    path("<int:pk>/refund/", views.refund_payment, name="refund_payment"),
    path("<int:pk>/cancel-payment/", views.cancel_payment, name="cancel_payment"),
    path("my-payments/", views.my_payments, name="my_payments"),
]
