from django.urls import path
from .views import CartItemCreateView, CartItemDeleteView, CartItemListView,CartItemUpdateView,CartRetrieveView
urlpatterns = [
    path('cart/', CartRetrieveView.as_view(), name='cart'),
    path('cart/add/', CartItemCreateView.as_view(), name='cart-add'),
    path('cart/remove/<int:pk>/', CartItemDeleteView.as_view(), name='cart-remove'),
    path('cart/update/<int:pk>/', CartItemUpdateView.as_view(), name='cart-update'),

]
