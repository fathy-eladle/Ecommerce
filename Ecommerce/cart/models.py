from django.db import models
from accounts.models import User
from product.models import Product
from django.utils import timezone
# Create your models here.
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return f"cart for {self.user.username}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

class CartItem (models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name='items')
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='item')
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ['cart', 'product']
    
    @property
    def total_price(self):
        return self.quantity * self.product.price
        
    