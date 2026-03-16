from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import permissions, generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter

from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
# from axes.decorators import axes_dispatch

from core.tasks import send_reset_password_email_task
from .models import UserResetPasswordToken
from .serializers import LogOutSerializer, UserSerializer, ResetPasswordSerializer, ResetPasswordConfirmSerializer
# from integration.gns import get_data_from_gns
# from integration.minust import get_data_from_minust


User = get_user_model()


@extend_schema(
    tags=["Account"],
    description="Авторизация пользователя и получение JWT-токенов.",
    request=None,
    responses={200: "JWT токены"},
)
# @method_decorator(axes_dispatch, name='dispatch')
class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]


@extend_schema(
    tags=["Account"],
    description="Обновление JWT-токена.",
    request=None,
    responses={200: "Обновленный JWT токен"},
)
class RefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]


@extend_schema(
    tags=["Account"],
    description="Выход из системы и добавление refresh-токена в черный список.",
    request=LogOutSerializer,
    responses={
        200: "Successfully logged out",
        400: "Token expired or invalid"
    },
)
class LogOutView(APIView):
    serializer_class = LogOutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data['refresh_token']
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response('Successfully logged out')
        except Exception:
            return Response({'msg': 'Token expired or invalid'}, status=400)


@extend_schema(
    tags=["Account"],
    description="Получение информации о текущем пользователе.",
    responses={200: UserSerializer}
)
class UserGetMeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


@extend_schema(
    tags=["Account"],
    description="Запрос на сброс пароля (отправляет письмо с инструкцией).",
    request=ResetPasswordSerializer,
    responses={
        200: "Вам на почту отправлено письмо с инструкцией по сбросу пароля",
        404: "User not found",
    },
    examples=[
        OpenApiExample(
            "Пример запроса",
            summary="Запрос на сброс пароля",
            value={"email": "user@example.com"},
            request_only=True,
        ),
        OpenApiExample(
            "Пример ответа",
            summary="Успешный запрос",
            value={"msg": "Вам на почту отправлено письмо с инструкцией по сбросу пароля"},
            response_only=True,
        ),
    ]
)
class ResetPasswordView(APIView):
    serializer_class = ResetPasswordSerializer
    throttle_scope = 'forgot_password'

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'msg': 'User not found'}, status=404)

        token = UserResetPasswordToken.objects.create(user=user)
        send_reset_password_email_task.delay(email=email, reset_token=token.reset_token)
        return Response({'msg': 'Вам на почту отправлено письмо с инструкцией по сбросу пароля'})


@extend_schema(
    tags=["Account"],
    description="Подтверждение сброса пароля с использованием токена.",
    request=ResetPasswordConfirmSerializer,
    responses={
        200: "Ваш пароль изменен!",
        400: "Ваш код недействителен или истек",
    },
    parameters=[
        OpenApiParameter(name="token", description="Токен сброса пароля", required=True, type=str)
    ],
    examples=[
        OpenApiExample(
            "Пример запроса",
            summary="Подтверждение сброса пароля",
            value={"new_password": "NewSecurePassword123"},
            request_only=True,
        ),
        OpenApiExample(
            "Пример ответа",
            summary="Успешный сброс пароля",
            value={"msg": "Ваш пароль изменен!"},
            response_only=True,
        ),
    ]
)
class PasswordResetConfirmView(APIView):
    serializer_class = ResetPasswordConfirmSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        reset_token = request.query_params.get('token')
        new_password = request.data.get('new_password')

        try:
            reset_token = UserResetPasswordToken.objects.get(reset_token=reset_token)
        except UserResetPasswordToken.DoesNotExist:
            return Response({'msg': 'Ваш код недействителен'}, status=400)

        if not reset_token.is_valid():
            return Response({'msg': 'Срок действия вашего кода истек'}, status=400)

        user = reset_token.user
        user.set_password(new_password)
        user.save()
        reset_token.delete()
        return Response({'msg': "Ваш пароль изменен!"}, status=200)


class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# @api_view(['GET'])
# def gns_view(request):
#     inn = request.user.inn
#     # inn = request.query_params.get('inn')
#     data = get_data_from_gns(inn)
#     return Response(data)


# @api_view(['GET'])
# def minust_view(request):
#     inn = request.user.inn
#     # inn = request.query_params.get('inn')
#     data = get_data_from_minust(inn)
#     return Response(data)