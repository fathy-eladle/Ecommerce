from django.db import models
from django.conf import settings
from order.models import Order

class PaymentTransaction(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payment_transactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    paymob_order_id = models.CharField(max_length=100, null=True, blank=True)
    paymob_payment_id = models.CharField(max_length=100, null=True, blank=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    payment_token = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    error_message = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.id} for Order {self.order.id}"
