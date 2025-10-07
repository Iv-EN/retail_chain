from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import NetworkObject
from .serializers import NetworkObjectSerializer


class NetworkObjectViewSet(viewsets.ModelViewSet):
    queryset = NetworkObject.objects.all()
    serializer_class = NetworkObjectSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['country']
    ordering_fields = ['name', 'country']