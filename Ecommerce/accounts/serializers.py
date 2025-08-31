from pathlib import __all__
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken,TokenError
from accounts.models import User
from django.db import transaction
from accounts.utils.email_utils import send_verification_email
import re
from shared.common import ResponseGlobal 
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


from rest_framework.exceptions import AuthenticationFailed
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'password', 'username', 'phone', 'first_name','last_name']
        
    def validate_password(self, value):
        if not re.search(r'[a-z]',value):
            raise serializers.ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'[A-Z]',value):
            raise serializers.ValidationError('Password must contain at least one Cpitalcase letter.')
        if not re.search(r'\d',value):
            raise serializers.ValidationError('Password must contain at least one number.')
        if not re.search(r'[!@#$%?*&]',value):
            raise serializers.ValidationError('Password must contain at least one special Character.')
        
        return value
        
        
    def validate(self, data):   
        password = data.get('password')
        username = data.get('username')
        if username.lower() in password.lower():
            raise serializers.ValidationError('Password cant contain username.') 
        
        return data   
    
       
    def create(self, validated_data):
        with transaction.atomic():
            password = validated_data.pop('password')
            user = User(**validated_data)
            user.set_password(password)
            user.save()
            user.generate_verification_code()
            print(user.verification_code)
    
            send_verification_email(user)
            
        return user        


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        try:
            data = super().validate(attrs)

            response = ResponseGlobal(
                success=True,
                message="login_success",
                error="",
                data={
                    "access": data["access"],
                    "refresh": data["refresh"],
                }
            )
            return response.to_dict()

        except AuthenticationFailed as e:

            response = ResponseGlobal(
                success=False,
                message="login_failed",
                error=str(e.detail),
                data={}
            )
            return response.to_dict()

class ChangePasswordSerializer(serializers.ModelSerializer):
    
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    
    class Meta():
        model =  User
        fields = ['old_password','new_password','confirm_password']
        
    def validate(self, data):
        user = self.context['request'].user
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError('the new password is not same')
        if user.username in data['new_password']:
            raise serializers.ValidationError('password must not contain username ')
        return data
    
    def validate_old_password(self,value):
        user = self.context.get('request').user 
        if not user.check_password(value):
            raise serializers.ValidationError('the old password is not correct')
        return value
    
    def validate_new_password(self,value):
        if not re.search(r'[a-z]',value):
            raise serializers.ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'[A-Z]',value):
            raise serializers.ValidationError('Password must contain at least one Cpitalcase letter.')
        if not re.search(r'\d',value):
            raise serializers.ValidationError('Password must contain at least one number.')
        if not re.search(r'[!@#$%?*&]',value):
            raise serializers.ValidationError('Password must contain at least one special Character.')
        return value
        
        
    def update(self, instance, validated_data):
        new_password = validated_data['new_password'] 
        instance.set_password(new_password)
        instance.save()        
        return instance
  
  
    
class LogoutSerializer(serializers.Serializer):
    refresh =  serializers.CharField()
    
    def validate(self, attrs):
        self.token = attrs['refresh']        
        return attrs
          
    def save(self, **kwargs):
        try:
            refresh_token = RefreshToken(self.token)
            refresh_token.blacklist()
        except TokenError:
            self.fail('bad_token ') 
    

class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name','last_name','phone','email','image','address','city']
           
        def validate_image(self,value):
            max_size = 2 * 1024 * 1024  # 2MB

            if value.size > max_size:
                raise serializers.ValidationError("Image size must not exceed 2MB.")

            valid_extensions = ['jpg', 'jpeg', 'png']
            if not value.name.split('.')[-1].lower() in valid_extensions:
                raise serializers.ValidationError("Unsupported image format. Allowed formats: jpg, jpeg, png.")
            return value
            