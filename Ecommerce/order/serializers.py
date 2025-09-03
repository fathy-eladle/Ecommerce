from rest_framework import serializers
from django.db import transaction
from .models import Order, OrderItem
from cart.models import Cart

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price', 'total_price']
        read_only_fields = ['price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    cart_id = serializers.IntegerField(write_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'status', 'status_display', 
            'payment_status', 'payment_status_display',
            'total_amount', 'shipping_address', 'phone',
            'tracking_number', 'notes', 'items', 
            'cart_id', 'created_at', 'total_items'
        ]
        read_only_fields = ['status', 'payment_status', 'total_amount', 'tracking_number']

    def validate_cart_id(self, value):
        try:
            cart = Cart.objects.get(id=value, user=self.context['request'].user)
            if not cart.items.exists():
                raise serializers.ValidationError("Cart is empty")
            return value
        except Cart.DoesNotExist:
            raise serializers.ValidationError("Cart not found")

    def validate_phone(self, value):
        if not value.isdigit() or len(value) < 11:
            raise serializers.ValidationError("Invalid phone number")
        return value

    def validate_shipping_address(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Shipping address must be detailed")
        return value

    @transaction.atomic
    def create(self, validated_data):
        cart_id = validated_data.pop('cart_id')
        cart = Cart.objects.get(id=cart_id)
        user = self.context['request'].user

        order = Order.objects.create(
            user=user,
            **validated_data
        )

        total_amount = 0
        for cart_item in cart.items.all():
            # if not cart_item.product.stock:
            #  raise serializers.ValidationError(f"{cart_item.product.name} is out of stock")
            if cart_item.quantity > cart_item.product.stock:
                raise serializers.ValidationError(
                    f"Product {cart_item.product.name} is out of stock"
                )
            
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            
            product = cart_item.product
            product.stock -= cart_item.quantity
            product.save()
            
            total_amount += cart_item.quantity * cart_item.product.price

        order.total_amount = total_amount
        order.save()
        cart.items.all().delete()

        return order
    
    
    