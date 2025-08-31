from django.shortcuts import render
from rest_framework import generics ,status
from rest_framework.response import Response 
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from .models import CartItem,Cart
from .serializers import CartItemSerializer,CartSerializer
# Create your views here.

class CartRetrieveView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        cart , created =Cart.objects.get_or_create(user = self.request.user)
        return cart
    


class CartItemListView(generics.ListAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

class CartItemCreateView(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def perform_create(self, serializer):
        cart, _created = Cart.objects.get_or_create(user = self.request.user)
        product = serializer.validated_data.get("product")
        quantity = serializer.validated_data.get("quantity")
        
        cart_item , created = CartItem.objects.get_or_create(cart =cart , product = product)
        if not created :
            cart_item.quantity += quantity
            cart_item.save()
        else:
            serializer.save(cart=cart)

class CartItemUpdateView(generics.UpdateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        quantity = request.data.get('quantity',instance.quantity)
        partial_data = {'quantity':quantity}
        if int(quantity) == 0:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        serializer = self.get_serializer(instance , data = partial_data, partial = True)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)
        return Response({"msg":"cart item updated successfully","data":serializer.data})
    
class CartItemDeleteView(generics.DestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)
