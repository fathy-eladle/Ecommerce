from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseForbidden
from .models import PaymentTransaction,Order
from .serializers import PaymentTransactionSerializer
import hmac
import hashlib
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import get_object_or_404

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initialize_payment(request):
    """Initialize payment for an order using serializer"""
    serializer = PaymentTransactionSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        transaction = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response({
        'status': 'error',
        'message': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def payment_callback(request):
    """Callback endpoint for Paymob to notify about payment status"""
    data = request.POST or request.GET

    try:
        hmac_fields = [
            'amount_cents', 'created_at', 'currency', 'error_occured',
            'has_parent_transaction', 'id', 'integration_id', 'is_3d_secure',
            'is_auth', 'is_capture', 'is_refunded', 'is_standalone_payment',
            'is_voided', 'order', 'owner', 'pending',
            'source_data.pan', 'source_data.sub_type', 'source_data.type',
            'success'
        ]

        hmac_string = ''.join(str(data.get(field, '')) for field in hmac_fields)

        # Calculate HMAC
        secret = settings.PAYMOB_HMAC.encode('utf-8')
        calculated_hmac = hmac.new(
            secret,
            hmac_string.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()

        # Verify HMAC
        received_hmac = data.get('hmac')
        if not hmac.compare_digest(calculated_hmac, received_hmac):
            print("Received HMAC:", received_hmac)
            print("Calculated HMAC:", calculated_hmac)
            print("Data used for HMAC:", hmac_string)
            return HttpResponseForbidden("Invalid HMAC")

        # Process the payment
        order_id = data.get('merchant_order_id', '').split('_')[0]
        order = get_object_or_404(Order, id=int(order_id))
        transaction = PaymentTransaction.objects.filter(order=order).latest('created_at')
        
        if data.get('success') == 'true':
            transaction.status = 'success'
            transaction.payment_method = data.get('source_data.type', '')
            transaction.transaction_id = data.get('id', '')
            transaction.paymob_order_id = data.get('order', '')
        

            # Update order status
            transaction.order.payment_status = 'paid'
            transaction.order.save()

            # Save amount paid
            amount_cents = int(data.get('amount_cents', 0))
            transaction.amount_paid = amount_cents / 100
            status_message = "success"
        else:
            transaction.status = 'failed'
            transaction.error_message = data.get('error_occured', 'Payment failed')
            status_message = "failed"

        transaction.save()

        return HttpResponse("ok", status=200)

    except Exception as e:
        return HttpResponse(f"error: {str(e)}", status=400)


@api_view(['GET'])
@permission_classes([AllowAny])
def payment_status(request):
    """Frontend polls this to get final payment status"""
    order_id = request.query_params.get('order_id')
    if not order_id:
        return Response({"error": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    order = get_object_or_404(Order, id=order_id)
    transaction = PaymentTransaction.objects.filter(order=order).latest('created_at')

    return Response({
        "order_id": order.id,
        "status": transaction.status,
        "amount": transaction.amount_paid if transaction.status == 'success' else 0,
        "message": "Payment completed successfully" if transaction.status == 'success' else transaction.error_message
    })
