from django.urls import include, path
from rest_framework_nested import routers

from .apps import NetworkConfig
from .views import NetworkObjectViewSet

app_name = NetworkConfig.name

router = routers.DefaultRouter()
router.register(
    r"network_objects", NetworkObjectViewSet, basename="network_objects"
)

urlpatterns = [
    path("api/", include(router.urls)),
]
