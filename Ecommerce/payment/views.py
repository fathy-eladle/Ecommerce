from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from order.models import Order
from .models import PaymentTransaction
from .paymob import PaymobClient
from .serializers import PaymentTransactionSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initialize_payment(request):
    """Initialize payment for an order"""
    order_id = request.data.get('order_id')
    payment_method = request.data.get('payment_method')
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Create payment transaction
    transaction = PaymentTransaction.objects.create(
        order=order,
        user=request.user,
        amount=order.total_amount,
        status='pending'
    )
    
    try:
        # Get integration IDs from settings
        integration_ids = {
            "card": settings.PAYMOB_CARD_INTEGRATION_ID,
            "wallet": settings.PAYMOB_WALLET_INTEGRATION_ID,
        }
        
        if payment_method not in integration_ids:
            raise ValueError("Invalid payment method selected")
            
        return PaymobClient().checkout(
            total_price=order.total_amount,
            integration_id=integration_ids[payment_method],
            order_id=order.id
        )
        
    except Exception as e:
        transaction.status = 'failed'
        transaction.error_message = str(e)
        transaction.save()
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def payment_callback(request):
    """Callback endpoint for Paymob to notify about payment status"""
    data = request.POST or request.GET
    
    try:
        order_id = data.get('merchant_order_id', '').split('_')[0]
        order = get_object_or_404(Order, id=int(order_id))
        transaction = PaymentTransaction.objects.filter(order=order).latest('created_at')
        
        if data.get('success') == 'true':
            transaction.status = 'success'
            transaction.order.payment_status = 'paid'
            transaction.order.save()
            status_message = "success"
        else:
            transaction.status = 'failed'
            transaction.error_message = "Payment failed"
            status_message = "failed"
            
        transaction.save()
        
        # You can create a payment status template or return JSON response
        return Response({'status': status_message})
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
