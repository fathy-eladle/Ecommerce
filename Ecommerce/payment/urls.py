from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('initialize/', views.initialize_payment, name='initialize_payment'),
    path('callback/', views.payment_callback, name='payment_callback'),
]
