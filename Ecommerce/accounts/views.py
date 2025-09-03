
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView,UpdateAPIView
from .serializers import (RegisterSerializer, ChangePasswordSerializer,LogoutSerializer
                          ,UpdateProfileSerializer,
                          CustomTokenObtainPairSerializer,VerifyAccountSerializer
                          ,ResendCodeSerializer,ResetPasswordRequestSerializer,ResetPasswordConfirmSerializer,CheckUserStatusSerializer
                          ,ResendPasswordCodeSerializer)
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
        serializer = VerifyAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'msg': 'account is verified successfully'}, status=status.HTTP_200_OK)

class ResendCodeView(APIView):
    permission_classes = []
    def post(self, request):
        serializer = ResendCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'msg': 'Verification code resent'}, status=status.HTTP_200_OK)


        

class ResetPasswordRequestView(APIView):
    permission_classes = []
    def post(self, request):
        serializer = ResetPasswordRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'msg': 'code sent successfully'}, status=status.HTTP_200_OK)

class CheckUserStatus(APIView):
    permission_classes = []

    def post(self, request):
        serializer = CheckUserStatusSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


class ResetPasswordConfirmView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'msg': 'password updated successfully'}, status=status.HTTP_200_OK)


class ResendPasswordCodeView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = ResendPasswordCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'msg': 'code is resent'}, status=status.HTTP_200_OK)

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
    
    