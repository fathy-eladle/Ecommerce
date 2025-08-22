from django.urls import path
from .views import RegisterView, VerifyAccountView,ResendCodeView,CheckUserStatus,ResetPasswordRequestView,ResetPasswordConfirmView,ResendPasswordCodeView,ChangePasswordView,LogoutView,UpdateProfileView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
urlpatterns = [
    path('register/',RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(),name='login'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    path('verify/', VerifyAccountView.as_view(),name='verify'),
    path('resend-verify_code/',ResendCodeView.as_view(), name='resend_verify_code'),
    path('reset-password/request/',ResetPasswordRequestView.as_view(),name='reset_password_request'),
    path('reset-password/confirm/',ResetPasswordConfirmView.as_view(),name='reset_password_confirm'),
    path('resend-password_code/',ResendPasswordCodeView.as_view(),name='resend_password_code'),
    path('change-password/',ChangePasswordView.as_view(),name='change_password'),
    path('update-profile/',UpdateProfileView.as_view(),name='update_profile'),
    path('check-status/',CheckUserStatus.as_view(),name='check-status'),
    
]
