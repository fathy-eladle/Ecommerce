from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User
from product.models import Product

class Review(models.Model):
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.username}'s review for {self.product.name}"
