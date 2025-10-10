from django.urls import include, path
from rest_framework.permissions import AllowAny
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .apps import UsersConfig
from .views import (MyTokenObtainPairView, ResetPasswordAPIViews,
                    ResetPasswordConfirmAPIView, UserViewSet)

app_name = UsersConfig.name

router = SimpleRouter()
router.register("", UserViewSet, basename="users")

urlpatterns = [
    path(
        "token/",
        MyTokenObtainPairView.as_view(permission_classes=(AllowAny,)),
        name="token_obtain_pair",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(permission_classes=(AllowAny,)),
        name="token_refresh",
    ),
    path(
        "reset_password/",
        ResetPasswordAPIViews.as_view(),
        name="reset_password",
    ),
    path(
        "reset_password_confirm/",
        ResetPasswordConfirmAPIView.as_view(),
        name="reset_password_confirm",
    ),
    path("", include(router.urls)),
]
