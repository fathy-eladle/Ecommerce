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
from django.utils import timezone
from datetime import timedelta
from accounts.utils.email_utils import send_reset_password_code

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
        if username.lower() == password.lower():
            raise serializers.ValidationError('Password can\'t be same as username.') 
        
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

class VerifyAccountSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        code = attrs.get('code')

        try:
            user = User.objects.get(email=email, verification_code=code)
        except User.DoesNotExist:
            raise serializers.ValidationError("invalid code or email")

        if user.verification_code_created_at:
            now = timezone.now()
            if now - user.verification_code_created_at > timedelta(minutes=5):
                raise serializers.ValidationError("verification code is expired")

        attrs['user'] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data['user']
        user.is_active = True
        user.verification_code = None
        user.verification_code_created_at = None
        user.save()
        return user
class ResendCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get('email')
        try:
            user = User.objects.get(email=email, is_active=False)
        except User.DoesNotExist:
            raise serializers.ValidationError("user not registered or already active")

        if timezone.now() - user.verification_code_created_at < timedelta(seconds=60):
            raise serializers.ValidationError("Please wait before requesting another code.")

        attrs['user'] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data['user']
        user.verification_code = user.generate_verification_code()
        user.save()
        send_verification_email(user)
        return user

class CheckUserStatusSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"status": "not_registered"})
        attrs["user"] = user
        return attrs

    def to_representation(self, instance):
        user = self.validated_data["user"]
        if not user.is_active:
            return {"status": "pending_verification"}
        return {"status": "verified"}

class ResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("this email is not registered")
        attrs['user'] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data['user']
        user.reset_password_code = user.generate_reset_password_code()
        user.save()
        send_reset_password_code(user)
        return user

class ResetPasswordConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        email = attrs.get("email")
        code = attrs.get("code")
        new_password = attrs.get("new_password")

        try:
            user = User.objects.get(email=email, reset_password_code=code)
        except User.DoesNotExist:
            raise serializers.ValidationError("invalid code or email")

        if user.reset_password_created_at:
            now = timezone.now()
            if now - user.reset_password_created_at > timedelta(minutes=5):
                raise serializers.ValidationError("expired code, try resend code again")

        attrs["user"] = user
        attrs["new_password"] = new_password
        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        new_password = self.validated_data["new_password"]
        user.set_password(new_password)
        user.reset_password_code = None
        user.reset_password_created_at = None
        user.save()
        return user

class ResendPasswordCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("this email is not registered")

        if timezone.now() - user.reset_password_created_at < timedelta(seconds=60):
            raise serializers.ValidationError("Please wait before requesting another code.")

        attrs["user"] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        user.reset_password_code = user.generate_reset_password_code()
        user.save()
        send_reset_password_code(user)
        return user


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
            