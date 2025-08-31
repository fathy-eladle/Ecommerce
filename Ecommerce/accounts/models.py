from django.db import models
import random
# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    username = models.CharField(max_length=50,blank=False, null=False, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=11, blank=True, null=True)
    image = models.ImageField(upload_to='users/', null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    verification_code_created_at = models.DateTimeField(blank=True,null=True)
    reset_password_code = models.CharField(max_length=6, blank=True, null=True)
    reset_password_created_at = models.DateTimeField(blank=True, null=True)
    
    def generate_verification_code(self):
        code = f"{random.randint(100000,999999)}"
        self.verification_code=code
        self.verification_code_created_at = timezone.now()
        self.save()
        return code
    
    def generate_reset_password_code(self):
        code = f"{random.randint(100000,999999)}"
        self.reset_password_code = code
        self.reset_password_created_at = timezone.now()
        self.save()
        return code
        
        
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['last_name', 'first_name', 'username']
    
    def __str__(self):
        return self.email  