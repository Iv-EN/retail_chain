from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import (
    MyTokenObtainPairSerializer,
    ResetPasswordConfirmSerializer,
    ResetPasswordSerializer,
    UserSerializer,
)


class UserViewSet(ModelViewSet):
    """Создаёт пользователя."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ResetPasswordAPIViews(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            try:
                user = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                user = None
            if user is not None:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                frontend_url = getattr(
                    settings,
                    "FRONTEND_PASSWORD_RESET_URL",
                    ""
                )
                if frontend_url:
                    reset_link = f'{frontend_url.rstrip("/")}/{uid}/{token}'
                else:
                    reset_link = f"/reset_password_confirm/{uid}/{token}"
                subject = "Reset your password"
                message = f"Ссылка для сброса пароля: {reset_link}"
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=True,
                )
            return Response(
                {
                    "detail": """
                    Если пользователь с таким адресом электронной почты
                    существует, на указанный адрес придёт ссылка
                    для сброса пароля.
                    """
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordConfirmAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        if serializer.is_valid():
            uidb64 = serializer.validated_data["uid"]
            token = serializer.validated_data["token"]
            new_password = serializer.validated_data["new_password"]
            user = get_user_model()
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
            except Exception:
                user = None
            if user is None:
                return Response(
                    {"detail": "Invalid link."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not default_token_generator.check_token(user, token):
                return Response(
                    {"detail": "Invalid or expired token."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.set_password(new_password)
            user.save()
            return Response(
                {"detail": "Пароль успешно изменён."},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
