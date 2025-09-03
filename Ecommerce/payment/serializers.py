from rest_framework import serializers
from .models import PaymentTransaction
from .paymob import PaymobClient
from order.models import Order
from django.conf import settings
import time

class PaymentTransactionSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(write_only=True)
    payment_method = serializers.CharField(write_only=True)
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    phone_number = serializers.CharField(write_only=True)
    street = serializers.CharField(write_only=True)
    city = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'order', 'amount', 'status', 'payment_method',
            'created_at', 'updated_at', 'error_message', 'order_id',
            'first_name', 'last_name', 'phone_number', 'street', 'city'
        ]
        read_only_fields = [
            'status', 'paymob_order_id', 'paymob_payment_id',
            'transaction_id', 'payment_token', 'created_at',
            'updated_at', 'error_message', 'order', 'amount'
        ]
    
    def validate_order_id(self, value):
        """Validate that order exists and belongs to user"""
        user = self.context['request'].user
        try:
            order = Order.objects.get(id=value, user=user)
            return value
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found or doesn't belong to you")
    
    def validate_payment_method(self, value):
        """Validate payment method"""
        integration_ids = {
            "card": settings.PAYMOB_CARD_INTEGRATION_ID,
            "wallet": settings.PAYMOB_WALLET_INTEGRATION_ID,
        }
        
        if value not in integration_ids:
            raise serializers.ValidationError("Invalid payment method selected")
        return value
    
    def create(self, validated_data):
        """Create payment transaction and initialize payment"""
        request = self.context['request']
        user = request.user
        
        # Extract order data
        order_id = validated_data.pop('order_id')
        payment_method = validated_data.pop('payment_method')
        first_name = validated_data.pop('first_name', user.first_name or user.username)
        last_name = validated_data.pop('last_name', user.last_name or user.username)
        phone_number = validated_data.pop('phone_number')
        street = validated_data.pop('street')
        city = validated_data.pop('city', 'NA')
        
        
        # Get order
        order = Order.objects.get(id=order_id, user=user)
        
        # Create payment transaction
        transaction = PaymentTransaction.objects.create(
            order=order,
            user=user,
            amount=order.total_amount,
            status='pending',
            **validated_data
        )
        
        try:
            # Prepare billing info
            billing_info = {
                'first_name': first_name,
                'last_name': last_name,
                'phone_number': phone_number,
                'street': street,
                'city': city
            }
            
            # Initialize payment
            integration_ids = {
                "card": settings.PAYMOB_CARD_INTEGRATION_ID,
                "wallet": settings.PAYMOB_WALLET_INTEGRATION_ID,
            }
            
            paymob_client = PaymobClient()
            redirect_url = paymob_client.checkout(
                total_price=order.total_amount,
                integration_id=integration_ids[payment_method],
                order_id=order.id,
                user=user,
                billing_info=billing_info
            )
            
            # Store redirect URL in instance for response
            transaction._redirect_url = redirect_url
            return transaction
            
        except Exception as e:
            transaction.status = 'failed'
            transaction.error_message = str(e)
            transaction.save()
            raise serializers.ValidationError(str(e))
    
    def to_representation(self, instance):
        """Add redirect URL to response if available"""
        representation = super().to_representation(instance)
        
        # Add redirect URL if payment was initialized successfully
        if hasattr(instance, '_redirect_url'):
            representation['redirect_url'] = instance._redirect_url
        
        return representation