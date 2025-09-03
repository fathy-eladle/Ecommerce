from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    

class Product(models.Model):
    name = models.CharField(max_length=150,db_index=True)
    description = models.TextField(null=True,blank=True)
    price = models.DecimalField(max_digits=10 ,decimal_places=2)
    image = models.ImageField(upload_to='products/' , null=True ,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name='products')
    stock = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
        