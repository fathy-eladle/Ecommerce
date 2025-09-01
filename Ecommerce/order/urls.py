from django.urls import path
from .views import (
    OrderCreateView,
    OrderListView,
    OrderDetailView,
    OrderCancelView
)

urlpatterns = [
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/create/', OrderCreateView.as_view(), name='order-create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/cancel/', OrderCancelView.as_view(), name='order-cancel'),
]