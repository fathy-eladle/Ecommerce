
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView,UpdateAPIView
from .serializers import (RegisterSerializer, ChangePasswordSerializer,LogoutSerializer
                          ,UpdateProfileSerializer,
                          CustomTokenObtainPairSerializer)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from shared.common import ResponseGlobal

from rest_framework import status
from .models import User
from accounts.utils.email_utils import send_verification_email,send_reset_password_code
from django.utils import timezone
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema

class RegisterView(APIView):    
    permission_classes = []
    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(slef, request):
        serializer =  RegisterSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            response = ResponseGlobal(
                success=True,
                message="user created ",
                error=""
            )
            return Response(response.to_dict(),status=status.HTTP_200_OK)
        return Response(ResponseGlobal(success= False,
                              message="Registration failed",
                              error=serializer.errors).to_dict(),status=status.HTTP_400_BAD_REQUEST)
    
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    

class VerifyAccountView(APIView):
    permission_classes = []
    @swagger_auto_schema()

    def post(self, request):
        email = request.data.get('email') 
        code =request.data.get('code')
         
        try: 
            user = User.objects.get(email= email, verification_code= code)
            
            if user.verification_code_created_at:
                now= timezone.now()
                if now-user.verification_code_created_at > timedelta(minutes=5):
                    return Response({'msg':'verification code is expired'},status=status.HTTP_400_BAD_REQUEST)
             
            user.is_active = True
            user.verification_code = None
            user.verification_code_created_at = None
            user.save()
            return Response({'msg':'account is verified successfully'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'msg':'invalid code or email'}, status=status.HTTP_400_BAD_REQUEST)
              
class ResendCodeView(APIView):
    
    permission_classes = []
    
    def post(self,request):
        email = request.data.get('email') 
        if not email:
            return Response({'msg': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email,is_active=False)
            if timezone.now() - user.verification_code_created_at < timedelta(seconds=60):
                return Response({'msg': 'Please wait before requesting another code.'}, status=status.HTTP_400_BAD_REQUEST)
            user.verification_code = user.generate_verification_code()
            user.save()
            send_verification_email(user)
            return Response({'msg':'Verification code resent'},status=status.HTTP_200_OK)            
        except User.DoesNotExist:
            return Response({'msg':'user not registered or alredy active'},status=status.HTTP_400_BAD_REQUEST)


class CheckUserStatus(APIView):
    permission_classes = []
    
    def post(self,request):
        email = request.data.get('email')
        if not email:
            return Response({'mag':'email is required'},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                return Response({'status': 'pending_verification'},status=status.HTTP_200_OK)
            else:
                return Response({'status': 'verified'},status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'status': 'not_registered'},status=status.HTTP_404_NOT_FOUND)  
        

class ResetPasswordRequestView(APIView):
    permission_classes = []
    @swagger_auto_schema()

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'msg':'email is required'},status=status.HTTP_404_NOT_FOUND)
        
        try:        
            user = User.objects.get(email=email)
            user.reset_password_code = user.generate_reset_password_code()
            user.save()
            send_reset_password_code(user)
            return Response({'msg':'code sent successfylly'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'msg':'this email is not registered'}, status=status.HTTP_400_BAD_REQUEST)
            
class ResetPasswordConfirmView(APIView):
    permission_classes = []
    
    def post(self,request):
        email = request.data.get('email')
        code = request.data.get('code')
        new_password = request.data.get('new_password')
        
        try:
            user = User.objects.get(email=email,reset_password_code=code)
           
            if user.reset_password_created_at:
               now = timezone.now()
               if now-user.reset_password_created_at> timedelta(minutes=5):
                   return Response({'msg':'expired code  try resend code again'},status=status.HTTP_400_BAD_REQUEST)
               user.set_password(new_password)
               user.reset_password_code = None
               user.reset_password_created_at = None
               user.save()
               return Response({'msg':'password updated successfully'},status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'msg':'invalid code or email'},status=status.HTTP_404_NOT_FOUND)                   


class ResendPasswordCodeView(APIView):
    permission_classes=[]
    
    def post(self,request):
        email = request.data.get('email')
        if not email:
            return Response({'mmsg':'email is required'},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            if timezone.now() - user.reset_password_created_at < timedelta(seconds=60):
                return Response({'msg': 'Please wait before requesting another code.'}, status=status.HTTP_400_BAD_REQUEST)
            user.reset_password_code=user.generate_reset_password_code()
            user.save()
            send_reset_password_code(user)
            
            return Response({'msg':'code is resend '},status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'msg':'this email is not registeerd'},status=status.HTTP_404_NOT_FOUND)
        

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request):
        try:
            serializer = ChangePasswordSerializer(instance=request.user,data =request.data ,context={'request':request})
            serializer.is_valid(raise_exception=True)
            serializer.save()   
            return Response(
                {'msg':'the password is updated successfully'},
                status=status.HTTP_200_OK
                )
        except Exception as e:
            return Response(
                {
                'status':'error',
                'message':'error happened',
                'details':str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        serializer = LogoutSerializer(data =request.data)
        try:  
            serializer.is_valid(raise_exception=True)
            serializer.save() 
            return Response({'msg':' successfully logged out'})
        except Exception as e:
            return Response({'msg':str(e)})
                
        
class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self,request):
        serializer = UpdateProfileSerializer(instance = request.user , data = request.data, partial =True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response (serializer.errors,status=status.HTTP_400_BAD_REQUEST)   
    
    