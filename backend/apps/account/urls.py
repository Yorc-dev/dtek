from django.urls import path

from .views import LoginView, LogOutView, RefreshView, UserGetMeView, ResetPasswordView, PasswordResetConfirmView, UserListAPIView
from rest_framework_simplejwt.views import TokenBlacklistView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('refresh-token/', RefreshView.as_view(), name='refresh-token'),
    path('logout/', LogOutView.as_view(), name='logout'),
    path('get-me/', UserGetMeView.as_view()),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('reset-password-confirm/с', PasswordResetConfirmView.as_view(), name='reset-password-confirm'),
    path('staffs/', UserListAPIView.as_view(), name='staffs')
]