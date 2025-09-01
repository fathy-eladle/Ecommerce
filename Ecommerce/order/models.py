from django.db import models
from django.core.validators import MinValueValidator
from accounts.models import User
from product.models import Product

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='unpaid')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_address = models.TextField()
    phone = models.CharField(max_length=15)
    tracking_number = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

    @property
    def total_items(self):
        """Return total number of items in order"""
        return sum(item.quantity for item in self.items.all())

    @property
    def can_cancel(self):
        """Check if order can be cancelled"""
        return self.status == 'pending'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ['order', 'product']

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def total_price(self):
        """Calculate total price for this item"""
        return self.quantity * self.price

    def clean(self):
        """Validate order item"""
        from django.core.exceptions import ValidationError
        if self.quantity > self.product.stock:
            raise ValidationError(f"Not enough stock. Only {self.product.stock} available.")