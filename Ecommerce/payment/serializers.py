from rest_framework import serializers
from .models import PaymentTransaction

class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'order', 'amount', 'status', 'payment_method',
            'created_at', 'updated_at', 'error_message'
        ]
        read_only_fields = [
            'status', 'paymob_order_id', 'paymob_payment_id',
            'transaction_id', 'payment_token', 'created_at',
            'updated_at', 'error_message'
        ]
