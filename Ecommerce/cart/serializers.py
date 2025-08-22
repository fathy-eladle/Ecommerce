from rest_framework import serializers
from .models import Cart,CartItem
from product.serializer import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only = True)
    product_id = serializers.PrimaryKeyRelatedField(source ="product", write_only = True, queryset= CartItem.objects.all())
    
    class Meta:
        model = Cart
        fields = ['product_id' , 'product', 'quantity', 'total_price', 'id']
        read_only_fields = ['total_price']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True,read_only = True)
    total_price = serializers.DecimalField(max_digits=10 , decimal_places=2 ,read_only = True)
    
    class Meta:
        model = Cart
        fields = ['id','user','created_at','update_at','items', 'total_price']
        read_only_fields = ['user', 'total_price', 'created_at', 'updated_at']
        
    
    