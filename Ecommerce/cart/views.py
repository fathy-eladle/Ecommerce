from django.shortcuts import render
from rest_framework import generics ,status
from rest_framework.response import Response 
 
from rest_framework.permissions import IsAuthenticated
from .models import CartItem,Cart
from .serializers import CartItemSerializer,CartSerializer
# Create your views here.

class CartRetrieveView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        cart , created =Cart.objects.get_or_create(user = self.request.user)
        return cart
    

class CartItemCreateView(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user =self.request.user)

class CartItemUpdateView(generics.UpdateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        partial_data = {'quantity':request.data.get('quantity',instance.quantity)}
        serializer = self.get_serializer(instance , data = partial_data, partial = True)
        serializer.is_valid(raise_exception=True)
        
        if serializer.validated_data['qauntity'] == 0:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        self.perform_update(serializer)
        return Response(serializer.data)
        
        
    
    
    
class CartItemCreateView(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CartItem.objects.filter(cart__user = self.request.user)
    
    
    def perform_create(self, serializer):
        cart = Cart.objects.get_or_create(user = self.request.user)
        serializer.save(cart=cart)